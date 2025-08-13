from __future__ import annotations

import argparse
import json
import os
import re
import logging
from datetime import datetime
from typing import Iterable, List, Optional

import instructor
from exa_py import Exa
from openai import OpenAI
from pydantic import BaseModel, Field, HttpUrl
from pathlib import Path

from utils import (
    DEFAULT_LANGS,
    OPENAI_MODEL,
    build_llm_client,
    build_exa_client,
    EventSeed,
    EXA_API_KEY,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if EXA_API_KEY is None:
    raise ValueError("EXA_API_KEY is not set")


class SearchQueries(BaseModel):
    queries: List[str] = Field(
        ..., description="Distinct, well-formed search queries (no site: filters)"
    )


# ===== Step 1: Discover events =====
def generate_search_queries(
    client: instructor.Instructor,
    country_a: str,
    country_b: str,
    start_year: int,
    end_year: int,
    search_langs: Iterable[str],
    max_queries: int,
) -> List[str]:
    system = (
        "Generate diverse, high-recall search queries to find Wikipedia pages about concrete historical conflicts between two countries within a year range."
        "\nIdentify the main topics within which you will need to find conflicts and prepare search queries for each of the topics."
        "\nTopics should be distinct and cover the all events and conflicts between the two countries."
        "\nThe queries should be diverse and cover the main topics."
        "\nThe queries should be concise and avoid quotes."
    )
    user = (
        f"Countries: {country_a} vs {country_b}. Years: {start_year}-{end_year}.\n"
        f"Wikipedia languages to consider: {', '.join(search_langs)}.\n"
        f"Return up to {max_queries} queries.\n"
        "Queries should be concise, avoid quotes, and MUST NOT include site: filters.\n"
        "Cover wars, crises, border clashes, incidents, disputes, skirmishes, standoffs, and named operations; include possible list/timeline pages."
    )
    try:
        resp: SearchQueries = client.chat.completions.create(  # type: ignore
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_model=SearchQueries,
        )
        queries = []
        for q in resp.queries:
            q = (q or "").strip()
            if not q:
                continue
            # Ensure no site: filters leak in
            q = re.sub(r"\bsite:[^\s]+", "", q).strip()
            if q and q not in queries:
                queries.append(q)
        return queries[:max_queries]
    except Exception:
        # Fallback set
        return [
            f"major conflicts between {country_a} and {country_b} {start_year}-{end_year}",
            f"{country_a} {country_b} war conflict incidents {start_year}..{end_year}",
            f"{country_a}-{country_b} dispute timeline {start_year} to {end_year}",
            f"list of {country_a} {country_b} conflicts",
        ]


def discover_events(
    client: instructor.Instructor,
    exa: Exa,
    country_a: str,
    country_b: str,
    start_year: int,
    end_year: int,
    max_events: int,
    search_langs: Iterable[str],
) -> List[EventSeed]:
    include_domains = [f"{lang}.wikipedia.org" for lang in search_langs] + ['wikipedia.org']

    queries = generate_search_queries(
        client=client,
        country_a=country_a,
        country_b=country_b,
        start_year=start_year,
        end_year=end_year,
        search_langs=search_langs,
        max_queries=max(4, max_events * 2),
    )
    logger.info(f"Generated {len(queries)} search queries:{'; '.join(queries)}")

    results = []
    for q in queries:
        r = exa.search(
            q,
            type="neural",
            use_autoprompt=True,
            num_results=min(20, max_events * 2),
            include_domains=include_domains,
        )
        # Each result has: id, title, url, score, ...
        results.extend(r.results)
    logger.info(f"Found {len(results)} results.")

    # Deduplicate by URL and keep top by score
    seen = {}
    for item in results:
        url = getattr(item, "url", None)
        score = getattr(item, "score", 0)
        if not url or not isinstance(url, str):
            continue
        if "wikipedia.org" not in url:
            continue
        if url not in seen:
            seen[url] = {"title": getattr(item, "title", ""), "score": score, "id": getattr(item, "id", None)}

    # Build seeds directly from unique URLs, keeping title as name
    ranked = sorted(seen.items(), key=lambda kv: kv[1]["score"], reverse=True)[: max_events]
    seeds: List[EventSeed] = []
    for url, meta in ranked:
        title = meta.get("title") or url.split("/")[-1].replace("_", " ")
        try:
            seeds.append(EventSeed(name=title, url=url))
        except Exception:
            continue
    logger.info(f"Returning {len(seeds)} seeds.")
    return seeds


def discover_and_save(
    country_a: str,
    country_b: str,
    start_year: int = 1900,
    end_year: int = 2005,
    max_events: int = 200,
    langs: Iterable[str] = DEFAULT_LANGS,
    output_path: Optional[str|Path] = None,
) -> List[EventSeed]:
    """Discover seeds and optionally save them to a JSON file.

    Returns the list of discovered seeds.
    """
    _, instructor_llm = build_llm_client()
    exa = build_exa_client()

    seeds = discover_events(
        client=instructor_llm,
        exa=exa,
        country_a=country_a,
        country_b=country_b,
        start_year=start_year,
        end_year=end_year,
        max_events=max_events,
        search_langs=langs,
    )
    logger.info(f"Found {len(seeds)} events.")

    if output_path:
        output_path = Path(output_path).resolve()
        os.makedirs(output_path.parent, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "llm": OPENAI_MODEL,
                    "start_year": start_year,
                    "end_year": end_year,
                    "countries": [country_a, country_b],
                    "max_events": max_events,
                    "langs": list(langs),
                    "search_engine": "exa",
                    "datetime": datetime.now().isoformat(),
                    "seeds": [s.model_dump(mode="json") for s in seeds],
                },
                f,
                ensure_ascii=False,
                indent=4,
            )
        logger.info(f"Discovered seeds saved to {output_path}")

    return seeds


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover historical conflict events (1900-2005)")
    parser.add_argument("country_a", type=str)
    parser.add_argument("country_b", type=str)
    parser.add_argument("--start", type=int, default=1900)
    parser.add_argument("--end", type=int, default=2005)
    parser.add_argument("--max-events", type=int, default=15)
    parser.add_argument(
        "--langs",
        type=str,
        default=",".join(DEFAULT_LANGS),
        help="Comma-separated list of Wikipedia languages to compare (e.g., en,fr,ru)",
    )
    parser.add_argument("--discover-output", type=str, required=True, help="Path to save discovered seeds JSON")
    args = parser.parse_args()

    logging.info(
        f"Discovering seeds for {args.country_a} vs {args.country_b} from {args.start} to {args.end} with {args.max_events} events and languages {args.langs}"
    )

    langs = [s.strip() for s in args.langs.split(",") if s.strip()]

    discover_and_save(
        country_a=args.country_a,
        country_b=args.country_b,
        start_year=args.start,
        end_year=args.end,
        max_events=args.max_events,
        langs=langs,
        output_path=Path(args.discover_output),
    )


if __name__ == "__main__":
    main()


