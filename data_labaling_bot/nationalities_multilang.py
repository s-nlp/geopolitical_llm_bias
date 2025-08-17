# Multi-language nationality mappings
# Maps nationality names in different languages to canonical English names

from typing import Dict, List, Set, Optional


# Core nationality mappings - canonical English names mapped to translations
NATIONALITY_TRANSLATIONS = {
    # Major nationalities with translations
    "American": {
        "en": ["American", "US American"],
        "ar": ["أمريكي", "أميركي"],
        "fr": ["Américain", "Américaine", "États-Unien", "Étatsunien"],
        "he": ["אמריקאי", "אמריקנית"],
        "ru": ["Американец", "Американка", "Американский"],
        "zh": ["美国人"],
        "de": ["Amerikaner", "Amerikanerin", "US-Amerikaner"],
    },
    "Chinese": {
        "en": ["Chinese"],
        "ar": ["صيني", "صينية"],
        "fr": ["Chinois", "Chinoise"],
        "he": ["סיני", "סינית", "חיני"],
        "ru": ["Китаец", "Китаянка", "Китайский"],
        "zh": ["中国人", "华人"],
        "de": ["Chinese", "Chinesin"],
    },
    "Russian": {
        "en": ["Russian"],
        "ar": ["روسي", "روسية"],
        "fr": ["Russe"],
        "he": ["רוסי", "רוסית"],
        "ru": ["Русский", "Русская", "Россиянин", "Россиянка"],
        "zh": ["俄国人", "俄罗斯人"],
        "de": ["Russe", "Russin", "Russisch"],
    },
    "French": {
        "en": ["French"],
        "ar": ["فرنسي", "فرنسية"],
        "fr": ["Français", "Française"],
        "he": ["צרפתי", "צרפתית"],
        "ru": ["Француз", "Француженка", "Французский"],
        "zh": ["法国人"],
        "de": ["Franzose", "Französin", "Französisch"],
    },
    "German": {
        "en": ["German"],
        "ar": ["ألماني", "ألمانية"],
        "fr": ["Allemand", "Allemande"],
        "he": ["גרמני", "גרמנית"],
        "ru": ["Немец", "Немка", "Германец", "Немецкий"],
        "zh": ["德国人"],
        "de": ["Deutsch", "Deutsche", "Deutscher"],
    },
    "British": {
        "en": ["British", "UK", "United Kingdom"],
        "ar": ["بريطاني", "بريطانية"],
        "fr": ["Britannique", "Anglais", "Anglaise"],
        "he": ["בריטי", "בריטית", "אנגלי"],
        "ru": ["Британец", "Британка", "Английский", "Англичанин"],
        "zh": ["英国人"],
        "de": ["Brite", "Britin", "Britisch"],
    },
    "English": {
        "en": ["English"],
        "ar": ["إنجليزي", "إنجليزية"],
        "fr": ["Anglais", "Anglaise"],
        "he": ["אנגלי", "אנגלית"],
        "ru": ["Англичанин", "Англичанка", "Английский"],
        "zh": ["英格兰人"],
        "de": ["Engländer", "Engländerin"],
    },
    "Japanese": {
        "en": ["Japanese"],
        "ar": ["ياباني", "يابانية"],
        "fr": ["Japonais", "Japonaise"],
        "he": ["יפני", "יפנית"],
        "ru": ["Японец", "Японка", "Японский"],
        "zh": ["日本人"],
        "de": ["Japaner", "Japanerin"],
    },
    "Indian": {
        "en": ["Indian"],
        "ar": ["هندي", "هندية"],
        "fr": ["Indien", "Indienne"],
        "he": ["הודי", "הודית"],
        "ru": ["Индиец", "Индианка", "Индийский"],
        "zh": ["印度人"],
        "de": ["Inder", "Inderin", "Indisch"],
    },
    "Canadian": {
        "en": ["Canadian"],
        "ar": ["كندي", "كندية"],
        "fr": ["Canadien", "Canadienne"],
        "he": ["קנדי", "קנדית"],
        "ru": ["Канадец", "Канадка", "Канадский"],
        "zh": ["加拿大人"],
        "de": ["Kanadier", "Kanadierin"],
    },
    "Australian": {
        "en": ["Australian"],
        "ar": ["أسترالي", "أسترالية"],
        "fr": ["Australien", "Australienne"],
        "he": ["אוסטרלי", "אוסטרלית"],
        "ru": ["Австралиец", "Австралийка", "Австралийский"],
        "zh": ["澳大利亚人"],
        "de": ["Australier", "Australierin"],
    },
    "Brazilian": {
        "en": ["Brazilian"],
        "ar": ["برازيلي", "برازيلية"],
        "fr": ["Brésilien", "Brésilienne"],
        "he": ["ברזילאי", "ברזילאית"],
        "ru": ["Бразилец", "Бразильянка", "Бразильский"],
        "zh": ["巴西人"],
        "de": ["Brasilianer", "Brasilianerin"],
    },
    "Mexican": {
        "en": ["Mexican"],
        "ar": ["مكسيكي", "مكسيكية"],
        "fr": ["Mexicain", "Mexicaine"],
        "he": ["מקסיקני", "מקסיקנית"],
        "ru": ["Мексиканец", "Мексиканка", "Мексиканский"],
        "zh": ["墨西哥人"],
        "de": ["Mexikaner", "Mexikanerin"],
    },
    "Spanish": {
        "en": ["Spanish"],
        "ar": ["إسباني", "إسبانية"],
        "fr": ["Espagnol", "Espagnole"],
        "he": ["ספרדי", "ספרדית"],
        "ru": ["Испанец", "Испанка", "Испанский"],
        "zh": ["西班牙人"],
        "de": ["Spanier", "Spanierin", "Spanisch"],
    },
    "Italian": {
        "en": ["Italian"],
        "ar": ["إيطالي", "إيطالية"],
        "fr": ["Italien", "Italienne"],
        "he": ["איטלקי", "איטלקית"],
        "ru": ["Итальянец", "Итальянка", "Итальянский"],
        "zh": ["意大利人"],
        "de": ["Italiener", "Italienerin"],
    },
    "Polish": {
        "en": ["Polish"],
        "ar": ["بولندي", "بولندية"],
        "fr": ["Polonais", "Polonaise"],
        "he": ["פולני", "פולנית"],
        "ru": ["Поляк", "Полька", "Польский"],
        "zh": ["波兰人"],
        "de": ["Pole", "Polin", "Polnisch"],
    },
    "Ukrainian": {
        "en": ["Ukrainian"],
        "ar": ["أوكراني", "أوكرانية"],
        "fr": ["Ukrainien", "Ukrainienne"],
        "he": ["אוקראיני", "אוקראינית"],
        "ru": ["Украинец", "Украинка", "Украинский"],
        "zh": ["乌克兰人"],
        "de": ["Ukrainer", "Ukrainerin"],
    },
    "Turkish": {
        "en": ["Turkish"],
        "ar": ["تركي", "تركية"],
        "fr": ["Turc", "Turque"],
        "he": ["טורקי", "טורקיה"],
        "ru": ["Турок", "Турчанка", "Турецкий"],
        "zh": ["土耳其人"],
        "de": ["Türke", "Türkin"],
    },
    "Iranian": {
        "en": ["Iranian", "Persian"],
        "ar": ["إيراني", "إيرانية", "فارسي"],
        "fr": ["Iranien", "Iranienne", "Persan", "Persane"],
        "he": ["איראני", "איראנית", "פרסי"],
        "ru": ["Иранец", "Иранка", "Персиянин", "Персидский"],
        "zh": ["伊朗人", "波斯人"],
        "de": ["Iraner", "Iranerin", "Perser"],
    },
    "Israeli": {
        "en": ["Israeli"],
        "ar": ["إسرائيلي", "إسرائيلية"],
        "fr": ["Israélien", "Israélienne"],
        "he": ["ישראלי", "ישראלית"],
        "ru": ["Израильтянин", "Израильтянка", "Израильский"],
        "zh": ["以色列人"],
        "de": ["Israeli", "Israelisch"],
    },
    "Egyptian": {
        "en": ["Egyptian"],
        "ar": ["مصري", "مصرية"],
        "fr": ["Égyptien", "Égyptienne"],
        "he": ["מצרי", "מצרית"],
        "ru": ["Египтянин", "Египтянка", "Египетский"],
        "zh": ["埃及人"],
        "de": ["Ägypter", "Ägypterin"],
    },
    "Saudi": {
        "en": ["Saudi", "Saudi Arabian"],
        "ar": ["سعودي", "سعودية"],
        "fr": ["Saoudien", "Saoudienne"],
        "he": ["סעודי", "סעודית"],
        "ru": ["Саудовец", "Саудовка", "Саудовский"],
        "zh": ["沙特人"],
        "de": ["Saudier", "Saudierin"],
    },
    "Korean": {
        "en": ["Korean", "South Korean"],
        "ar": ["كوري", "كورية"],
        "fr": ["Coréen", "Coréenne"],
        "he": ["קוריאני", "קוריאנית"],
        "ru": ["Кореец", "Кореянка", "Корейский"],
        "zh": ["韩国人", "朝鲜人"],
        "de": ["Koreaner", "Koreanerin"],
    },
    "Dutch": {
        "en": ["Dutch", "Netherlands"],
        "ar": ["هولندي", "هولندية"],
        "fr": ["Néerlandais", "Néerlandaise", "Hollandais"],
        "he": ["הולנדי", "הולנדית"],
        "ru": ["Голландец", "Голландка", "Нидерландский"],
        "zh": ["荷兰人"],
        "de": ["Niederländer", "Niederländerin", "Holländer"],
    },
    # Add more as needed...
}


def build_reverse_mapping() -> Dict[str, Dict[str, str]]:
    """Build reverse mapping from localized names to canonical English names."""
    reverse_map: Dict[str, Dict[str, str]] = {}
    
    for canonical_name, translations in NATIONALITY_TRANSLATIONS.items():
        for lang, names in translations.items():
            if lang not in reverse_map:
                reverse_map[lang] = {}
            for name in names:
                # Store both original case and lowercase for fuzzy matching
                reverse_map[lang][name.lower()] = canonical_name
                
    return reverse_map


def get_nationalities_for_language(language: str) -> List[str]:
    """Get list of nationality names in specific language."""
    nationalities = []
    for canonical_name, translations in NATIONALITY_TRANSLATIONS.items():
        if language in translations:
            nationalities.extend(translations[language])
    return sorted(set(nationalities))


def find_canonical_nationality(input_text: str, language: str) -> Optional[str]:
    """Find canonical English nationality name from input in any language."""
    reverse_map = build_reverse_mapping()
    
    normalized_input = input_text.lower().strip()
    
    # Try exact match in the specified language first
    if language in reverse_map and normalized_input in reverse_map[language]:
        return reverse_map[language][normalized_input]
    
    # Try all languages if not found in specified language
    for lang_map in reverse_map.values():
        if normalized_input in lang_map:
            return lang_map[normalized_input]
    
    return None


def get_nationality_suggestions(input_text: str, language: str, k: int = 3) -> List[str]:
    """Get nationality suggestions in the user's language."""
    from utils import top_k_similar
    
    available_nationalities = get_nationalities_for_language(language)
    if not available_nationalities:
        # Fallback to English if language not available
        available_nationalities = get_nationalities_for_language("en")
    
    suggestions = top_k_similar(input_text, available_nationalities, k=k)
    return [name for name, _score in suggestions]
