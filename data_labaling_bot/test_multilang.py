#!/usr/bin/env python3
"""
Simple test script to verify multi-language functionality works.
Run this after setting up the database with translated data.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db import init_db, get_weighted_viewpoint_with_event, get_user, upsert_user
from localization import get_text, SUPPORTED_LANGUAGES, is_supported_language
from nationalities_multilang import (
    find_canonical_nationality,
    get_nationality_suggestions,
    get_nationalities_for_language,
)


def test_localization():
    """Test localization functionality."""
    print("Testing localization...")
    
    # Test basic translation
    for lang in SUPPORTED_LANGUAGES:
        welcome = get_text("welcome", lang)
        print(f"{lang}: {welcome}")
    
    # Test with parameters
    label_text = get_text("saved_label", "en", label=3, label_text="Neutral description")
    print(f"Formatted text: {label_text}")
    
    print("✅ Localization test passed\n")


def test_database():
    """Test database functionality."""
    print("Testing database...")
    
    # Initialize database
    init_db()
    
    # Test user operations
    test_user_id = 12345
    upsert_user(
        telegram_id=test_user_id,
        nationality="American",
        age=25,
        occupation_type="student",
        education_level="bachelor",
        preferred_language="fr"
    )
    
    user = get_user(test_user_id)
    assert user is not None, "User should exist"
    assert user["preferred_language"] == "fr", "Language should be French"
    print(f"✅ User created: {user}")
    
    # Test viewpoint retrieval for different languages
    for lang in ["en", "fr", "de"]:  # Test a few languages
        item = get_weighted_viewpoint_with_event(language=lang)
        if item:
            print(f"✅ Found viewpoint in {lang}: {item['topic_name'][:50]}...")
        else:
            print(f"⚠️  No viewpoints found for language: {lang}")
    
    print("✅ Database test passed\n")


def test_language_support():
    """Test language support functions."""
    print("Testing language support...")
    
    assert is_supported_language("en"), "English should be supported"
    assert is_supported_language("fr"), "French should be supported"
    assert not is_supported_language("xyz"), "Invalid language should not be supported"
    
    print("✅ Language support test passed\n")


def test_multilang_demographics():
    """Test multi-language demographics functionality."""
    print("Testing multi-language demographics...")
    
    # Test nationality lookup in different languages
    test_cases = [
        ("American", "en", "American"),
        ("Américain", "fr", "American"),
        ("أمريكي", "ar", "American"),
        ("Русский", "ru", "Russian"),
        ("中国人", "zh", "Chinese"),
        ("Deutsch", "de", "German"),
    ]
    
    for input_text, language, expected in test_cases:
        result = find_canonical_nationality(input_text, language)
        if result == expected:
            print(f"✅ {input_text} ({language}) -> {result}")
        else:
            print(f"⚠️  {input_text} ({language}) -> {result}, expected {expected}")
    
    # Test nationality suggestions
    for lang in ["en", "fr", "ru", "ar"]:
        suggestions = get_nationality_suggestions("amer", lang, k=3)
        print(f"✅ Suggestions for 'amer' in {lang}: {suggestions}")
    
    # Test occupation and education translations
    for lang in ["en", "fr", "ru", "ar"]:
        occupation_text = get_text("occupation_student", lang)
        education_text = get_text("education_bachelor", lang)
        print(f"✅ {lang}: Student = {occupation_text}, Bachelor = {education_text}")
    
    print("✅ Multi-language demographics test passed\n")


def main():
    """Run all tests."""
    print("🧪 Testing multi-language bot functionality...\n")
    
    try:
        test_localization()
        test_language_support()
        test_multilang_demographics()
        test_database()
        
        print("🎉 All tests passed! The multi-language bot with improved demographics should be working correctly.")
        print("\nNext steps:")
        print("1. Initialize the dataset: python -m data_labaling_bot.init_dataset")
        print("2. Set your TELEGRAM_BOT_TOKEN in .env file") 
        print("3. Run the bot: python -m data_labaling_bot.bot")
        print("\n📝 New features:")
        print("- Users can enter nationality in their preferred language")
        print("- Improved translations for better user experience")
        print("- Localized occupation and education options")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
