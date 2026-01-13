#!/usr/bin/env python3
"""
Script to validate, fix translations, and filter polarizing events in the dataset.

This script:
1. Validates language detection of text fields
2. Fixes incomplete translations using LLM
3. Validates Wikipedia URLs for target languages
4. Fixes inconsistent country name translations
5. Filters out non-polarizing historical events using LLM assessment

Requirements:
- OPENAI_API_KEY environment variable must be set
- LLM functionality is required for this script

Usage:
    python dataset_validation.py --input data/final_dataset_with_propaganda_translated.json
"""

import json
import logging
import argparse
from textwrap import dedent
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse, quote, unquote
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import langdetect
from langdetect.lang_detect_exception import LangDetectException
# Required LLM imports
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from tqdm.auto import tqdm

# Import from local utils - fail fast if not available
from utils import build_llm_client, OPENAI_MODEL, DEFAULT_LANGS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress verbose HTTP request logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Supported languages - extend DEFAULT_LANGS to include German
SUPPORTED_LANGUAGES = list(DEFAULT_LANGS) + ["de"] if "de" not in DEFAULT_LANGS else list(DEFAULT_LANGS)

# Language detection mappings (langdetect uses different codes)
LANGDETECT_TO_ISO = {
    "ar": "ar",
    "en": "en", 
    "fr": "fr",
    "he": "he",
    "ru": "ru",
    "zh": "zh",
    "zh-cn": "zh",
    "de": "de"
}

# Fields that should contain translatable text
TEXT_FIELDS = [
    "seed_name",
    "topic_name", 
    "topic_description",
    "countries"
]

# Standard country name translations
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

# Language names for LLM prompts
LANGUAGE_NAMES = {
    "ar": "Arabic",
    "en": "English", 
    "fr": "French",
    "he": "Hebrew",
    "ru": "Russian",
    "zh": "Chinese",
    "de": "German"
}

# Pydantic models for LLM responses
class TranslationResult(BaseModel):
    """Model for translation response."""
    translated_text: str = Field(..., description="The translated text")
    target_language: str = Field(..., description="Target language code")


class PolarizationAssessment(BaseModel):
    """Model for polarization assessment response."""
    is_polarizing: bool = Field(..., description="Whether the event is polarizing between countries")
    confidence: float = Field(..., description="Confidence score between 0 and 1")
    reasoning: str = Field(..., description="Brief explanation of the assessment")

class PolarizationAssessments(BaseModel):
    """Model for multiple polarization assessments response."""
    assessments: List[PolarizationAssessment] = Field(..., description="List of polarization assessments")


class LanguageDetection(BaseModel):
    """Model for language detection response."""
    language_code: str = Field(..., description="Two-letter ISO language code")
    confidence: float = Field(..., description="Confidence score between 0 and 1")


def translate_text_llm(client, text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate text to target language using LLM."""
    if target_lang == source_lang:
        return text
        
    target_name = LANGUAGE_NAMES.get(target_lang, target_lang)
    source_name = LANGUAGE_NAMES.get(source_lang, "detected language") if source_lang != "auto" else "detected language"
    
    system_prompt = "We have removed this prompt for safety reasons."
    
    user_prompt = dedent(f"""Translate the following text from {source_name} to {target_name}.
    Maintain the original meaning and tone. For historical and political content, be precise and neutral.

    Text to translate: "{text}"

    Provide only the translated text with no additional commentary.""")

    attempts = 3
    delay_seconds = 1.0
    for attempt in range(1, attempts + 1):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                response_model=TranslationResult,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                parallel_tool_calls=False,
            )
            return response.translated_text
        except Exception as e:
            if attempt == attempts:
                logger.warning(f"Translation failed after {attempts} attempts: {e}")
                return text
            time.sleep(delay_seconds)
            delay_seconds *= 2


def detect_language_llm(client, text: str) -> str:
    """Detect the language of given text using LLM."""
    system_prompt = "We have removed this prompt for safety reasons."
    
    user_prompt = dedent(f"""Detect the language of the following text and return the two-letter ISO language code.

    Text: "{text[:500]}..."

    Identify the language and provide the two-letter code (e.g., 'en', 'fr', 'ru', 'zh', 'ar', 'he', 'de').""")

    attempts = 3
    delay_seconds = 1.0
    for attempt in range(1, attempts + 1):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                response_model=LanguageDetection,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                parallel_tool_calls=False,
            )
            return response.language_code
        except Exception as e:
            if attempt == attempts:
                logger.warning(f"Language detection failed after {attempts} attempts: {e}")
                return "en"
            time.sleep(delay_seconds)
            delay_seconds *= 2


def assess_event_polarization(client, full_entry: Dict) -> Tuple[bool, str]:
    """Assess if a historical event is polarizing between countries using LLM.
    
    Uses English content for analysis when available, with fallback to other languages.
    """
    # Prioritize English for assessment, fallback to other languages
    entry = None
    if "en" in full_entry:
        entry = full_entry["en"]
    else:
        # Fallback to first available language
        for lang in SUPPORTED_LANGUAGES:
            if lang in full_entry:
                entry = full_entry[lang]
                break
    
    if not entry:
        return True, "No valid entry found - keeping event"
    
    # Extract key information from entry (now guaranteed to be English if available)
    topic_name = entry.get("topic_name", "Unknown event")
    topic_description = entry.get("topic_description", "")
    countries = entry.get("countries", [])
    years = entry.get("years", "")
    
    system_prompt = "We have removed this prompt for safety reasons."

    user_prompt = dedent(f"""Analyze this historical event to determine if it represents a genuine conflict or controversial topic that would polarize communities and generate different viewpoints from supporters of different countries.

    Event: {topic_name}
    Years: {years}  
    Countries involved: {', '.join(countries)}
    Description: {topic_description}

    Consider these criteria:
    1. Is this event a conflict, war, political dispute, or controversial topic between nations?
    2. Would supporters of different countries have fundamentally different perspectives on this event?
    3. Is this something that would generate heated debate and polarized opinions?
    4. Does this event involve national interests, territorial disputes, ideological conflicts, or competing claims?

    Examples of polarizing events: wars, territorial conflicts, political interventions, ideological disputes, colonial conflicts
    Examples of non-polarizing events: natural disasters, scientific discoveries, cultural festivals, sports events, purely domestic issues

    Provide a single assessment with your determination and brief reasoning.""")

    attempts = 3
    delay_seconds = 1.0
    for attempt in range(1, attempts + 1):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                response_model=PolarizationAssessments,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                parallel_tool_calls=False,
            )
            return response.assessments[0].is_polarizing, response.assessments[0].reasoning
        except Exception as e:
            if attempt == attempts:
                logger.warning(f"Polarization assessment failed after {attempts} attempts: {e}")
                return True, f"Assessment failed - keeping event: {e}"
            time.sleep(delay_seconds)
            delay_seconds *= 2


def find_wikipedia_url(original_url: str, target_lang: str) -> str:
    """Find Wikipedia URL for the topic in target language using Wikipedia API."""
    import requests
    
    # Extract article title from original URL
    def extract_wikipedia_title(url: str) -> Optional[str]:
        try:
            parsed = urlparse(url)
            if 'wikipedia.org' not in parsed.netloc:
                return None
            path_parts = parsed.path.split('/')
            if len(path_parts) >= 3 and path_parts[1] == 'wiki':
                title = unquote(path_parts[2])
                return title.replace('_', ' ')
            return None
        except Exception:
            return None
    
    title = extract_wikipedia_title(original_url)
    if not title:
        return original_url
    
    # Detect source language from URL
    try:
        parsed = urlparse(original_url)
        source_lang = parsed.netloc.split('.')[0]
    except Exception:
        source_lang = 'en'
    
    # Get interlanguage links from Wikipedia API
    try:
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
        
        if 'query' in data and 'pages' in data['query']:
            pages = data['query']['pages']
            page_id = list(pages.keys())[0]
            
            if page_id != '-1' and 'langlinks' in pages[page_id]:
                for link in pages[page_id]['langlinks']:
                    if link['lang'] == target_lang:
                        target_title = link['*']
                        encoded_title = quote(target_title.replace(' ', '_'), safe='')
                        return f"https://{target_lang}.wikipedia.org/wiki/{encoded_title}"
        
        return original_url
        
    except Exception as e:
        logger.debug(f"Failed to get Wikipedia URL for {target_lang}: {e}")
        return original_url


class ValidationResults:
    """Container for validation results."""
    
    def __init__(self):
        self.issues: List[Dict] = []
        self.stats: Dict[str, int] = {
            "total_entries": 0,
            "language_mismatches": 0,
            "missing_translations": 0,
            "invalid_urls": 0,
            "inconsistent_countries": 0,
            "non_polarizing_events": 0,
            "translation_fixes": 0,
            "url_fixes": 0
        }
    
    def add_issue(self, issue_type: str, entry_idx: int, language: str, field: str, details: str):
        """Add a validation issue."""
        self.issues.append({
            "type": issue_type,
            "entry_index": entry_idx,
            "language": language,
            "field": field,
            "details": details
        })
        if issue_type in self.stats:
            self.stats[issue_type] += 1
    
    def print_summary(self):
        """Print validation summary."""
        logger.info(f"Validation Summary:")
        logger.info(f"  Total entries: {self.stats['total_entries']}")
        logger.info(f"  Language mismatches: {self.stats['language_mismatches']}")
        logger.info(f"  Missing translations: {self.stats['missing_translations']}")
        logger.info(f"  Invalid URLs: {self.stats['invalid_urls']}")
        logger.info(f"  Inconsistent countries: {self.stats['inconsistent_countries']}")
        logger.info(f"  Non-polarizing events: {self.stats['non_polarizing_events']}")
        logger.info(f"  Translation fixes applied: {self.stats['translation_fixes']}")
        logger.info(f"  URL fixes applied: {self.stats['url_fixes']}")
        logger.info(f"  Total issues: {len(self.issues)}")


def detect_text_language(text: str) -> Optional[str]:
    """Detect language of text using langdetect."""
    if not text or len(text.strip()) < 3:
        return None
    
    try:
        detected = langdetect.detect(text)
        return LANGDETECT_TO_ISO.get(detected, detected)
    except LangDetectException:
        return None


def is_wikipedia_url(url: str) -> bool:
    """Check if URL is a Wikipedia URL."""
    try:
        parsed = urlparse(url)
        return 'wikipedia.org' in parsed.netloc
    except:
        return False


def get_wikipedia_language(url: str) -> Optional[str]:
    """Extract language code from Wikipedia URL."""
    try:
        parsed = urlparse(url)
        if 'wikipedia.org' in parsed.netloc:
            return parsed.netloc.split('.')[0]
    except:
        pass
    return None


def validate_text_field(text: str, expected_lang: str) -> bool:
    """Validate that text is in expected language."""
    if not text:
        return False
    
    detected_lang = detect_text_language(text)
    if not detected_lang:
        return False
    
    return detected_lang == expected_lang


def normalize_country_name(country: str) -> str:
    """Normalize country name for comparison."""
    # Handle common variations
    normalized = country.upper().strip()
    if normalized in ["UNITED STATES", "UNITED STATES OF AMERICA"]:
        return "USA"
    elif normalized in ["SOVIET UNION", "UNION OF SOVIET SOCIALIST REPUBLICS"]:
        return "USSR"
    elif normalized in ["UNITED KINGDOM", "GREAT BRITAIN", "BRITAIN"]:
        return "UK"
    elif normalized in ["PEOPLE'S REPUBLIC OF CHINA", "PRC"]:
        return "China"
    return normalized


def validate_country_translation(country: str, expected_lang: str) -> bool:
    """Check if country name is properly translated."""
    normalized = normalize_country_name(country)
    
    if normalized in COUNTRY_TRANSLATIONS:
        expected_translation = COUNTRY_TRANSLATIONS[normalized].get(expected_lang)
        if expected_translation:
            return country == expected_translation
    
    # For unknown countries, check if it's in the right language
    return validate_text_field(country, expected_lang)


def validate_entry(entry: Dict, entry_idx: int, results: ValidationResults):
    """Validate a single data entry."""
    results.stats["total_entries"] += 1
    
    for lang in SUPPORTED_LANGUAGES:
        if lang not in entry:
            results.add_issue("missing_translations", entry_idx, lang, "entire_entry", 
                            f"Missing language section for {lang}")
            continue
        
        lang_data = entry[lang]
        
        # Validate text fields
        for field in TEXT_FIELDS:
            if field in lang_data:
                value = lang_data[field]
                
                if field == "countries":
                    # Validate country list
                    if isinstance(value, list):
                        for i, country in enumerate(value):
                            if not validate_country_translation(country, lang):
                                results.add_issue("inconsistent_countries", entry_idx, lang, 
                                                f"countries[{i}]", f"Country '{country}' not properly translated")
                elif isinstance(value, str):
                    # Validate text language
                    if not validate_text_field(value, lang):
                        detected = detect_text_language(value)
                        results.add_issue("language_mismatches", entry_idx, lang, field, 
                                        f"Expected {lang}, detected {detected}")
        
        # Validate Wikipedia URL
        if "topic_url" in lang_data:
            url = lang_data["topic_url"]
            if is_wikipedia_url(url):
                url_lang = get_wikipedia_language(url)
                if url_lang != lang:
                    results.add_issue("invalid_urls", entry_idx, lang, "topic_url", 
                                    f"URL language {url_lang} doesn't match expected {lang}")
        
        # Validate viewpoints
        if "viewpoints" in lang_data:
            viewpoints = lang_data["viewpoints"]
            
            # Check neutral description
            if "neutral" in viewpoints and "description" in viewpoints["neutral"]:
                desc = viewpoints["neutral"]["description"]
                if not validate_text_field(desc, lang):
                    detected = detect_text_language(desc)
                    results.add_issue("language_mismatches", entry_idx, lang, "neutral.description", 
                                    f"Expected {lang}, detected {detected}")
            
            # Check perspectives
            if "perspectives" in viewpoints:
                for i, perspective in enumerate(viewpoints["perspectives"]):
                    if "key_points" in perspective:
                        for j, point in enumerate(perspective["key_points"]):
                            if not validate_text_field(point, lang):
                                detected = detect_text_language(point)
                                results.add_issue("language_mismatches", entry_idx, lang, 
                                                f"perspectives[{i}].key_points[{j}]", 
                                                f"Expected {lang}, detected {detected}")
            
            # Check propaganda
            if "propaganda" in viewpoints:
                for i, prop in enumerate(viewpoints["propaganda"]):
                    for prop_field in ["position", "description"]:
                        if prop_field in prop:
                            if not validate_text_field(prop[prop_field], lang):
                                detected = detect_text_language(prop[prop_field])
                                results.add_issue("language_mismatches", entry_idx, lang, 
                                                f"propaganda[{i}].{prop_field}", 
                                                f"Expected {lang}, detected {detected}")
                    
                    # Check country name in propaganda
                    if "country" in prop:
                        country = prop["country"]
                        if not validate_country_translation(country, lang):
                            results.add_issue("inconsistent_countries", entry_idx, lang, 
                                            f"propaganda[{i}].country", 
                                            f"Country '{country}' not properly translated")


def fix_country_names(entry: Dict) -> Dict:
    """Fix country name translations in an entry."""
    fixed_entry = entry.copy()
    
    for lang in SUPPORTED_LANGUAGES:
        if lang not in fixed_entry:
            continue
        
        lang_data = fixed_entry[lang]
        
        # Fix countries array
        if "countries" in lang_data and isinstance(lang_data["countries"], list):
            fixed_countries = []
            for country in lang_data["countries"]:
                normalized = normalize_country_name(country)
                if normalized in COUNTRY_TRANSLATIONS:
                    fixed_countries.append(COUNTRY_TRANSLATIONS[normalized][lang])
                else:
                    fixed_countries.append(country)
            lang_data["countries"] = fixed_countries
        
        # Fix propaganda country names
        if "viewpoints" in lang_data and "propaganda" in lang_data["viewpoints"]:
            for prop in lang_data["viewpoints"]["propaganda"]:
                if "country" in prop:
                    normalized = normalize_country_name(prop["country"])
                    if normalized in COUNTRY_TRANSLATIONS:
                        prop["country"] = COUNTRY_TRANSLATIONS[normalized][lang]
    
    return fixed_entry


def fix_entry_translations(entry: Dict, client, results: ValidationResults) -> Dict:
    """Fix translation issues in an entry using LLM."""
    fixed_entry = entry.copy()
    
    for lang in SUPPORTED_LANGUAGES:
        if lang not in fixed_entry:
            continue
        
        lang_data = fixed_entry[lang]
        
        # Fix text fields
        for field in TEXT_FIELDS:
            if field in lang_data:
                value = lang_data[field]
                
                if field == "countries":
                    continue  # Already handled by fix_country_names
                elif isinstance(value, str):
                    # Check if translation is needed
                    if not validate_text_field(value, lang):
                        # Detect source language
                        source_lang = detect_text_language(value)
                        if source_lang and source_lang != lang:
                            # Fix translation
                            fixed_text = translate_text_llm(client, value, lang, source_lang)
                            if fixed_text != value:
                                lang_data[field] = fixed_text
                                results.stats["translation_fixes"] += 1
        
        # Fix Wikipedia URL
        if "topic_url" in lang_data:
            url = lang_data["topic_url"]
            if is_wikipedia_url(url):
                url_lang = get_wikipedia_language(url)
                if url_lang != lang:
                    # Try to find correct URL
                    fixed_url = find_wikipedia_url(url, lang)
                    if fixed_url != url:
                        lang_data["topic_url"] = fixed_url
                        results.stats["url_fixes"] += 1
        
        # Fix viewpoints
        if "viewpoints" in lang_data:
            viewpoints = lang_data["viewpoints"]
            
            # Fix neutral description
            if "neutral" in viewpoints and "description" in viewpoints["neutral"]:
                desc = viewpoints["neutral"]["description"]
                if not validate_text_field(desc, lang):
                    source_lang = detect_text_language(desc)
                    if source_lang and source_lang != lang:
                        fixed_desc = translate_text_llm(client, desc, lang, source_lang)
                        if fixed_desc != desc:
                            viewpoints["neutral"]["description"] = fixed_desc
                            results.stats["translation_fixes"] += 1
            
            # Fix perspectives
            if "perspectives" in viewpoints:
                for i, perspective in enumerate(viewpoints["perspectives"]):
                    if "key_points" in perspective:
                        for j, point in enumerate(perspective["key_points"]):
                            if not validate_text_field(point, lang):
                                source_lang = detect_text_language(point)
                                if source_lang and source_lang != lang:
                                    fixed_point = translate_text_llm(client, point, lang, source_lang)
                                    if fixed_point != point:
                                        perspective["key_points"][j] = fixed_point
                                        results.stats["translation_fixes"] += 1
            
            # Fix propaganda
            if "propaganda" in viewpoints:
                for i, prop in enumerate(viewpoints["propaganda"]):
                    for prop_field in ["position", "description"]:
                        if prop_field in prop:
                            text = prop[prop_field]
                            if not validate_text_field(text, lang):
                                source_lang = detect_text_language(text)
                                if source_lang and source_lang != lang:
                                    fixed_text = translate_text_llm(client, text, lang, source_lang)
                                    if fixed_text != text:
                                        prop[prop_field] = fixed_text
                                        results.stats["translation_fixes"] += 1
    
    return fixed_entry


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate, fix translations, and filter polarizing events in dataset")
    parser.add_argument("--input", "-i", type=Path, 
                       default=Path("data/final_dataset_with_propaganda_translated.json"),
                       help="Path to input JSON file (default: data/final_dataset_with_propaganda_translated.json)")
    parser.add_argument("--output", "-o", type=Path,
                       default=Path("data/final_dataset_with_propaganda_translated_validated.json"),
                       help="Path to output processed JSON file (optional)")
    parser.add_argument("--validation-only", action="store_true",
                       default=False,
                       help="Only validate without fixing translations or filtering events")
    parser.add_argument("--skip-polarization-filter", action="store_true",
                       default=False,
                       help="Skip polarization filtering (keep all events)")
    parser.add_argument("--report", "-r", type=Path,
                       default=Path("data/final_dataset_with_propaganda_translated_validated_report.json"),
                       help="Path to save validation report (optional)")
    parser.add_argument("--limit", "-l", type=int,
                       default=None,
                       help="Limit validation to first N entries (for testing)")
    parser.add_argument("--workers", type=int,
                       default=4,
                       help="Number of threads for parallel processing")
    
    args = parser.parse_args()
    
    # Load data
    logger.info(f"Loading data from {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Initialize LLM client - required for this script
    logger.info("Initializing LLM client")
    _, client = build_llm_client()

    # Validate and process
    logger.info("Starting validation and processing...")
    results = ValidationResults()
    
    entries = data.get("data", [])
    if args.limit:
        entries = entries[:args.limit]
        logger.info(f"Limiting processing to first {args.limit} entries")
    
    processed_entries_by_index: List[Tuple[int, Dict]] = []
    filtered_out_entries: List[Dict] = []

    def process_one(index: int, entry: Dict):
        local_results = ValidationResults()
        filtered_event = None

        if not args.skip_polarization_filter:
            is_polarizing, reasoning = assess_event_polarization(client, entry)
            if not is_polarizing:
                local_results.stats["non_polarizing_events"] += 1

                topic_name = "Unknown"
                if "en" in entry:
                    topic_name = entry["en"].get("topic_name", "Unknown")
                else:
                    for lang in SUPPORTED_LANGUAGES:
                        if lang in entry:
                            topic_name = entry[lang].get("topic_name", "Unknown")
                            break

                filtered_event = {
                    "entry_index": index,
                    "topic_name": topic_name,
                    "reasoning": reasoning
                }
                return index, None, filtered_event, local_results

        validate_entry(entry, index, local_results)

        fixed_entry = entry.copy()
        if not args.validation_only:
            fixed_entry = fix_country_names(fixed_entry)
            fixed_entry = fix_entry_translations(fixed_entry, client, local_results)

        return index, fixed_entry, None, local_results

    logger.info(f"Processing with {args.workers} threads...")
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_one, i, entry): i for i, entry in enumerate(entries)}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Validating entries"):
            index, fixed_entry, filtered_event, local_results = future.result()

            # Aggregate stats
            for key, value in local_results.stats.items():
                results.stats[key] += value
            # Aggregate issues
            results.issues.extend(local_results.issues)

            if filtered_event is not None:
                filtered_out_entries.append(filtered_event)
            elif fixed_entry is not None:
                processed_entries_by_index.append((index, fixed_entry))

    # Preserve original order among kept entries
    processed_entries_by_index.sort(key=lambda x: x[0])
    processed_entries = [e for _, e in processed_entries_by_index]
    
    # Update data with processed entries
    if args.output:
        data["data"] = processed_entries
    
    results.print_summary()
    
    # Save validation report
    if args.report:
        logger.info(f"Saving validation report to {args.report}")
        report_data = {
            "stats": results.stats,
            "issues": results.issues
        }
        
        # Add filtering information if applicable
        if not args.skip_polarization_filter:
            report_data["filtered_events"] = filtered_out_entries
        
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    # Save processed data if requested
    if args.output:
        logger.info(f"Saving processed data to {args.output}")
        logger.info(f"Original entries: {len(entries)}, Processed entries: {len(processed_entries)}")
        if filtered_out_entries:
            logger.info(f"Filtered out {len(filtered_out_entries)} non-polarizing events")
        
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Print sample issues
    if results.issues:
        logger.info("\nFirst 10 validation issues:")
        for issue in results.issues[:10]:
            logger.info(f"  {issue['type']}: Entry {issue['entry_index']}, "
                       f"{issue['language']}.{issue['field']} - {issue['details']}")
    
    # Print sample filtered events
    if filtered_out_entries:
        logger.info(f"\nFirst 5 filtered out events:")
        for event in filtered_out_entries[:5]:
            logger.info(f"  Entry {event['entry_index']}: {event['topic_name']} - {event['reasoning']}")


if __name__ == "__main__":
    main()
