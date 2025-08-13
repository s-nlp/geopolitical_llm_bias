from __future__ import annotations

import json
import logging
import os
from typing import Iterable, List, Optional, Tuple

import instructor
from exa_py import Exa
from openai import OpenAI
from pydantic import BaseModel, Field, HttpUrl


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ===== Environment and configuration =====
OPENAI_BASE_URL: Optional[str] = os.environ.get("OPENAI_BASE_URL")
OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "openai/gpt-oss-120b")

if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set")
if OPENAI_BASE_URL is None:
    OPENAI_BASE_URL = "https://openrouter.ai/api/v1"
    logger.warning("OPENAI_BASE_URL is not set. Using the default OpenRouter URL.")

EXA_API_KEY: Optional[str] = os.environ.get("EXA_API_KEY")
if EXA_API_KEY is None:
    logger.warning("EXA_API_KEY is not set")

# Default languages used to compare multilingual Wikipedia articles
DEFAULT_LANGS: Tuple[str, ...] = ("en", "fr", "ru", "zh", "ar", "he")


# ===== Shared models =====
class EventSeed(BaseModel):
    name: str = Field(..., description="Canonical name of the event, maximum 30 words")
    url: HttpUrl = Field(..., description="Wikipedia URL for this event")


# ===== Shared clients =====
def build_llm_client() -> tuple[OpenAI, instructor.Instructor]:
    """Return OpenAI client and Instructor-wrapped OpenAI client."""
    base_client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
    logger.info(f"Using OpenAI model {OPENAI_MODEL} with base URL {OPENAI_BASE_URL}.")
    return base_client, instructor.from_openai(base_client)


def build_exa_client() -> Exa:
    logger.info("Exa initialized.")
    return Exa(api_key=EXA_API_KEY)


# ===== Shared utilities =====
def load_seeds_and_metadata(input_json_path: str) -> tuple[List[EventSeed], dict]:
    """Load seeds and return (seeds, metadata) from a discovered/unique/final JSON file.

    - Accepts either {"seeds": [...]} or {"data": [...]} formats.
    - Metadata is the remaining top-level fields with the seeds removed.
    """
    with open(input_json_path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    raw_seeds = obj.get("seeds") or obj.get("data") or []
    seeds: List[EventSeed] = []
    for it in raw_seeds:
        try:
            seeds.append(EventSeed.model_validate(it))
        except Exception:
            # Back-compat: if structure is slightly off, try mapping
            name = (it.get("name") if isinstance(it, dict) else None) or (it.get("title") if isinstance(it, dict) else None)
            url = (it.get("url") if isinstance(it, dict) else None)
            if name and url:
                seeds.append(EventSeed(name=name, url=url))

    # Copy to avoid mutating the original object
    metadata = dict(obj)
    metadata.pop("seeds", None)
    metadata.pop("data", None)
    return seeds, metadata


