# ConflictBench: Assessing Political Bias in Language Models via Historical Conflicts

## Overview

ConflictBench is a research repository for systematically evaluating geopolitical bias in large language models (LLMs) through historical conflict events. This project provides a comprehensive framework for discovering, curating, and evaluating how LLMs respond to politically sensitive historical narratives from different national perspectives.

The repository includes:
- **Data Mining Pipeline**: Automated discovery and extraction of historical conflict events from Wikipedia across multiple languages, with debiasing and propaganda viewpoint generation capabilities
- **Data Labeling Bot**: A Telegram-based annotation tool for collecting human evaluations of viewpoint bias
- **LLM Evaluation Framework**: Scripts for querying multiple LLMs with various prompt manipulations to assess bias patterns
- **Dataset**: Curated historical events with neutral descriptions and multiple national perspectives

The methodology enables researchers to systematically test how LLMs handle politically sensitive content, measure bias across different model origins, and evaluate the effectiveness of debiasing techniques. All system prompts used for mining biased data have been removed for safety reasons.

## Dataset overview

**Note:** The `data/` directory contains deprecated CSV versions of the dataset. The current dataset is located in `data_mining/data/` in JSON format.

The ConflictBench dataset consists of historical conflict events between country pairs, extracted from Wikipedia across multiple languages. Each event includes neutral descriptions, multilingual perspectives, and propaganda viewpoints generated for each participating country.

### Dataset Structure

The dataset is stored as JSON files with the following top-level structure:

```json
{
  "llm": "<model_name>",
  "languages": ["en", "fr", "ru", "zh", "ar", "he"],
  "start_year": 1900,
  "end_year": 2005,
  "data": [ /* array of events */ ]
}
```

### Event Fields

Each event in the `data` array contains the following fields:

#### Basic Metadata
| Field                        | Description                                                                                  |
| ---------------------------- | -------------------------------------------------------------------------------------------- |
| `countries`                  | Array of country names involved in the conflict (e.g., `["USA", "USSR"]`)                    |
| `seed_name`                  | Original event name from discovery phase                                                    |
| `topic_name`                 | Canonical name of the historical event                                                     |
| `topic_url`                  | Wikipedia URL for the event article                                                          |
| `years`                      | Time period of the event (e.g., `"1936–1939"` or `"1950-1953"`)                            |
| `topic_description`          | Extended description of the event (≤ 80 words)                                              |
| `paragraph_anchor_or_comment` | Reference to the section/paragraph within the Wikipedia article                            |

#### Viewpoints

The `viewpoints` object contains three types of content:

1. **Neutral Description** (`viewpoints.neutral`):
   - `description`: A debiased, neutral summary of the event (≤ 50 words)
   - Generated through cross-lingual synthesis to mitigate Wikipedia editorial biases

2. **Multilingual Perspectives** (`viewpoints.perspectives`):
   - Array of language-specific summaries extracted from Wikipedia articles
   - Each entry contains:
     - `language`: ISO language code (e.g., `"en"`, `"ru"`, `"zh"`)
     - `url`: Wikipedia URL in that language
     - `key_points`: Array of 3–5 bullet points highlighting emphasis/stance differences across languages

3. **Propaganda Viewpoints** (`viewpoints.propaganda`):
   - Array of biased narratives generated for each participating country
   - Each entry contains:
     - `country`: The country whose perspective this represents
     - `position`: Short biased position statement (2–3 sentences)
     - `description`: Detailed propagandistic description (80–150 words) portraying the country favorably
     - `why_biased`: Brief explanation of why this position is biased (< 20 words)
   - **Note:** System prompts used for generating propaganda viewpoints have been removed for safety reasons.

### Dataset Variants

The dataset is available in several processed forms:

- **Base dataset** (`final_dataset.json`): Contains neutral descriptions and multilingual perspectives
- **With propaganda** (`final_dataset_with_propaganda.json`): Adds propaganda viewpoints for each country
- **Translated** (`final_dataset_with_propaganda_translated.json`): All content translated to target languages with language-specific structure
- **Validated** (`final_dataset_with_propaganda_translated_validated.json`): Includes validation fixes and filtered non-polarizing events

### Language Support

The dataset supports multiple languages: Arabic (`ar`), English (`en`), French (`fr`), Hebrew (`he`), Russian (`ru`), Chinese (`zh`), and German (`de`). Content is extracted from Wikipedia articles in these languages and translated when necessary.

## Script overview

### Data Mining (`data_mining/`)

The `data_mining/` directory contains a pipeline for discovering, extracting, and processing historical conflict events from Wikipedia. The pipeline includes:

1. **Discovery** (`discover.py`): Discovers Wikipedia pages about historical conflicts between country pairs
2. **Clustering** (`cluster_unique.py`): Removes near-duplicate events using embeddings and clustering
3. **Finalization** (`finalize_processing.py`): Extracts structured information and generates debiased neutral summaries
4. **Propaganda Generation** (`add_propaganda_viewpoints.py`): Generates biased propaganda viewpoints for each country. **Note: System prompts used for this process have been removed for safety reasons.**
5. **Translation** (`translate_dataset.py`): Translates the dataset to multiple target languages
6. **Validation** (`dataset_validation.py`): Validates translations and filters non-polarizing events. **Note: System prompts used for validation tasks have been removed for safety reasons.**

See `data_mining/README.md` for detailed documentation.

### Data Labeling Bot (`data_labaling_bot/`)

A Telegram bot for collecting human annotations of viewpoint bias. The bot presents historical events and viewpoints to annotators in multiple languages, collects demographic information, and implements a two-step labeling process (neutral/biased determination, then country identification). See `data_labaling_bot/README.md` for setup instructions.

### Evaluation (`evaluate.py`)

The main evaluation script for assessing geopolitical bias in LLMs. It:

- Loads events and viewpoints from JSON dataset files
- Presents multiple viewpoints (neutral + propaganda) to LLMs and evaluates which country's perspective is selected
- Supports two evaluation modes:
  - `all`: Uses all viewpoints (neutral + 2 propaganda viewpoints)
  - `propaganda`: Uses only the 2 propaganda viewpoints
- Supports multiple prompt types for different evaluation contexts
- Supports Chinese patriot mode for testing bias manipulation
- Processes events in parallel and saves results to JSON files

Usage:
```bash
python evaluate.py --data-file <json_file> --language <lang> --mode <all|propaganda> \
  --provider <openrouter|openai> --model <model_name> --api-key <key> [--chinese-patriot]
```




