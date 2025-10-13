#!/usr/bin/env python3
"""
Script to export annotation data from the bot database to Excel format.
Exports N=50 annotation examples with the specified format.
"""

import sqlite3
import pandas as pd
import os
from typing import List, Dict, Any

def get_annotations_data(db_path: str, events_per_language: int = 10) -> List[Dict[str, Any]]:
    """
    Extract annotation data from the database, getting events per language.
    
    Args:
        db_path: Path to the SQLite database file
        events_per_language: Number of events to get per language (default: 10)
    
    Returns:
        List of dictionaries containing annotation data
    """
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    
    try:
        # Get all available languages
        languages_query = "SELECT DISTINCT language FROM events ORDER BY language"
        languages_cursor = conn.execute(languages_query)
        languages = [row['language'] for row in languages_cursor.fetchall()]
        
        data = []
        
        # For each language, get events with annotations
        for language in languages:
            # Query to get events in this language with their annotations
            # We'll get the most recent annotations for events in this language
            query = """
            SELECT 
                e.topic_name,
                e.topic_url,
                e.topic_description,
                v.viewpoint_text as viewpoint,
                a.step_1_choice as is_biased,
                a.step_2_choice as biased_to_country,
                e.language,
                a.created_at
            FROM events e
            JOIN viewpoints v ON e.id = v.event_id
            JOIN annotations a ON v.id = a.viewpoint_id
            WHERE e.language = ? 
            AND a.has_error = 0  -- Exclude error annotations
            ORDER BY a.created_at DESC
            LIMIT ?
            """
            
            cursor = conn.execute(query, (language, events_per_language))
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            for row in rows:
                data.append({
                    'topic_name': row['topic_name'],
                    'topic_url': row['topic_url'],
                    'topic_description': row['topic_description'],
                    'viewpoint': row['viewpoint'],
                    'is_biased': row['is_biased'],
                    'biased_to_country': row['biased_to_country'],
                    'language': row['language']
                })
            
            # If we didn't get enough events for this language, try to get more from other languages
            # but keep the event content in the original language
            if len(rows) < events_per_language:
                remaining_needed = events_per_language - len(rows)
                print(f"Warning: Only found {len(rows)} annotations for language {language}, need {remaining_needed} more")
                
                # Try to get events from other languages that have annotations
                # but use the event content AND viewpoint from the target language
                fallback_query = """
                SELECT 
                    e_target.topic_name,
                    e_target.topic_url,
                    e_target.topic_description,
                    v_target.viewpoint_text as viewpoint,
                    a.step_1_choice as is_biased,
                    a.step_2_choice as biased_to_country,
                    e_target.language,
                    a.created_at
                FROM events e_target
                JOIN viewpoints v_target ON e_target.id = v_target.event_id
                JOIN events e_other ON e_target.event_index = e_other.event_index 
                JOIN viewpoints v_other ON e_other.id = v_other.event_id
                JOIN annotations a ON v_other.id = a.viewpoint_id
                WHERE e_target.language = ? 
                AND e_other.language != ?
                AND a.has_error = 0
                AND e_target.id NOT IN (
                    SELECT DISTINCT e2.id 
                    FROM events e2 
                    JOIN viewpoints v2 ON e2.id = v2.event_id 
                    JOIN annotations a2 ON v2.id = a2.viewpoint_id 
                    WHERE e2.language = ? AND a2.has_error = 0
                )
                ORDER BY a.created_at DESC
                LIMIT ?
                """
                
                fallback_cursor = conn.execute(fallback_query, (language, language, language, remaining_needed))
                fallback_rows = fallback_cursor.fetchall()
                
                for row in fallback_rows:
                    data.append({
                        'topic_name': row['topic_name'],
                        'topic_url': row['topic_url'],
                        'topic_description': row['topic_description'],
                        'viewpoint': row['viewpoint'],
                        'is_biased': row['is_biased'],
                        'biased_to_country': row['biased_to_country'],
                        'language': row['language']
                    })
        
        return data
        
    finally:
        conn.close()

def export_to_excel(data: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export data to Excel file.
    
    Args:
        data: List of dictionaries containing the data
        output_path: Path where to save the Excel file
    """
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Export to Excel
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    print(f"Successfully exported {len(data)} annotations to {output_path}")

def main():
    """Main function to run the export process."""
    
    # Configuration
    db_path = "bot_backup_23sep.db"
    output_path = "annotations_export.xlsx"
    events_per_language = 10
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return
    
    print(f"Extracting {events_per_language} events per language from {db_path}...")
    
    # Get data from database
    data = get_annotations_data(db_path, events_per_language)
    
    if not data:
        print("No valid annotations found in the database!")
        return
    
    # Count by language
    language_counts = {}
    for item in data:
        lang = item['language']
        language_counts[lang] = language_counts.get(lang, 0) + 1
    
    print(f"Found {len(data)} valid annotations (excluding errors)")
    print("Events per language:")
    for lang, count in sorted(language_counts.items()):
        print(f"  {lang}: {count} events")
    
    # Export to Excel
    export_to_excel(data, output_path)
    
    # Print summary
    print("\nExport Summary:")
    print(f"- Total annotations exported: {len(data)}")
    print(f"- Output file: {output_path}")
    
    # Show sample of data
    if data:
        print("\nSample data:")
        sample = data[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
