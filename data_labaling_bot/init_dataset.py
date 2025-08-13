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
            "final_dataset_with_propaganda.json",
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

    clear_dataset()

    for idx, ev in enumerate(events):
        countries = ev.get("countries") or []
        country_a = countries[0] if len(countries) > 0 else "Country A"
        country_b = countries[1] if len(countries) > 1 else "Country B"

        viewpoints = (ev.get("viewpoints") or {})
        neutral_description = None
        if isinstance(viewpoints, dict):
            neutral = viewpoints.get("neutral")
            if isinstance(neutral, dict):
                neutral_description = neutral.get("description")

        if not neutral_description and isinstance(viewpoints, dict):
            perspectives = viewpoints.get("perspectives") or []
            preferred = None
            for p in perspectives:
                if p.get("language") == "en":
                    preferred = p
                    break
            if not preferred and perspectives:
                preferred = perspectives[0]
            if preferred:
                keys = preferred.get("key_points") or []
                if keys:
                    neutral_description = "\n".join(keys)

        event_id = insert_event(
            event_index=idx,
            seed_name=ev.get("seed_name"),
            topic_name=ev.get("topic_name"),
            topic_url=ev.get("topic_url"),
            topic_description=ev.get("topic_description"),
            years=ev.get("years"),
            country_a=country_a,
            country_b=country_b,
        )

        if neutral_description:
            insert_viewpoint(
                event_id=event_id,
                viewpoint_type="neutral",
                viewpoint_text=neutral_description,
                propaganda_country=None,
                viewpoint_index=None,
                language="en",
            )

        propaganda_list = []
        prop_section = viewpoints.get("propaganda") if isinstance(viewpoints, dict) else None
        if isinstance(prop_section, list):
            propaganda_list = prop_section

        for i, prop in enumerate(propaganda_list):
            text = prop.get("description") or prop.get("position") or ""
            lang = prop.get("language")
            insert_viewpoint(
                event_id=event_id,
                viewpoint_type="propaganda",
                viewpoint_text=text,
                propaganda_country=prop.get("country"),
                viewpoint_index=i,
                language=lang,
            )

    print("Dataset initialized into SQLite.")


if __name__ == "__main__":
    main()


