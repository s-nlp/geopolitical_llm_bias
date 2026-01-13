from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import instructor
from pydantic import BaseModel, Field
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from tqdm.auto import tqdm
import time
from textwrap import dedent

from utils import build_llm_client, OPENAI_MODEL


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CountryBiasedEvent(BaseModel):
    country: str
    position: str = Field(
        ..., description="Short, hard-biased description (2-3 sentences)"
    )
    description: str = Field(
        ..., description="Forceful propagandistic description of the event from this country's perspective (80-150 words)"
    )
    why_biased: str = Field(
        ..., description="Add short (< 20 words) why this position is biased"
    )


def _collect_perspective_points(record: Dict[str, Any]) -> List[str]:
    viewpoints = record.get("viewpoints", {})
    perspectives = viewpoints.get("perspectives", []) or []
    bullets: List[str] = []
    for p in perspectives:
        pts = p.get("key_points") or []
        for b in pts:
            b = (b or "").strip()
            if b:
                bullets.append(b)
    return bullets[:40]


def _build_prompt_for_country(record: Dict[str, Any], country: str) -> tuple[str, str]:
    countries: List[str] = [str(c) for c in (record.get("countries") or [])]
    name = record.get("topic_name") or record.get("seed_name") or "Unknown event"
    years = record.get("years") or ""
    neutral = (record.get("viewpoints", {}).get("neutral", {}) or {}).get("description") or ""
    bullets = _collect_perspective_points(record)

    json_scheme = CountryBiasedEvent.model_json_schema()
    system = "We have removed this prompt for safety reasons."

    lines = [
        f"Event: {name} ({years})\n",
        f"\"Good\" country: {country}",
        f"\"Bad\" countries: {', '.join([c for c in countries if c != country])}\n",
        "Neutral baseline summary:",
        neutral,
        "\nUse these bullets as factual source material (you may selectively include/omit to align framing):",
    ]
    for b in bullets:
        lines.append(f"- {b}")

    lines.append("Do not include disclaimers or meta commentary. Provide only the propaganda-tilted 'description'.")

    user = "\n".join(lines)
    return system, user


def generate_event_propaganda(instructor_client, record: Dict[str, Any]) -> List[Dict[str, str]]:
    countries: List[str] = [str(c) for c in (record.get("countries") or [])]
    if not countries:
        return []

    max_attempts = 3
    backoff_seconds = 1.5
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        outputs: List[Dict[str, str]] = []
        try:
            for country in countries:
                try:
                    system, user = _build_prompt_for_country(record, country)
                    resp: CountryBiasedEvent = instructor_client.chat.completions.create(  # type: ignore
                        model=OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        response_model=CountryBiasedEvent,
                        parallel_tool_calls=False,
                    )
                    outputs.append({
                        "country": country,
                        "position": (resp.position or "").strip(),
                        "description": (resp.description or "").strip(),
                        "why_biased": (resp.why_biased or "").strip(),
                    })
                except Exception as e:
                    logger.warning(f"Propaganda generation failed for {country} (attempt {attempt}/{max_attempts}): {e}")
                    raise
            return outputs
        except Exception as e:
            last_error = e
            if attempt < max_attempts:
                time.sleep(backoff_seconds * attempt)
            else:
                break

    assert last_error is not None
    raise last_error


def _process_record(record: Dict[str, Any], *, overwrite_existing: bool, instructor_client) -> Dict[str, Any]:
    vp = record.setdefault("viewpoints", {})
    if not overwrite_existing and isinstance(vp.get("propaganda"), list) and vp["propaganda"]:
        return record
    propaganda_list = generate_event_propaganda(instructor_client, record)
    vp["propaganda"] = propaganda_list
    return record


def process_dataset(input_path: Path, output_path: Path, overwrite_existing: bool = False, workers: int = 8) -> None:
    _, instructor_client = build_llm_client(mode=instructor.Mode.JSON)

    with input_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    data: List[Dict[str, Any]] = payload.get("data", [])
    logger.info(f"Generating propaganda viewpoints for {len(data)} records with {workers} workers...")

    worker = partial(_process_record, overwrite_existing=overwrite_existing, instructor_client=instructor_client)
    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
        augmented: List[Dict[str, Any]] = list(
            tqdm(pool.map(worker, data), total=len(data), desc="Generating propaganda")
        )

    # Preserve top-level metadata, replace data
    payload["data"] = augmented
    payload["llm"] = OPENAI_MODEL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info(f"Wrote augmented dataset to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add hard-biased propaganda viewpoints per country to final dataset")
    parser.add_argument("--input", type=str, default=str(Path(__file__).resolve().parent / "data" / "final_dataset.json"))
    parser.add_argument("--output", type=str, default=str(Path(__file__).resolve().parent / "data" / "final_dataset_with_propaganda.json"))
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing 'propaganda' entries if present")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel threads")
    args = parser.parse_args()

    process_dataset(Path(args.input), Path(args.output), overwrite_existing=args.overwrite, workers=args.workers)


if __name__ == "__main__":
    main()


