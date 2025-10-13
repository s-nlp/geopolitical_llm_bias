#!/usr/bin/env python3
"""
Script to translate the dataset with propaganda viewpoints to multiple languages.

This script:
1. Detects the current language of content using LLM
2. Translates topic names, descriptions, and viewpoints to target languages using LLM
3. Finds corresponding Wikipedia pages in target languages using Wikipedia API
4. Restructures the output with language codes as top-level keys
"""

import json
import logging
import os
import requests
from typing import Dict, List, Optional, Set
from pathlib import Path
from urllib.parse import urlparse, unquote, quote
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from tqdm import tqdm

# Try to import from utils, handle missing env vars gracefully
try:
    from utils import build_llm_client, OPENAI_MODEL
    HAS_LLM_CONFIG = True
except ValueError as e:
    HAS_LLM_CONFIG = False
    # OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "openai/gpt-oss-120b")
    OPENAI_MODEL = "openai/gpt-oss-20b"
    print(f"Warning: {e}")
    print("Please set OPENAI_API_KEY and optionally EXA_API_KEY to run translations.")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Suppress verbose HTTP request logs from httpx/httpcore
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Target languages including German
TARGET_LANGUAGES = [
    "ar",
    "en",
    "fr",
    "he",
    "ru",
    "zh",
    "de",
]

# Language names for prompts
LANGUAGE_NAMES = {
    "ar": "Arabic",
    "en": "English", 
    "fr": "French",
    "he": "Hebrew",
    "ru": "Russian",
    "zh": "Chinese",
    "de": "German"
}


class LanguageDetection(BaseModel):
    """Model for language detection response."""
    language_code: str = Field(..., description="Two-letter ISO language code (e.g., 'en', 'fr', 'ru')")
    confidence: float = Field(..., description="Confidence score between 0 and 1")


class TranslationResult(BaseModel):
    """Model for translation response."""
    translated_text: str = Field(..., description="The translated text")
    target_language: str = Field(..., description="Target language code")


def extract_wikipedia_title(url: str) -> Optional[str]:
    """Extract the article title from a Wikipedia URL."""
    try:
        parsed = urlparse(url)
        if 'wikipedia.org' not in parsed.netloc:
            return None
        
        # Extract title from path like /wiki/Article_Title
        path_parts = parsed.path.split('/')
        if len(path_parts) >= 3 and path_parts[1] == 'wiki':
            title = unquote(path_parts[2])
            return title.replace('_', ' ')
        return None
    except Exception:
        return None


def get_wikipedia_interlang_links(title: str, source_lang: str = 'en') -> Dict[str, str]:
    """Get interlanguage links for a Wikipedia article using the API."""
    try:
        # Wikipedia API endpoint
        api_url = f"https://{source_lang}.wikipedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'langlinks',
            'lllimit': 'max',
            'redirects': 1
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'query' not in data or 'pages' not in data['query']:
            return {}
        
        # Get the first (and usually only) page
        pages = data['query']['pages']
        page_id = list(pages.keys())[0]
        
        if page_id == '-1':  # Page not found
            return {}
        
        page = pages[page_id]
        if 'langlinks' not in page:
            return {}
        
        # Build mapping of language code to article title
        lang_links = {}
        for link in page['langlinks']:
            lang = link['lang']
            title = link['*']
            lang_links[lang] = title
        
        return lang_links
        
    except Exception as e:
        logger.warning(f"Failed to get interlanguage links for '{title}': {e}")
        return {}


def detect_language(client: instructor.Instructor, text: str) -> str:
    """Detect the language of given text."""
    prompt = f"""
    Detect the language of the following text and return the two-letter ISO language code.
    
    Text: "{text[:500]}..."
    
    No parallel tool calls.
    Return the two-letter language code (e.g., 'en', 'fr', 'ru', 'zh', 'ar', 'he', 'de').
    """

    attempts = 3
    delay_seconds = 1.0
    for attempt in range(1, attempts + 1):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                response_model=LanguageDetection,
                messages=[{"role": "user", "content": prompt}],
                parallel_tool_calls=False,
            )
            return response.language_code
        except Exception as e:
            if attempt == attempts:
                logger.warning(f"Language detection failed after {attempts} attempts: {e}")
                return "en"
            time.sleep(delay_seconds)
            delay_seconds *= 2


def translate_text(client: instructor.Instructor, text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate text to target language using LLM."""
    if target_lang == source_lang:
        return text
        
    target_name = LANGUAGE_NAMES.get(target_lang, target_lang)
    source_name = LANGUAGE_NAMES.get(source_lang, "detected language") if source_lang != "auto" else "detected language"
    
    prompt = f"""
    Translate the following text from {source_name} to {target_name}.
    Maintain the original meaning and tone. For historical and political content, be precise and neutral.
    
    Text to translate: "{text}"
    
    No parallel tool calls.
    Return the translated text, no additional commentary.
    Double check that translation complete. 
    """

    attempts = 3
    delay_seconds = 1.0
    for attempt in range(1, attempts + 1):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                response_model=TranslationResult,
                messages=[{"role": "user", "content": prompt}],
                parallel_tool_calls=False,
            )
            return response.translated_text
        except Exception as e:
            if attempt == attempts:
                logger.warning(f"Translation failed after {attempts} attempts: {e}")
                return text
            time.sleep(delay_seconds)
            delay_seconds *= 2


def find_wikipedia_url(original_url: str, target_lang: str) -> str:
    """Find Wikipedia URL for the topic in target language using Wikipedia API.
    
    If the article doesn't exist in the target language, returns the original URL.
    """
    # Extract article title from original URL
    title = extract_wikipedia_title(original_url)
    if not title:
        logger.warning(f"Could not extract title from URL: {original_url}")
        return original_url
    
    # Detect source language from URL
    try:
        parsed = urlparse(original_url)
        source_lang = parsed.netloc.split('.')[0]
    except Exception:
        source_lang = 'en'  # Default to English
    
    # Get interlanguage links
    lang_links = get_wikipedia_interlang_links(title, source_lang)
    
    # Check if target language exists
    if target_lang in lang_links:
        target_title = lang_links[target_lang]
        # URL encode the title for the Wikipedia URL
        encoded_title = quote(target_title.replace(' ', '_'), safe='')
        return f"https://{target_lang}.wikipedia.org/wiki/{encoded_title}"
    
    # If target language not found, return original URL
    logger.debug(f"No {target_lang} version found for '{title}', keeping original URL")
    return original_url


def translate_viewpoint(client: instructor.Instructor, viewpoint: Dict, target_lang: str, source_lang: str) -> Dict:
    """Translate a single viewpoint to target language."""
    translated = viewpoint.copy()
    
    # Translate description if it exists
    if "description" in viewpoint:
        translated["description"] = translate_text(client, viewpoint["description"], target_lang, source_lang)
    
    # Update language code
    if "language" in viewpoint:
        translated["language"] = target_lang
    
    # Update URL if it exists
    if "url" in viewpoint:
        translated["url"] = find_wikipedia_url(viewpoint["url"], target_lang)
    
    # Translate key_points if they exist
    if "key_points" in viewpoint:
        translated["key_points"] = [
            translate_text(client, point, target_lang, source_lang) 
            for point in viewpoint["key_points"]
        ]
    
    return translated


def translate_propaganda_entry(client: instructor.Instructor, propaganda: Dict, target_lang: str, source_lang: str) -> Dict:
    """Translate a propaganda entry to target language."""
    translated = propaganda.copy()
    
    # Translate position and description
    if "position" in propaganda:
        translated["position"] = translate_text(client, propaganda["position"], target_lang, source_lang)
    
    if "description" in propaganda:
        translated["description"] = translate_text(client, propaganda["description"], target_lang, source_lang)
    
    return translated

def translate_country_name(client: instructor.Instructor, country: str, target_lang: str, source_lang: str) -> str:
    """Translate a country name to target language."""
    # Standard country name mappings for different languages
    COUNTRY_TRANSLATIONS = {
        "USSR": {
            "ar": "الاتحاد السوفيتي",
            "en": "USSR", 
            "fr": "URSS",
            "he": "ברית המועצות",
            "ru": "СССР",
            "zh": "苏联",
            "de": "UdSSR"
        },
        "USA": {
            "ar": "الولايات المتحدة",
            "en": "USA",
            "fr": "États-Unis", 
            "he": "ארצות הברית",
            "ru": "США",
            "zh": "美国",
            "de": "USA"
        },
        "US": {
            "ar": "الولايات المتحدة",
            "en": "US",
            "fr": "États-Unis",
            "he": "ארצות הברית", 
            "ru": "США",
            "zh": "美国",
            "de": "USA"
        },
        "China": {
            "ar": "الصين",
            "en": "China",
            "fr": "Chine",
            "he": "סין",
            "ru": "Китай", 
            "zh": "中国",
            "de": "China"
        },
        "UK": {
            "ar": "المملكة المتحدة",
            "en": "UK",
            "fr": "Royaume-Uni",
            "he": "בריטניה",
            "ru": "Великобритания",
            "zh": "英国", 
            "de": "Vereinigtes Königreich"
        }
    }

    if country.upper() in COUNTRY_TRANSLATIONS and target_lang in COUNTRY_TRANSLATIONS[country.upper()]:
        return COUNTRY_TRANSLATIONS[country.upper()][target_lang]
    return country.upper()

def translate_data_entry(client: instructor.Instructor, entry: Dict, target_lang: str) -> Dict:
    """Translate a complete data entry to target language."""
    # Detect source language from topic_description
    source_lang = detect_language(client, entry.get("topic_description", ""))
    # logger.info(f"Detected source language: {source_lang} for topic: {entry.get('topic_name', 'Unknown')}")
    
    if target_lang == source_lang:
        return entry
    
    translated = entry.copy()
    
    # Translate seed_name, topic_name and topic_description
    if "seed_name" in entry:
        translated["seed_name"] = translate_text(client, entry["seed_name"], target_lang, source_lang)
    
    if "topic_name" in entry:
        translated["topic_name"] = translate_text(client, entry["topic_name"], target_lang, source_lang)
    
    if "topic_description" in entry:
        translated["topic_description"] = translate_text(client, entry["topic_description"], target_lang, source_lang)
    
    # Update topic_url to target language
    if "topic_url" in entry:
        translated["topic_url"] = find_wikipedia_url(entry["topic_url"], target_lang)

    if "countries" in entry:
        translated["countries"] = [
            translate_country_name(client, country, target_lang, source_lang)
            for country in entry["countries"]
        ]
    
    # Translate viewpoints
    if "viewpoints" in entry:
        translated_viewpoints = entry["viewpoints"].copy()
        
        # Translate neutral description
        if "neutral" in translated_viewpoints and "description" in translated_viewpoints["neutral"]:
            translated_viewpoints["neutral"]["description"] = translate_text(
                client, translated_viewpoints["neutral"]["description"], target_lang, source_lang
            )
        
        # Translate perspectives
        if "perspectives" in translated_viewpoints:
            translated_viewpoints["perspectives"] = [
                translate_viewpoint(client, perspective, target_lang, source_lang)
                for perspective in translated_viewpoints["perspectives"]
            ]
        
        # Translate propaganda viewpoints
        if "propaganda" in translated_viewpoints:
            translated_viewpoints["propaganda"] = [
                translate_propaganda_entry(client, propaganda, target_lang, source_lang)
                for propaganda in translated_viewpoints["propaganda"]
            ]
            translated_viewpoints["propaganda"][0]["country"] = translate_country_name(client, translated_viewpoints["propaganda"][0]["country"], target_lang, source_lang)
            translated_viewpoints["propaganda"][1]["country"] = translate_country_name(client, translated_viewpoints["propaganda"][1]["country"], target_lang, source_lang)
        
        translated["viewpoints"] = translated_viewpoints
    
    return translated


def main(input_file: Path, output_file: Path, workers: int) -> None:
    """Main function to translate the dataset."""
    # Load input data
    logger.info(f"Loading data from {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Check if LLM configuration is available
    if not HAS_LLM_CONFIG:
        logger.error("LLM configuration not available. Cannot run translations.")
        logger.error("Please set the required environment variables:")
        logger.error("- OPENAI_API_KEY (required)")
        logger.error("- EXA_API_KEY (optional)")
        logger.error("- OPENAI_BASE_URL (optional, defaults to OpenRouter)")
        logger.error("- OPENAI_MODEL (optional, defaults to openai/gpt-oss-120b)")
        return
    
    # Build LLM client
    logger.info("Initializing LLM client")
    _, client = build_llm_client()
    
    # Prepare per-language results store
    entries = data.get("data", [])
    per_language_results: Dict[str, List[Dict]] = {}

    # Process each target language
    for lang in TARGET_LANGUAGES:
        logger.info(f"Processing language: {lang} ({LANGUAGE_NAMES.get(lang, lang)})")

        if not entries:
            per_language_results[lang] = []
            continue

        # Preallocate list to preserve original order
        ordered_results = [None] * len(entries)

        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            future_to_index = {
                executor.submit(translate_data_entry, client, entry, lang): idx
                for idx, entry in enumerate(entries)
            }

            for future in tqdm(as_completed(future_to_index), total=len(future_to_index), desc=f"Translating to {lang}"):
                idx = future_to_index[future]
                try:
                    ordered_results[idx] = future.result()
                except Exception as e:
                    logger.error(f"Error translating entry index {idx} for {lang}: {e}")
                    ordered_results[idx] = entries[idx]

        per_language_results[lang] = ordered_results
    
    # Combine per-language results into the requested final schema
    combined_data: List[Dict[str, Dict]] = []
    total_items = len(entries)
    for idx in range(total_items):
        item_for_all_langs: Dict[str, Dict] = {}
        for lang in TARGET_LANGUAGES:
            lang_results = per_language_results.get(lang, [])
            value = None
            if idx < len(lang_results):
                value = lang_results[idx]
            # Fallback to original entry if missing
            if value is None:
                value = entries[idx]
            item_for_all_langs[lang] = value
        combined_data.append(item_for_all_langs)

    output_object = {
        "llm": data.get("llm"),
        "languages": TARGET_LANGUAGES,
        "start_year": data.get("start_year"),
        "end_year": data.get("end_year"),
        "data": combined_data,
    }

    # Save translated data
    logger.info(f"Saving translated data to {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_object, f, ensure_ascii=False, indent=2)
    
    logger.info("Translation completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate dataset to multiple languages and resolve Wikipedia interlanguage links.")
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path("data/final_dataset_with_propaganda.json"),
        help="Path to input JSON dataset (default: data/final_dataset_with_propaganda.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("data/final_dataset_with_propaganda_translated.json"),
        help="Path to output JSON file (default: data/final_dataset_with_propaganda_translated.json)",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=4,
        help="Number of threads for parallel translation (default: 4)",
    )
    args = parser.parse_args()
    main(args.input, args.output, args.workers)
