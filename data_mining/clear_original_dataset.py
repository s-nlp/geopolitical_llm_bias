#!/usr/bin/env python3
import json
import re
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict

# Canonical country names for normalization
CANONICAL_NAMES = {
    'USA': 'USA',
    'UK': 'UK', 
    'USSR': 'USSR',
    'China': 'China'
}

# Country name mapping dictionary for normalization
COUNTRY_MAPPINGS = {
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
}

def normalize_country_name(country: str) -> str:
    """Normalize a country name to its canonical form."""
    if not country or not isinstance(country, str):
        return country
    
    country = country.strip()
    if not country:
        return country
        
    # Try exact match first
    if country in COUNTRY_MAPPINGS:
        return COUNTRY_MAPPINGS[country]
    
    # Try case-insensitive match
    for variant, canonical in COUNTRY_MAPPINGS.items():
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

def is_valid_year_range(year_str: str, min_year: int = 1800, max_year: int = 2010) -> bool:
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
    fields_to_check = [
        entry.get('topic_name', ''),
        entry.get('seed_name', ''),
        entry.get('topic_description', ''),
    ]
    
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
        r'[￿]',   # Replacement characters
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
    fields_to_check = [
        entry.get('topic_name', ''),
        entry.get('topic_description', ''),
    ]
    
    # Check viewpoints section
    viewpoints = entry.get('viewpoints', {})
    if isinstance(viewpoints, dict):
        neutral = viewpoints.get('neutral', {})
        if isinstance(neutral, dict):
            fields_to_check.append(neutral.get('description', ''))
        
        perspectives = viewpoints.get('perspectives', [])
        if isinstance(perspectives, list):
            for perspective in perspectives:
                if isinstance(perspective, dict):
                    key_points = perspective.get('key_points', [])
                    if isinstance(key_points, list):
                        for point in key_points:
                            if isinstance(point, str):
                                fields_to_check.append(point)
    
    return any(has_severely_corrupted_text(str(field)) for field in fields_to_check)

def is_entry_valid(entry: Dict[str, Any]) -> bool:
    """Check if entry has valid structure and required fields."""
    if not isinstance(entry, dict):
        return False
    
    # Check for required fields
    required_fields = ['countries', 'seed_name', 'topic_name', 'years', 'topic_description']
    if not all(field in entry for field in required_fields):
        return False
    
    # Check if countries is a non-empty list
    countries = entry.get('countries', [])
    if not isinstance(countries, list) or len(countries) < 2:
        return False
    
    # Check if viewpoints structure is valid
    viewpoints = entry.get('viewpoints', {})
    if not isinstance(viewpoints, dict):
        return False
    
    return True

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
    
    # Check Wikipedia service pages
    topic_name = entry.get('topic_name', '')
    seed_name = entry.get('seed_name', '')
    topic_url = entry.get('topic_url', '')

    if (is_wikipedia_service_page(topic_name) or
            is_wikipedia_service_page(seed_name) or
            is_wikipedia_service_page(topic_url)):
        return True, "wikipedia_service_page"
    
    # Check year validity
    years = entry.get('years', '')
    if not is_valid_year_range(years):
        return True, "invalid_year_range"
    
    return False, ""

def extract_country_pairs(entry: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Extract normalized country pairs from an entry."""
    countries = entry.get('countries', [])
    if not isinstance(countries, list) or len(countries) < 2:
        return []
    
    # Normalize country names
    normalized_countries = []
    for country in countries:
        if country and isinstance(country, str):
            normalized = normalize_country_name(country)
            if normalized:
                normalized_countries.append(normalized)
    
    # Remove duplicates and ensure we have at least 2 countries
    unique_countries = list(set(normalized_countries))
    if len(unique_countries) < 2:
        return []
    
    # Generate all unique pairs from the normalized countries
    country_pairs = []
    for i in range(len(unique_countries)):
        for j in range(i + 1, len(unique_countries)):
            country1 = unique_countries[i]
            country2 = unique_countries[j]
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
        
        # Show corrupted fields
        found_corruption = False
        fields_to_check = [
            ('topic_name', entry.get('topic_name', '')),
            ('topic_description', entry.get('topic_description', '')),
        ]
        
        for field_name, field_value in fields_to_check:
            if field_value and has_severely_corrupted_text(str(field_value)):
                print(f"  Field: {field_name}")
                # Truncate very long corrupted text for readability
                display_text = str(field_value)[:200] + "..." if len(str(field_value)) > 200 else str(field_value)
                print(f"  Corrupted text: {repr(display_text)}")
                found_corruption = True
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
    input_file = "data2/final_dataset_propaganda.json"
    output_file = "data2/final_dataset_propaganda_cleaned.json"
    
    print("Cleaning original dataset...")
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
