#!/usr/bin/env python3
import json
import re
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict

# Canonical country names for each language
CANONICAL_NAMES = {
    'en': {
        'USA': 'USA',
        'UK': 'UK', 
        'USSR': 'USSR',
        'China': 'China'
    },
    'ar': {
        'USA': 'الولايات المتحدة',
        'UK': 'المملكة المتحدة',
        'USSR': 'الاتحاد السوفيتي', 
        'China': 'الصين'
    },
    'fr': {
        'USA': 'États-Unis',
        'UK': 'Royaume-Uni',
        'USSR': 'URSS',
        'China': 'Chine'
    },
    'he': {
        'USA': 'ארצות הברית',
        'UK': 'בריטניה',
        'USSR': 'ברית המועצות',
        'China': 'סין'
    },
    'ru': {
        'USA': 'США',
        'UK': 'Великобритания', 
        'USSR': 'СССР',
        'China': 'Китай'
    },
    'zh': {
        'USA': '美国',
        'UK': '英国',
        'USSR': '苏联',
        'China': '中国'
    },
    'de': {
        'USA': 'USA',
        'UK': 'Vereinigtes Königreich',
        'USSR': 'UdSSR',
        'China': 'China'
    }
}

# Country name mapping dictionaries for normalization
COUNTRY_MAPPINGS = {
    'en': {
        # USA variations
        'US': 'USA', 'USA': 'USA', 'usa': 'USA', 'Us': 'USA',
        'United States': 'USA', 'United States of America': 'USA',
        'America': 'USA', 'U.S.': 'USA', 'U.S.A.': 'USA',
        
        # UK variations  
        'UK': 'UK', 'uk': 'UK', 'Uk': 'UK',
        'United Kingdom': 'UK', 'Britain': 'UK', 'Great Britain': 'UK',
        'British Empire': 'UK', 'England': 'UK', 'U.K.': 'UK',
        
        # USSR variations
        'USSR': 'USSR', 'ussr': 'USSR', 'Ussr': 'USSR',
        'Soviet Union': 'USSR', 'Russia': 'USSR', 'russia': 'USSR',
        'Russian Empire': 'USSR', 'Soviet Russia': 'USSR', 'U.S.S.R.': 'USSR',
        'Russian Federation': 'USSR', 'Russian SFSR': 'USSR',
        
        # China variations
        'China': 'China', 'CHINA': 'China', 'china': 'China',
        'People\'s Republic of China': 'China', 'PRC': 'China',
        'Chinese Empire': 'China', 'Republic of China': 'China'
    },
    'ar': {
        # English words that might appear in Arabic sections
        'USA': 'الولايات المتحدة', 'UK': 'المملكة المتحدة', 'USSR': 'الاتحاد السوفيتي', 
        'China': 'الصين', 'CHINA': 'الصين',
        
        # USA variations
        'أمريكا': 'الولايات المتحدة', 'الولايات المتحدة الأمريكية': 'الولايات المتحدة',
        'الولايات المتحدة': 'الولايات المتحدة', 'أميركا': 'الولايات المتحدة',
        
        # UK variations
        'المملكة المتحدة': 'المملكة المتحدة', 'بريطانيا': 'المملكة المتحدة', 
        'بريطانيا العظمى': 'المملكة المتحدة', 'الإمبراطورية البريطانية': 'المملكة المتحدة',
        'إنجلترا': 'المملكة المتحدة',
        
        # USSR variations  
        'الاتحاد السوفيتي': 'الاتحاد السوفيتي', 'الاتحاد السوفييتي': 'الاتحاد السوفيتي',
        'روسيا': 'الاتحاد السوفيتي', 'الإمبراطورية الروسية': 'الاتحاد السوفيتي',
        'روسيا السوفيتية': 'الاتحاد السوفيتي',
        
        # China variations
        'الصين': 'الصين', 'جمهورية الصين الشعبية': 'الصين', 'الإمبراطورية الصينية': 'الصين'
    },
    'fr': {
        # English words that might appear in French sections
        'USA': 'États-Unis', 'UK': 'Royaume-Uni', 'USSR': 'URSS', 
        'China': 'Chine', 'CHINA': 'Chine',
        
        # USA variations
        'États-Unis': 'États-Unis', 'Etats-Unis': 'États-Unis',
        'Amérique': 'États-Unis', 'États-Unis d\'Amérique': 'États-Unis',
        
        # UK variations
        'Royaume-Uni': 'Royaume-Uni', 'Grande-Bretagne': 'Royaume-Uni',
        'Angleterre': 'Royaume-Uni', 'Empire britannique': 'Royaume-Uni',
        
        # USSR variations
        'URSS': 'URSS', 'Union soviétique': 'URSS', 'Russie': 'URSS',
        'Empire russe': 'URSS', 'Russie soviétique': 'URSS',
        
        # China variations  
        'Chine': 'Chine', 'République populaire de Chine': 'Chine',
        'Empire chinois': 'Chine'
    },
    'he': {
        # English words that might appear in Hebrew sections
        'USA': 'ארצות הברית', 'UK': 'בריטניה', 'USSR': 'ברית המועצות', 
        'China': 'סין', 'CHINA': 'סין',
        
        # USA variations
        'ארצות הברית': 'ארצות הברית', 'אמריקה': 'ארצות הברית', 'ארה״ב': 'ארצות הברית',
        
        # UK variations
        'בריטניה': 'בריטניה', 'אנגליה': 'בריטניה', 'הממלכה המאוחדת': 'בריטניה',
        'הממלכה הבריטית': 'בריטניה',
        
        # USSR variations
        'ברית המועצות': 'ברית המועצות', 'רוסיה': 'ברית המועצות',
        'ברה״מ': 'ברית המועצות', 'האימפריה הרוסית': 'ברית המועצות',
        
        # China variations
        'סין': 'סין', 'רפובליקה העממית של סין': 'סין', 'האימפריה הסינית': 'סין'
    },
    'ru': {
        # English words that might appear in Russian sections
        'USA': 'США', 'UK': 'Великобритания', 'USSR': 'СССР', 
        'China': 'Китай', 'CHINA': 'Китай',
        
        # USA variations
        'США': 'США', 'Соединенные Штаты': 'США', 'Америка': 'США',
        'Соединенные Штаты Америки': 'США',
        
        # UK variations
        'Великобритания': 'Великобритания', 'Англия': 'Великобритания',
        'Соединенное Королевство': 'Великобритания', 'Британская империя': 'Великобритания',
        'Британия': 'Великобритания',
        
        # USSR variations
        'СССР': 'СССР', 'Советский Союз': 'СССР', 'Россия': 'СССР',
        'Российская империя': 'СССР', 'Советская Россия': 'СССР',
        'Российская Федерация': 'СССР',
        
        # China variations
        'Китай': 'Китай', 'Китайская Народная Республика': 'Китай',
        'КНР': 'Китай', 'Китайская империя': 'Китай'
    },
    'zh': {
        # English words that might appear in Chinese sections
        'USA': '美国', 'UK': '英国', 'USSR': '苏联', 
        'China': '中国', 'CHINA': '中国',
        
        # USA variations
        '美国': '美国', '美利坚合众国': '美国', '美利坚': '美国', '美': '美国',
        
        # UK variations  
        '英国': '英国', '大不列颠': '英国', '英格兰': '英国', 
        '大英帝国': '英国', '联合王国': '英国',
        
        # USSR variations
        '苏联': '苏联', '苏维埃联盟': '苏联', '俄国': '苏联', 
        '俄罗斯帝国': '苏联', '苏俄': '苏联', '俄罗斯': '苏联',
        
        # China variations
        '中国': '中国', '中华人民共和国': '中国', '中华民国': '中国',
        '中华帝国': '中国', '华': '中国'
    },
    'de': {
        # English words that might appear in German sections
        'USA': 'USA', 'UK': 'Vereinigtes Königreich', 'USSR': 'UdSSR', 
        'China': 'China', 'CHINA': 'China',
        
        # USA variations
        'Vereinigte Staaten': 'USA', 'Amerika': 'USA',
        'Vereinigte Staaten von Amerika': 'USA', 'U.S.A.': 'USA',
        
        # UK variations
        'Vereinigtes Königreich': 'Vereinigtes Königreich', 'Großbritannien': 'Vereinigtes Königreich',
        'England': 'Vereinigtes Königreich', 'Britisches Empire': 'Vereinigtes Königreich',
        'Britannien': 'Vereinigtes Königreich',
        
        # USSR variations
        'UdSSR': 'UdSSR', 'Sowjetunion': 'UdSSR', 'Russland': 'UdSSR',
        'Russisches Reich': 'UdSSR', 'Sowjetrussland': 'UdSSR',
        
        # China variations
        'Volksrepublik China': 'China', 'Chinesisches Reich': 'China'
    }
}

def normalize_country_name(country: str, language: str) -> str:
    """Normalize a country name to its canonical form for the given language."""
    if not country or not isinstance(country, str):
        return country
    
    country = country.strip()
    if not country:
        return country
        
    # Get the mapping for this language
    mapping = COUNTRY_MAPPINGS.get(language, {})
    
    # Try exact match first
    if country in mapping:
        return mapping[country]
    
    # Try case-insensitive match for Latin scripts
    if language in ['en', 'fr', 'de']:
        for variant, canonical in mapping.items():
            if country.lower() == variant.lower():
                return canonical
    
    # Return original if no mapping found
    return country

def extract_years_from_string(year_str: str) -> List[int]:
    """Extract all years from a year string (handles ranges like '1918‑1922')."""
    # Remove common non-digit characters and replace various dash types
    cleaned = re.sub(r'[‑–—-]', '-', year_str)
    # Find all 4-digit numbers that look like years
    years = re.findall(r'\b(1[0-9]{3}|20[0-9]{2})\b', cleaned)
    return [int(year) for year in years]

def is_valid_year_range(year_str: str, min_year: int = 1850, max_year: int = 2010) -> bool:
    """Check if all years in the string are within the valid range."""
    if not year_str or not isinstance(year_str, str):
        return False
    
    years = extract_years_from_string(year_str)
    if not years:
        return False
    
    return all(min_year <= year <= max_year for year in years)

def is_wikipedia_service_page(text: str) -> bool:
    """Check if text starts with or contains Wikipedia service page prefixes."""
    if not text or not isinstance(text, str):
        return False
    
    service_prefixes = [
        'Category:', 'Portal:', 'Talk:', 'File:', 'Template:', 
        'User:', 'Wikipedia:', 'Help:', 'Special:', 'Draft:', 
        'Project:', 'Media:', 'MediaWiki:'
    ]
    
    # Check if the text starts with a prefix (for topic_name, seed_name)
    if any(text.lower().startswith(prefix.lower()) for prefix in service_prefixes):
        return True
        
    # Check if the text is a URL containing a service page prefix
    if "wikipedia.org" in text.lower():
        if any(f"/wiki/{prefix.lower()}" in text.lower() for prefix in service_prefixes):
            return True

    return False

def is_disambiguation_page(entry: Dict[str, Any]) -> bool:
    """Check if entry appears to be a disambiguation page."""
    # Check topic_name, seed_name, topic_description for disambiguation indicators
    fields_to_check = []
    
    for lang_data in entry.values():
        if isinstance(lang_data, dict):
            fields_to_check.extend([
                lang_data.get('topic_name', ''),
                lang_data.get('seed_name', ''),
                lang_data.get('topic_description', ''),
                lang_data.get('paragraph_anchor_or_comment', '')
            ])
    
    disambiguation_indicators = [
        'disambiguation', 'disambig', 'Disambiguation', 'DISAMBIGUATION'
    ]
    
    text_to_check = ' '.join(str(field) for field in fields_to_check)
    return any(indicator in text_to_check for indicator in disambiguation_indicators)

def has_severely_corrupted_text(text: str) -> bool:
    """Check if text contains severely corrupted characters or suspicious patterns."""
    if not text or not isinstance(text, str):
        return False
    
    # Only flag truly problematic corruption patterns
    severe_corruption_patterns = [
        r'[�￿]',   # Replacement characters
        r'[a-zA-Z0-9]{100,}',  # Extremely long sequences without spaces
        r'\\x[0-9a-fA-F]{2}',  # Hex escape sequences
        r'SulIlJ[^a-zA-Z]*zo\+.*→ǵ',  # Specific garbage pattern seen in data
        r'SC-G ABCDFChicytic',  # Another specific garbage pattern
        r'}\s*End of translation\.\s*\(No additional commentary\.\)',  # AI model output artifacts
        r'}\s*(please disregard|the answer strictly follows|no extra output|finished|EOF)',  # More AI artifacts
        r'​}​}​}​}​}​}',  # Repeated Unicode characters (5+ times)
        r'[^\w\s\-–—‑.,!?;:()\[\]{}\'\"]{20,}',  # 20+ consecutive special chars
    ]
    
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in severe_corruption_patterns)

def is_entry_corrupted(entry: Dict[str, Any]) -> bool:
    """Check if any part of the entry appears corrupted."""
    for lang_data in entry.values():
        if isinstance(lang_data, dict):
            fields_to_check = [
                lang_data.get('topic_name', ''),
                lang_data.get('topic_description', ''),
            ]
            
            if any(has_severely_corrupted_text(str(field)) for field in fields_to_check):
                return True
    
    return False

def is_entry_valid(entry: Dict[str, Any]) -> bool:
    """Check if entry has valid structure and required fields."""
    if not isinstance(entry, dict):
        return False
    
    # Check if entry has at least one language section
    has_valid_lang_section = False
    
    for key, value in entry.items():
        if isinstance(value, dict) and len(key) <= 3:  # Language codes are short
            # Check for required fields
            if all(field in value for field in ['topic_name', 'seed_name', 'years']):
                has_valid_lang_section = True
                break
    
    return has_valid_lang_section

def should_remove_entry(entry: Dict[str, Any]) -> tuple[bool, str]:
    """
    Determine if an entry should be removed and return reason.
    Returns (should_remove, reason)
    """
    # Check basic validity
    if not is_entry_valid(entry):
        return True, "invalid_structure"
    
    # Check for corruption
    if is_entry_corrupted(entry):
        return True, "corrupted_text"
    
    # Check for disambiguation pages
    if is_disambiguation_page(entry):
        return True, "disambiguation_page"
    
    # Check each language section
    for lang_data in entry.values():
        if isinstance(lang_data, dict):
            # Check Wikipedia service pages
            topic_name = lang_data.get('topic_name', '')
            seed_name = lang_data.get('seed_name', '')
            topic_url = lang_data.get('topic_url', '')

            if (is_wikipedia_service_page(topic_name) or
                    is_wikipedia_service_page(seed_name) or
                    is_wikipedia_service_page(topic_url)):
                return True, "wikipedia_service_page"
            
            # Check year validity
            years = lang_data.get('years', '')
            if not is_valid_year_range(years):
                return True, "invalid_year_range"
    
    return False, ""

def extract_country_pairs(entry: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Extract normalized country pairs from an entry using all language data."""
    # Collect all countries from all language sections and normalize to English canonical forms
    canonical_countries = set()
    
    # Available languages in the dataset
    languages = ['ar', 'en', 'fr', 'he', 'ru', 'zh', 'de']
    
    for lang in languages:
        lang_data = entry.get(lang, {})
        if not isinstance(lang_data, dict):
            continue
            
        countries = lang_data.get('countries', [])
        if not isinstance(countries, list):
            continue
            
        for country in countries:
            if country and isinstance(country, str):
                country = country.strip()
                if not country:
                    continue
                    
                # Normalize the country name using the language mapping
                normalized = normalize_country_name(country, lang)
                
                
                # For English, the normalized name is already in the correct canonical form
                # For other languages, try to convert to English canonical form
                if lang == 'en':
                    # For English, just use the normalized name directly
                    canonical_countries.add(normalized)
                else:
                    # For other languages, try to map to English canonical form
                    mapped_to_english = False
                    for canonical_key, canonical_value in CANONICAL_NAMES[lang].items():
                        if normalized == canonical_value:
                            canonical_countries.add(CANONICAL_NAMES['en'][canonical_key])
                            mapped_to_english = True
                            break
                    
                    # If no mapping found, keep the normalized name
                    if not mapped_to_english:
                        canonical_countries.add(normalized)
    
    # Convert to list and ensure we have at least 2 countries
    countries_list = list(canonical_countries)
    if len(countries_list) < 2:
        return []
    
    # Debug: print countries for first few entries to see what's happening
    # Uncomment next line to debug specific entries
    
    # Generate all unique pairs from the normalized countries
    country_pairs = []
    for i in range(len(countries_list)):
        for j in range(i + 1, len(countries_list)):
            country1 = countries_list[i]
            country2 = countries_list[j]
            # Sort alphabetically to ensure consistent ordering
            pair = tuple(sorted([country1, country2]))
            country_pairs.append(pair)
    
    return country_pairs

def collect_country_pair_statistics(entries: List[Dict[str, Any]]) -> Counter:
    """Collect statistics for all country pairs in the dataset."""
    pair_counter = Counter()
    
    for entry in entries:
        pairs = extract_country_pairs(entry)
        for pair in pairs:
            pair_counter[pair] += 1
    
    return pair_counter

def print_country_pair_statistics(stats: Counter, title: str, top_n: int = 20):
    """Print formatted country pair statistics."""
    print(f"\n{title}")
    print("=" * len(title))
    
    if not stats:
        print("No country pairs found.")
        return
    
    total_pairs = sum(stats.values())
    unique_pairs = len(stats)
    
    print(f"Total entries with country pairs: {total_pairs:,}")
    print(f"Unique country pairs: {unique_pairs:,}")
    print(f"\nTop {min(top_n, len(stats))} most frequent country pairs:")
    print("-" * 60)
    
    for i, (pair, count) in enumerate(stats.most_common(top_n), 1):
        country1, country2 = pair
        percentage = (count / total_pairs) * 100
        print(f"{i:2d}. {country1} - {country2}: {count:,} ({percentage:.1f}%)")
    
    if len(stats) > top_n:
        remaining_count = sum(count for _, count in stats.most_common()[top_n:])
        remaining_pairs = len(stats) - top_n
        print(f"    ... and {remaining_pairs:,} more pairs ({remaining_count:,} entries)")
    print()

def print_corrupted_examples(examples: List[Dict[str, Any]]):
    """Print examples of corrupted text entries that were removed."""
    if not examples:
        print("No corrupted text examples found.")
        return
    
    print("\n" + "="*60)
    print("EXAMPLES OF CORRUPTED TEXT ENTRIES (REMOVED)")
    print("="*60)
    print(f"Showing {len(examples)} examples:")
    print()
    
    for i, entry in enumerate(examples, 1):
        print(f"Example {i}:")
        print("-" * 30)
        
        # Show corrupted fields from different languages
        found_corruption = False
        for lang in ['ar', 'en', 'fr', 'he', 'ru', 'zh', 'de']:
            lang_data = entry.get(lang, {})
            if isinstance(lang_data, dict):
                topic_name = lang_data.get('topic_name', '')
                topic_description = lang_data.get('topic_description', '')
                
                # Check if any of these fields are corrupted and show them
                for field_name, field_value in [('topic_name', topic_name), ('topic_description', topic_description)]:
                    if field_value and has_severely_corrupted_text(str(field_value)):
                        print(f"  Language: {lang}")
                        print(f"  Field: {field_name}")
                        # Truncate very long corrupted text for readability
                        display_text = str(field_value)[:200] + "..." if len(str(field_value)) > 200 else str(field_value)
                        print(f"  Corrupted text: {repr(display_text)}")
                        found_corruption = True
                        break
            
            if found_corruption:
                break
        
        if not found_corruption:
            print("  No specific corruption pattern identified in displayed fields")
        
        print()

def clean_dataset(input_file: str, output_file: str) -> Dict[str, int]:
    """Clean the dataset and return statistics."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'data' not in data:
        raise ValueError("Dataset must have 'data' field")
    
    original_entries = data['data']
    original_count = len(original_entries)
    
    # Collect country pair statistics BEFORE cleaning
    print("Collecting country pair statistics...")
    original_country_stats = collect_country_pair_statistics(original_entries)
    print_country_pair_statistics(original_country_stats, "COUNTRY PAIR STATISTICS - BEFORE CLEANING")
    
    removal_stats = {
        'invalid_structure': 0,
        'corrupted_text': 0,
        'disambiguation_page': 0,
        'wikipedia_service_page': 0,
        'invalid_year_range': 0,
    }
    
    # Collect examples of corrupted entries
    corrupted_examples = []
    
    cleaned_entries = []
    
    for entry in original_entries:
        should_remove, reason = should_remove_entry(entry)
        
        if should_remove:
            removal_stats[reason] += 1
            
            # Collect examples of corrupted text
            if reason == 'corrupted_text' and len(corrupted_examples) < 20:
                corrupted_examples.append(entry)
        else:
            cleaned_entries.append(entry)
    
    # Collect country pair statistics AFTER cleaning
    cleaned_country_stats = collect_country_pair_statistics(cleaned_entries)
    print_country_pair_statistics(cleaned_country_stats, "COUNTRY PAIR STATISTICS - AFTER CLEANING")
    
    # Compare statistics
    print("\nCOMPARISON OF COUNTRY PAIR STATISTICS")
    print("=" * 40)
    print(f"Original unique pairs: {len(original_country_stats):,}")
    print(f"Cleaned unique pairs: {len(cleaned_country_stats):,}")
    print(f"Pairs removed: {len(original_country_stats) - len(cleaned_country_stats):,}")
    
    original_total = sum(original_country_stats.values())
    cleaned_total = sum(cleaned_country_stats.values())
    print(f"Original total entries with pairs: {original_total:,}")
    print(f"Cleaned total entries with pairs: {cleaned_total:,}")
    print(f"Pair entries removed: {original_total - cleaned_total:,}")
    
    if original_total > 0:
        retention_rate = (cleaned_total / original_total) * 100
        print(f"Pair retention rate: {retention_rate:.1f}%")
    
    # Print examples of corrupted text entries
    print_corrupted_examples(corrupted_examples)
    
    # Update the dataset
    data['data'] = cleaned_entries
    
    # Write cleaned dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Return statistics
    stats = {
        'original_count': original_count,
        'cleaned_count': len(cleaned_entries),
        'removed_count': original_count - len(cleaned_entries),
        **removal_stats
    }
    
    return stats

def main():
    input_file = "data2/final_dataset_propaganda_translated.json"
    output_file = "data2/final_dataset_propaganda_translated_cleaned.json"
    
    print("Cleaning dataset...")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print()
    
    try:
        stats = clean_dataset(input_file, output_file)
        
        print("\n" + "="*50)
        print("DATASET CLEANING SUMMARY")
        print("="*50)
        print(f"Original entries: {stats['original_count']:,}")
        print(f"Cleaned entries: {stats['cleaned_count']:,}")
        print(f"Removed entries: {stats['removed_count']:,}")
        print(f"Removal rate: {stats['removed_count']/stats['original_count']*100:.1f}%")
        print()
        print("Removal breakdown:")
        for reason, count in stats.items():
            if reason.endswith('_count'):
                continue
            print(f"  {reason}: {count:,}")
        print("\nCleaning completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
