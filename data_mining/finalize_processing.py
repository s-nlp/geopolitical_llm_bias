from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime
from typing import Iterable, List, Optional

from concurrent.futures import ThreadPoolExecutor
import re

import instructor
from exa_py import Exa
from openai import OpenAI
from pydantic import BaseModel, Field, HttpUrl
from tqdm.auto import tqdm

from utils import (
    EventSeed,
    DEFAULT_LANGS,
    build_llm_client,
    build_exa_client,
    OPENAI_MODEL,
    load_seeds_and_metadata,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EventExtracted(BaseModel):
    url: HttpUrl
    name: str
    years: str = Field(..., description="Year or year range, e.g., '1939-1945'")
    short_description: str = Field(..., description="Concise factual description (<=80 words)")
    paragraph_anchor_or_comment: str = Field(
        ..., description="A section/paragraph anchor like '#Background' or a short locator comment."
    )


class LanguagePerspective(BaseModel):
    language: str
    url: Optional[HttpUrl] = None
    key_points: List[str] = Field(
        default_factory=list,
        description="3-5 brief points capturing emphasis/stance in that language article",
    )


class DebiasedEventSummary(BaseModel):
    neutral_description_50_words_max: str = Field(
        ..., description="<= 50 words neutral summary"
    )
    bias_comment: str = Field(
        ..., description="Comment on potential biases and cross-language differences"
    )
    languages_used: List[str]
    perspectives: List[LanguagePerspective]


class DatasetEvent(BaseModel):
    seed: EventSeed
    extracted: EventExtracted
    debiased: DebiasedEventSummary


def _derive_anchor_from_text(text: str, event_name: str) -> str:
    heading = None
    for line in text.splitlines():
        if re.match(r"^=+ .* =+$", line.strip()) and event_name.lower()[:20] in line.lower():
            heading = line.strip(" =")
            break
    if heading:
        anchor = "#" + re.sub(r"[^A-Za-z0-9]+", "-", heading).strip("-")
        return anchor
    return "contextual paragraph (no explicit anchor)"


def extract_event_from_wiki(
    client: instructor.Instructor,
    exa: Exa,
    seed: EventSeed,
) -> EventExtracted:
    contents = exa.get_contents(urls=[str(seed.url)], text=True)
    page_text = ""
    if contents and getattr(contents, "results", None):
        page_text = contents.results[0].text or ""

    page_snippet = page_text[:64000] if page_text else ""

    system = (
        "Extract precise event metadata from Wikipedia text. If an article contains multiple events, pick the section/paragraph that describes the specific event referenced by the page itself."
    )
    user = (
        f"URL: {seed.url}\nEvent name: {seed.name}\n"
        "Return: years (e.g., '1939-1940' or '1962'), short factual description (<=80 words), and a paragraph anchor or short locator comment.\n\n"
        f"Content (truncated):\n{page_snippet}"
    )

    extracted: EventExtracted = client.chat.completions.create(  # type: ignore
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_model=EventExtracted,
        parallel_tool_calls=False,
    )
    if (
        extracted.paragraph_anchor_or_comment.startswith("contextual")
        or not extracted.paragraph_anchor_or_comment
    ) and page_text:
        extracted.paragraph_anchor_or_comment = _derive_anchor_from_text(
            page_text, seed.name
        )
    return extracted


def _candidate_lang_urls(base_url: str, langs: Iterable[str]) -> List[str]:
    m = re.match(r"https?://([a-z]+)\.wikipedia\.org(.*)", base_url)
    if not m:
        return []
    path = m.group(2)
    urls = [f"https://{lang}.wikipedia.org{path}" for lang in langs]
    return sorted(set(urls))


def _collect_lang_contents(exa: Exa, urls: List[str]) -> List[LanguagePerspective]:
    perspectives: List[LanguagePerspective] = []
    for u in urls:
        try:
            c = exa.get_contents(urls=[u], text=True)
            text = ""
            if c and getattr(c, "results", None):
                text = c.results[0].text or ""
            if not text:
                continue
            snippet = text[:64000]
            perspectives.append(
                LanguagePerspective(language=u.split(".")[0].split("//")[-1], url=u, key_points=[snippet])
            )
        except Exception:
            continue
    return perspectives


def debias_event(
    client: OpenAI,
    instructor_client: instructor.Instructor,
    exa: Exa,
    extracted: EventExtracted,
    compare_langs: Iterable[str],
) -> DebiasedEventSummary:
    lang_urls = _candidate_lang_urls(str(extracted.url), compare_langs)
    perspectives_raw = _collect_lang_contents(exa, lang_urls)

    if len(perspectives_raw) < 3:
        include_domains = [f"{lang}.wikipedia.org" for lang in compare_langs]
        r = exa.search(
            f"{extracted.name} {extracted.years} site:wikipedia.org",
            type="neural",
            use_autoprompt=True,
            num_results=10,
            include_domains=include_domains,
        )
        by_lang: dict[str, str] = {}
        for it in r.results:
            url = getattr(it, "url", "")
            m = re.match(r"https?://([a-z]+)\.wikipedia\.org/", url)
            if not m:
                continue
            lang = m.group(1)
            if lang not in by_lang:
                by_lang[lang] = url
        extra_persp = _collect_lang_contents(exa, list(by_lang.values()))
        have = {p.language for p in perspectives_raw}
        for p in extra_persp:
            if p.language not in have:
                perspectives_raw.append(p)
                have.add(p.language)

    lang_blurbs: List[LanguagePerspective] = []
    for p in perspectives_raw:
        text = p.key_points[0] if p.key_points else ""
        if not text:
            continue
        system = "Summarize the following Wikipedia text into 3-5 bullets that reflect emphasis/stance."
        msg = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": text}],
        )
        bullets = (msg.choices[0].message.content or "").strip()
        bullets_list = [b.strip("- •\n ") for b in bullets.splitlines() if b.strip()]
        lang_blurbs.append(LanguagePerspective(language=p.language, url=p.url, key_points=bullets_list[:5]))

    synthesis_context = []
    for lp in lang_blurbs:
        synthesis_context.append(
            f"Language: {lp.language}\nURL: {lp.url}\nPoints: "
            + "; ".join(lp.key_points[:10])
        )

    system = "Draft a neutral <=50-word description and a bias commentary based on differences across languages."
    user = (
        f"Event: {extracted.name} ({extracted.years})\n"
        f"Base URL: {extracted.url}\n\n"
        + "\n\n".join(synthesis_context)
    )

    debiased_event: DebiasedEventSummary = instructor_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        response_model=DebiasedEventSummary,
        parallel_tool_calls=False,
    )

    used = [lp.language for lp in lang_blurbs]
    debiased_event.languages_used = used
    debiased_event.perspectives = lang_blurbs
    return debiased_event


def finalize(
    unique_seeds_json: str,
    output_json: str,
    langs: Iterable[str] = DEFAULT_LANGS,
    workers: int = 8,
) -> List[DatasetEvent]:
    llm, instructor_llm = build_llm_client()
    exa = build_exa_client()

    seeds, metadata = load_seeds_and_metadata(unique_seeds_json)
    logger.info(f"Loaded {len(seeds)} unique seeds.")

    def _process(seed: EventSeed) -> Optional[DatasetEvent]:
        try:
            extracted: EventExtracted = extract_event_from_wiki(instructor_llm, exa, seed)
            debiased: DebiasedEventSummary = debias_event(llm, instructor_llm, exa, extracted, langs)
            return DatasetEvent(seed=seed, extracted=extracted, debiased=debiased)
        except Exception as e:
            logger.warning(f"Failed processing seed {seed.url}: {e}")
            return None

    dataset: List[DatasetEvent] = []
    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
        for item in tqdm(pool.map(_process, seeds), total=len(seeds), desc="Finalizing events"):
            if item is not None:
                dataset.append(item)

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    payload = {
        "llm": OPENAI_MODEL,
        "langs": list(langs),
        "datetime": datetime.now().isoformat(),
        "data": [d.model_dump(mode="json") for d in dataset],
    }
    for key, value in metadata.items():
        if key not in payload:
            payload[key] = value

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)

    logger.info(f"Saved final dataset with {len(dataset)} events to {output_json}")
    return dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize processing: extract and debias unique seeds")
    parser.add_argument("--input", type=str, required=True, help="Path to unique seeds JSON from clustering stage")
    parser.add_argument("--output", type=str, required=True, help="Path to write final dataset JSON")
    parser.add_argument(
        "--langs",
        type=str,
        default=",".join(DEFAULT_LANGS),
        help="Comma-separated list of Wikipedia languages to compare (e.g., en,fr,ru)",
    )
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel threads")
    args = parser.parse_args()

    langs = [s.strip() for s in args.langs.split(",") if s.strip()]
    finalize(unique_seeds_json=args.input, output_json=args.output, langs=langs, workers=args.workers)


if __name__ == "__main__":
    main()


