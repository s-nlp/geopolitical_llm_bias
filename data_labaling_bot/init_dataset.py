import json
import os
from typing import Any, Dict, List

from db import (
    clear_dataset,
    init_db,
    insert_event,
    insert_viewpoint,
)


def _get_default_dataset_path() -> str:

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data_mining",
            "data",
            "final_dataset_with_propaganda_translated.json",
        )
    )


def load_dataset(path: str) -> Dict[str, Any]:

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:

    init_db()
    dataset_path = os.getenv("DATASET_PATH", _get_default_dataset_path())
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    data = load_dataset(dataset_path)
    events: List[Dict[str, Any]] = data.get("data") or []
    supported_languages = data.get("languages") or ["ar", "en", "fr", "he", "ru", "zh", "de"]

    clear_dataset()

    for idx, event_langs in enumerate(events):
        # Process each language version of the event
        for lang in supported_languages:
            if lang not in event_langs:
                continue
                
            ev = event_langs[lang]
            countries = ev.get("countries") or []
            country_a = countries[0] if len(countries) > 0 else "Country A"
            country_b = countries[1] if len(countries) > 1 else "Country B"

            # Insert event for this language
            event_id = insert_event(
                event_index=idx,
                seed_name=ev.get("seed_name"),
                topic_name=ev.get("topic_name"),
                topic_url=ev.get("topic_url"),
                topic_description=ev.get("topic_description"),
                years=ev.get("years"),
                country_a=country_a,
                country_b=country_b,
                language=lang,
            )

            viewpoints = ev.get("viewpoints") or {}
            
            # Handle neutral viewpoint
            if isinstance(viewpoints, dict):
                neutral = viewpoints.get("neutral")
                neutral_description = None
                
                if isinstance(neutral, dict):
                    neutral_description = neutral.get("description")

                # Fallback to perspectives if no neutral description
                if not neutral_description:
                    perspectives = viewpoints.get("perspectives") or []
                    if perspectives and len(perspectives) > 0:
                        perspective = perspectives[0]  # Take first perspective
                        key_points = perspective.get("key_points") or []
                        if key_points:
                            neutral_description = "\n".join(key_points)

                if neutral_description:
                    insert_viewpoint(
                        event_id=event_id,
                        viewpoint_type="neutral",
                        viewpoint_text=neutral_description,
                        propaganda_country=None,
                        viewpoint_index=None,
                        language=lang,
                    )

                # Handle propaganda viewpoints
                propaganda_list = viewpoints.get("propaganda") or []
                if isinstance(propaganda_list, list):
                    for i, prop in enumerate(propaganda_list):
                        text = prop.get("description") or prop.get("position") or ""
                        if text:  # Only insert if there's actual text
                            insert_viewpoint(
                                event_id=event_id,
                                viewpoint_type="propaganda",
                                viewpoint_text=text,
                                propaganda_country=prop.get("country"),
                                viewpoint_index=i,
                                language=lang,
                            )

    print(f"Dataset initialized into SQLite with {len(supported_languages)} languages.")


if __name__ == "__main__":
    main()


