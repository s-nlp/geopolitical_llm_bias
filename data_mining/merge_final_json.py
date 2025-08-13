from __future__ import annotations

import json
import re
from datetime import datetime
import argparse
from pathlib import Path
from typing import Any, Dict, List, Set


def _extract_years(years_text: str) -> List[int]:
    if not years_text:
        return []
    return [int(y) for y in re.findall(r"\b(\d{4})\b", years_text)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge *_final.json datasets into a unified JSON")
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Input JSON files. If omitted, defaults to known *_final.json files in data_mining/data",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to write merged JSON (default: ./data/final_dataset.json)",
    )
    args = parser.parse_args()


    if args.inputs:
        input_files = [Path(p) if Path(p).is_absolute() else (Path.cwd() / p) for p in args.inputs]
    else:
        data_dir = Path(__file__).resolve().parent / "data"
        input_files = [
            data_dir / "USSR_UK_final.json",
            data_dir / "USA_USSR_final.json",
            data_dir / "USA_UK_final.json",
            data_dir / "USA_China_final.json",
            data_dir / "UK_China_final.json",
            data_dir / "China_USSR_final.json",
        ]

    merged_records: List[Dict[str, Any]] = []
    llm_values: Set[str] = set()
    langs_union: Set[str] = set()
    all_year_numbers: List[int] = []
    any_present_flag = False
    root_start_years: Set[int] = set()
    root_end_years: Set[int] = set()

    for path in input_files:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        if "llm" in payload:
            llm_values.add(payload["llm"]) 
        if "langs" in payload and isinstance(payload["langs"], list):
            langs_union.update([str(l) for l in payload["langs"]])
        if isinstance(payload.get("start_year"), int):
            root_start_years.add(int(payload["start_year"]))
        if isinstance(payload.get("end_year"), int):
            root_end_years.add(int(payload["end_year"]))

        pair_str = path.name.rsplit("_final", 1)[0]
        country_parts = pair_str.split("_")
        countries = country_parts[:2]

        for item in payload.get("data", []):
            seed = item.get("seed", {})
            extracted = item.get("extracted", {})
            debiased = item.get("debiased", {})

            years_text = str(extracted.get("years", ""))
            all_year_numbers.extend(_extract_years(years_text))
            if "present" in years_text.lower():
                any_present_flag = True

            record = {
                "countries": countries,
                "seed_name": seed.get("name"),
                "topic_url": extracted.get("url"),
                "topic_name": extracted.get("name"),
                "years": years_text,
                "topic_description": extracted.get("short_description"),
                "paragraph_anchor_or_comment": extracted.get("paragraph_anchor_or_comment"),
                "viewpoints": {
                    "neutral": {
                        "description": debiased.get("neutral_description_50_words_max"),
                    },
                    "perspectives": debiased.get("perspectives", []),
                },
            }

            merged_records.append(record)

    # Prefer start/end years from the root of input files (they are expected to be the same across inputs)
    if root_start_years:
        start_year = sorted(root_start_years)[0]
    else:
        start_year = min(all_year_numbers) if all_year_numbers else None

    if root_end_years:
        end_year = sorted(root_end_years)[-1]
    else:
        if any_present_flag:
            end_year = datetime.utcnow().year
        else:
            end_year = max(all_year_numbers) if all_year_numbers else None

    output = {
        "llm": next(iter(llm_values)) if llm_values else None,
        "languages": sorted(langs_union),
        "start_year": start_year,
        "end_year": end_year,
        "data": merged_records,
    }

    default_out_base = Path(__file__).resolve().parent / "data"
    out_path = Path(args.output) if args.output else (default_out_base / "final_dataset.json")
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()


