from ast import Pass
import json
import requests
import time
import re
from typing import Dict, List, Optional, Tuple
import sys
from urllib.parse import unquote, quote
import argparse
import copy
from rich.progress import Progress, TaskID, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.console import Console
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading



# Language mapping for Hunyuan-MT-7B supported languages
LANGUAGE_NAMES = {
    'zh': 'Chinese',
    'en': 'English', 
    'fr': 'French',
    'pt': 'Portuguese',
    'es': 'Spanish',
    'ja': 'Japanese',
    'tr': 'Turkish',
    'ru': 'Russian',
    'ar': 'Arabic',
    'ko': 'Korean',
    'th': 'Thai',
    'it': 'Italian',
    'de': 'German',
    'vi': 'Vietnamese',
    'ms': 'Malay',
    'id': 'Indonesian',
    'tl': 'Filipino',
    'hi': 'Hindi',
    'zh-hant': 'Traditional Chinese',
    'pl': 'Polish',
    'cs': 'Czech',
    'nl': 'Dutch',
    'km': 'Khmer',
    'my': 'Burmese',
    'fa': 'Persian',
    'gu': 'Gujarati',
    'ur': 'Urdu',
    'te': 'Telugu',
    'mr': 'Marathi',
    'he': 'Hebrew',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'uk': 'Ukrainian',
    'bo': 'Tibetan',
    'kk': 'Kazakh',
    'mn': 'Mongolian',
    'ug': 'Uyghur',
    'yue': 'Cantonese'
}

# Set seed for consistent language detection
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """Detect the language of the given text."""
    if not text or not text.strip():
        return 'en'  # Default to English for empty text
    
    try:
        detected_lang = detect(text)
        # Map detected language to Hunyuan-MT-7B supported language codes
        lang_mapping = {
            'zh-cn': 'zh',  # Simplified Chinese
            'zh-tw': 'zh-hant',  # Traditional Chinese
            'ko': 'ko',
            'ja': 'ja',
            'ar': 'ar',
            'he': 'he',
            'ru': 'ru',
            'fr': 'fr',
            'de': 'de',
            'es': 'es',
            'it': 'it',
            'pt': 'pt',
            'nl': 'nl',
            'pl': 'pl',
            'cs': 'cs',
            'tr': 'tr',
            'th': 'th',
            'vi': 'vi',
            'hi': 'hi',
            'bn': 'bn',
            'ta': 'ta',
            'te': 'te',
            'gu': 'gu',
            'mr': 'mr',
            'ur': 'ur',
            'fa': 'fa',
            'uk': 'uk',
            'ms': 'ms',
            'id': 'id',
            'tl': 'tl'
        }
        
        return lang_mapping.get(detected_lang, 'en')  # Default to English if not supported
        
    except LangDetectException:
        return 'en'  # Default to English on detection error


def get_translation_prompt(source_text: str, target_lang: str, source_lang: str = 'en') -> str:
    """Get the appropriate translation prompt based on language pair."""
    target_language = LANGUAGE_NAMES.get(target_lang, target_lang)
    
    # For Chinese <=> other language translations
    if source_lang == 'zh' or target_lang == 'zh':
        return f"把下面的文本翻译成{target_language}，不要额外解释。\n\n{source_text}"
    else:
        # For other language pairs (excluding Chinese)
        return f"Translate the following segment into {target_language}, without additional explanation.\n\n{source_text}"


def translate_single_text(text: str, target_lang: str, api_url: str) -> str:
    """Translate a single text and return (position, translated_text, success)."""
    
    try:
        # Detect source language for this specific text
        source_lang = detect_language(text)
        prompt = get_translation_prompt(text, target_lang, source_lang)
        
        # Format message for vLLM chat completion API
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        data = {
            "model": "tencent/Hunyuan-MT-7B",
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.6,
            "repetition_penalty": 1.05,
            "top_k": 20
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{api_url}/v1/chat/completions", 
                               headers=headers, json=data, timeout=180)
        response.raise_for_status()
        
        response_data = response.json()
        translated_text = response_data["choices"][0]["message"]["content"].strip()
        
        return translated_text
        
    except requests.exceptions.RequestException as e:
        print(f"Translation error for text '{text[:50]}...': {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing response for text '{text[:50]}...': {e}")
        return None



def get_wikipedia_url_for_language(url: str, target_lang: str) -> str:
    """Try to find Wikipedia page in target language."""
    # Extract article name from URL
    match = re.search(r'wikipedia\.org/wiki/(.+)$', url)
    if not match:
        return url
    
    article_name = unquote(match.group(1))
    
    # Check if URL already in target language
    if f'{target_lang}.wikipedia.org' in url:
        return url
    
    # Extract source language from URL
    source_lang_match = re.search(r'https://(\w+)\.wikipedia\.org', url)
    source_lang = source_lang_match.group(1) if source_lang_match else 'en'
    
    # Use Wikipedia API to get language links
    api_url = f"https://{source_lang}.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'prop': 'langlinks',
        'titles': article_name,
        'lllang': target_lang,
        'format': 'json',
        'lllimit': '500'
    }
    
    # Add User-Agent header to avoid 403 errors
    headers = {
        'User-Agent': 'DatasetTranslationBot/1.0 (https://example.com/contact)'
    }
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            langlinks = page_data.get('langlinks', [])
            for link in langlinks:
                if link.get('lang') == target_lang:
                    # Return the Wikipedia URL in target language
                    return f"https://{target_lang}.wikipedia.org/wiki/{quote(link['*'])}"
        
        # If not found in target language, return English version
        return f"https://en.wikipedia.org/wiki/{quote(article_name)}"
        
    except Exception as e:
        print(f"Error getting Wikipedia URL for {target_lang}: {e}")
        # Return English version as fallback
        return f"https://en.wikipedia.org/wiki/{quote(article_name)}"



def translate_item_for_language(item: Dict, lang: str, api_url: str, progress: Progress, task_id: TaskID) -> Tuple[str, Dict]:
    """Translate a single item to one target language."""
    # Deep copy the original item structure
    translated_item = copy.deepcopy(item)
    
    # Translate seed_name
    if 'seed_name' in item:
        translated_seed_name = translate_single_text(item['seed_name'], lang, api_url)
        if translated_seed_name:
            translated_item['seed_name'] = translated_seed_name
    
    # Convert topic_url to target language
    if 'topic_url' in item:
        translated_item['topic_url'] = get_wikipedia_url_for_language(item['topic_url'], lang)
    
    # Translate topic_name
    if 'topic_name' in item:
        translated_topic_name = translate_single_text(item['topic_name'], lang, api_url)
        if translated_topic_name:
            translated_item['topic_name'] = translated_topic_name
    
    # Translate topic_description
    if 'topic_description' in item:
        translated_description = translate_single_text(item['topic_description'], lang, api_url)
        if translated_description:
            translated_item['topic_description'] = translated_description
    
    # Translate viewpoints.neutral.description
    if ('viewpoints' in item and 
        'neutral' in item['viewpoints'] and 
        'description' in item['viewpoints']['neutral']):
        translated_neutral_desc = translate_single_text(
            item['viewpoints']['neutral']['description'], lang, api_url
        )
        if translated_neutral_desc:
            translated_item['viewpoints']['neutral']['description'] = translated_neutral_desc
    
    # Translate propaganda items
    if ('viewpoints' in item and 
        'propaganda' in item['viewpoints']):
        for i, prop_item in enumerate(item['viewpoints']['propaganda']):
            # Translate position
            if 'position' in prop_item:
                translated_position = translate_single_text(prop_item['position'], lang, api_url)
                if translated_position:
                    translated_item['viewpoints']['propaganda'][i]['position'] = translated_position
            
            # Translate description
            if 'description' in prop_item:
                translated_prop_desc = translate_single_text(prop_item['description'], lang, api_url)
                if translated_prop_desc:
                    translated_item['viewpoints']['propaganda'][i]['description'] = translated_prop_desc
            
            # Translate why_biased
            if 'why_biased' in prop_item:
                translated_why_biased = translate_single_text(prop_item['why_biased'], lang, api_url)
                if translated_why_biased:
                    translated_item['viewpoints']['propaganda'][i]['why_biased'] = translated_why_biased
    
    # Update progress after completing translations for this language
    progress.update(task_id, advance=1)
    
    return lang, translated_item


def translate_item(item: Dict, target_langs: List[str], api_url: str, progress: Progress, task_id: TaskID) -> Dict[str, Dict]:
    """Translate a single item to all target languages using parallel processing."""
    result = {}
    
    # Use ThreadPoolExecutor to process languages in parallel
    with ThreadPoolExecutor(max_workers=min(len(target_langs), 8)) as executor:
        # Submit all translation tasks
        future_to_lang = {
            executor.submit(translate_item_for_language, item, lang, api_url, progress, task_id): lang
            for lang in target_langs
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_lang):
            try:
                lang, translated_item = future.result()
                result[lang] = translated_item
            except Exception as e:
                lang = future_to_lang[future]
                print(f"Translation failed for language {lang}: {e}")
                # Use original item as fallback
                result[lang] = copy.deepcopy(item)
    
    return result



def main():
    console = Console()
    
    parser = argparse.ArgumentParser(description='Translate dataset to multiple languages')
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('output_file', help='Output JSON file path')
    parser.add_argument('--api-url', default='http://localhost:8000', 
                       help='Local vLLM API URL (default: http://localhost:8000)')
    parser.add_argument('--languages', nargs='+', 
                       default=['ar', 'en', 'fr', 'he', 'ru', 'zh'],
                       help='Target languages (default: ar en fr he ru zh)')
    
    args = parser.parse_args()
    
    # Load input data
    console.print(f"[cyan]📂 Loading data from[/cyan] [yellow]{args.input_file}[/yellow]...")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare output structure
    output_data = {
        'llm': data.get('llm', ''),
        'languages': args.languages,
        'start_year': data.get('start_year', 0),
        'end_year': data.get('end_year', 0),
        'data': []
    }
    
    # Process each item with detailed progress
    total_items = len(data.get('data', []))
    total_translations = total_items * len(args.languages)
    
    console.print(f"[green]📊 Starting translation:[/green] {total_items} items × {len(args.languages)} languages = {total_translations} total translations")
    
    with Progress(
        TextColumn("[bold blue]Progress"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        TextColumn("•"),
        TextColumn("{task.description}"),
        console=console,
        expand=True
    ) as progress:
        
        task = progress.add_task("Starting...", total=total_translations)
        
        for i, item in enumerate(data.get('data', [])):
            item_name = item.get('seed_name', 'Unknown')[:25]
            if len(item.get('seed_name', '')) > 25:
                item_name += "..."
            
            progress.update(task, description=f"[cyan]Item {i+1}/{total_items}:[/cyan] [yellow]{item_name}[/yellow]")
            
            translated_items = translate_item(item, args.languages, args.api_url, progress, task)
            output_data['data'].append(translated_items)

    
    # Save output
    console.print(f"\n[cyan]💾 Saving translated data to[/cyan] [yellow]{args.output_file}[/yellow]...")
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    console.print("[green]✅ Translation completed![/green]")


if __name__ == "__main__":
    main()
