## Data mining pipeline

This folder contains a 3-stage pipeline to build a multilingual event dataset from Wikipedia with structured extraction and an explicit debiasing step. The method is designed for academic reproducibility and supports ACL-style reporting.

### Prerequisites
- Set environment variables:
  - `OPENAI_API_KEY` (required)
  - `EXA_API_KEY` (required)
  - `OPENAI_BASE_URL` (optional; defaults to `https://openrouter.ai/api/v1`)
  - `OPENAI_MODEL` (optional; defaults to `openai/gpt-oss-120b`)
- Install dependencies from the project root:
  - `pip install -r requirements.txt`

### 1) Discover events (save seeds)
Saves raw discovered Wikipedia seeds to JSON.

```bash
python -m data_mining.discover "CountryA" "CountryB" \
  --start 1900 --end 2005 --max-events 200 \
  --langs en,fr,ru,zh,ar,he \
  --discover-output ./data/discovered.json
```

Output contains a top-level `seeds` list with items like:

```json
{ "name": "Event title", "url": "https://en.wikipedia.org/..." }
```

### 2) Cluster and select unique events
Embeds event names with `sentence-transformers/all-mpnet-base-v2`, clusters with agglomerative clustering (cosine distance), then uses the LLM to pick a canonical representative per cluster.

```bash
python -m data_mining.cluster_unique \
  --input ./data/discovered.json \
  --output ./data/unique_seeds.json \
  --threshold 0.3
```

Notes:
- Lower `--threshold` → tighter clusters (more clusters). Default: `0.3`.
- Change embedding model via `--embed-model` if needed.

### 3) Finalize: extract + debias
Runs extraction from the selected Wikipedia pages and produces a debiased multilingual summary per event.

```bash
python -m data_mining.finalize_processing \
  --input ./data/unique_seeds.json \
  --output ./data/final_dataset.json \
  --langs en,fr,ru,zh,ar,he \
  --workers 8
```

### Outputs
- `discovered.json`: raw seeds
- `unique_seeds.json`: deduplicated seeds (canonical per cluster)
- `final_dataset.json`: list of `DatasetEvent` objects `{ seed, extracted, debiased }`

### Merged final dataset structure
After generating country-pair specific files (e.g., `USA_USSR_final.json`), you can merge them with `merge_final_json.py` into a single dataset. The merged file schema is:

```json
{
  "llm": "<model_name>",
  "languages": ["en", "fr", "ru", "zh", "ar", "he"],
  "start_year": 1900,
  "end_year": 2005,
  "data": [
    {
      "countries": ["USA", "USSR"],
      "seed_name": "Korean War",
      "topic_url": "https://en.wikipedia.org/wiki/Korean_War",
      "topic_name": "Korean War",
      "years": "1950-1953",
      "topic_description": "…",
      "paragraph_anchor_or_comment": "intro paragraph",
      "viewpoints": {
        "neutral": {
          "description": "<= 50-word debiased summary"
        },
        "perspectives": [
          { "language": "en", "url": "…", "key_points": ["…"] }
        ]
      }
    }
  ]
}
```

Run the merge:

```bash
python -m data_mining.merge_final_json --output ./data/final_dataset.json
```

### 4) Translate dataset to multiple languages

Translates the final dataset with propaganda viewpoints to multiple target languages, including topic names, descriptions, viewpoints, and finds corresponding Wikipedia pages.

```bash
python -m data_mining.translate_dataset
```

This script:
- Detects the current language of content in the dataset using LLM
- Translates topic names, descriptions, and viewpoints to target languages: `ar, en, fr, he, ru, zh, de` using LLM
- Finds corresponding Wikipedia URLs in target languages using Wikipedia API (keeps original URL if target language version doesn't exist)
- Restructures the output with language codes as top-level keys

**Input**: `data/final_dataset_with_propaganda.json`
**Output**: `data/final_dataset_with_propaganda_translated.json`

The output structure becomes:
```json
{
  "en": { "llm": "...", "data": [...] },
  "fr": { "llm": "...", "data": [...] },
  "ru": { "llm": "...", "data": [...] },
  ...
}
```

Each language section contains the complete dataset structure with all content translated to that language.

## Method

### Task and scope
We construct a multilingual dataset of historical interstate conflicts and disputes between a pair of countries over a specified period. For each event, we extract structured facts and generate a short neutral description together with a commentary on cross-lingual bias. Sources are Wikipedia articles across languages `en, fr, ru, zh, ar, he` by default.

### Data collection (discovery)
Let \(A\) and \(B\) be two countries and \([y_s, y_e]\) the time window. We prompt an LLM to propose diverse, high-recall search queries (without `site:` filters) that cover wars, crises, incidents, skirmishes, and list/timeline pages. We then submit each query to the Exa neural search API with domain restriction to Wikipedia and retrieve up to \(k\) results per query.

Filtering steps implemented in `data_mining.discover`:
- Restrict results to `*.wikipedia.org` and deduplicate by full URL.
- Rank by the Exa score and keep the top `max_events` URLs.
- Convert each URL to an `EventSeed { name, url }`, using the returned title or a URL-derived fallback.

Formally, we approximate cosine similarity search over an internal embedding space and retain items with highest Exa relevance score. Deduplication is set-based over normalized URLs.

### Clustering and canonicalization
To remove near-duplicates and variant pages for the same event, we perform sentence-level embedding of seed names using `sentence-transformers/all-mpnet-base-v2`. We then run agglomerative clustering with average linkage and cosine distance threshold \(\tau\):

\[ d_{\cos}(x, y) = 1 - \frac{x \cdot y}{\lVert x \rVert\, \lVert y \rVert}. \]

Clusters are formed with `distance_threshold=\tau` (default \(\tau = 0.3\)). For each cluster, we ask the LLM to select a canonical page (prefer general, authoritative pages; prefer English when multiple language editions exist). The implementation supports returning multiple indices in ambiguous clusters, though by default a single representative is expected. We deduplicate the final selection by URL.

Implementation details in `data_mining.cluster_unique`:
- Embeddings: `all-mpnet-base-v2` with normalization.
- Clustering: `AgglomerativeClustering(metric="cosine", linkage="average", distance_threshold=\tau)`.
- Canonicalization: structured LLM output over enumerated candidates.
- Parallelism: `ThreadPoolExecutor` over clusters.

### Extraction and multilingual debiasing
Given a canonical seed, we fetch the article text via Exa (`get_contents`) and ask the LLM to extract:
- `years` (e.g., `1939–1945` or a single year),
- a concise factual `short_description` (≤ 80 words),
- a `paragraph_anchor_or_comment` indicating the likely section/paragraph within the page.

If the anchor is missing, we heuristically derive a section anchor from headings that match the event name.

Multilingual perspective collection (in `data_mining.finalize_processing`):
1. Construct candidate interlanguage URLs by swapping the language subdomain while preserving the path.
2. Retrieve article text for each candidate; if < 3 languages are available, backfill with Exa search constrained to Wikipedia domains in the target languages.
3. For each language, summarize the article into 3–5 bullets highlighting emphasis/stance.

Debiasing synthesis. We provide the set of language-specific bullets to the LLM and request:
- a neutral description (≤ 50 words), and
- a `bias_comment` that explicitly notes differences and potential biases across languages.

We store both the per-language bullets and the debiased synthesis for auditability.

### Data schema
Objects (Pydantic models) used throughout the pipeline:

- `EventSeed`:
  - `name: str`
  - `url: HttpUrl`

- `EventExtracted`:
  - `url: HttpUrl`
  - `name: str`
  - `years: str`
  - `short_description: str` (≤ 80 words)
  - `paragraph_anchor_or_comment: str`

- `LanguagePerspective`:
  - `language: str`
  - `url: Optional[HttpUrl]`
  - `key_points: List[str]` (3–5 bullets)

- `DebiasedEventSummary`:
  - `neutral_description_50_words_max: str`
  - `bias_comment: str`
  - `languages_used: List[str]`
  - `perspectives: List[LanguagePerspective]`

- `DatasetEvent`:
  - `seed: EventSeed`
  - `extracted: EventExtracted`
  - `debiased: DebiasedEventSummary`

Example item in `final_dataset.json`:

```json
{
  "seed": {
    "name": "Sino-Soviet border conflict",
    "url": "https://en.wikipedia.org/wiki/Sino-Soviet_border_conflict"
  },
  "extracted": {
    "url": "https://en.wikipedia.org/wiki/Sino-Soviet_border_conflict",
    "name": "Sino-Soviet border conflict",
    "years": "1969",
    "short_description": "A series of armed clashes along the Ussuri River between the USSR and China amid deteriorating relations.",
    "paragraph_anchor_or_comment": "#Background"
  },
  "debiased": {
    "neutral_description_50_words_max": "In 1969, China and the Soviet Union fought brief border clashes along the Ussuri River amid Sino–Soviet tensions.",
    "bias_comment": "Russian and Chinese articles emphasize defensive motives and casualty counts differently; English coverage stresses Cold War context.",
    "languages_used": ["en", "ru", "zh"],
    "perspectives": [
      {"language": "en", "url": "https://en.wikipedia.org/wiki/Sino-Soviet_border_conflict", "key_points": ["Cold War context", "Brief clashes", "Border demarcation issues"]},
      {"language": "ru", "url": "https://ru.wikipedia.org/wiki/Советско-китайский_пограничный_конфликт_(1969)", "key_points": ["Defense emphasis", "Casualties detailed"]},
      {"language": "zh", "url": "https://zh.wikipedia.org/wiki/中苏边界冲突", "key_points": ["Sovereignty framing", "Damansky/Zhenbao Island focus"]}
    ]
  }
}
```

### Quality control and filtering
- URL-level deduplication is applied after discovery and after canonical selection.
- The extractor enforces a short factual description and year format.
- Interlanguage retrieval requires at least ~3 languages when possible; we backfill via search.
- All LLM calls use structured outputs (via `instructor`) where applicable to reduce parse errors.

### Reproducibility and configuration
- Required environment variables: `OPENAI_API_KEY`, `EXA_API_KEY`.
- Optional: `OPENAI_BASE_URL` (default `https://openrouter.ai/api/v1`), `OPENAI_MODEL`.
- Parallelism: controlled by `--workers` in the finalization stage and `--workers` in clustering.
- Default languages: `en, fr, ru, zh, ar, he` (configurable via CLI).

Note that LLM outputs can be nondeterministic; for stable runs, pin `OPENAI_MODEL`, keep the same base URL/provider, and avoid mid-run parameter changes. The pipeline records basic metadata (model name, languages, datetime) alongside outputs.

### Ethical considerations and limitations
- Wikipedia may reflect contemporaneous editorial biases; our cross-lingual synthesis mitigates but does not eliminate this.
- The neutral description is constrained to ≤ 50 words and may omit nuance; the `bias_comment` surfaces omissions and emphasis differences.
- The method focuses on interstate events; civil conflicts and multi-party disputes may require additional curation.

### End-to-end example

```bash
# 1) Discover
python -m data_mining.discover "USA" "USSR" \
  --start 1900 --end 2005 --max-events 200 \
  --langs en,fr,ru,zh,ar,he \
  --discover-output ./data/USA_USSR_discovered.json

# 2) Cluster and canonicalize
python -m data_mining.cluster_unique \
  --input ./data/USA_USSR_discovered.json \
  --output ./data/USA_USSR_discovered_unique.json \
  --threshold 0.3

# 3) Extract and debias
python -m data_mining.finalize_processing \
  --input ./data/USA_USSR_discovered_unique.json \
  --output ./data/USA_USSR_final.json \
  --langs en,fr,ru,zh,ar,he \
  --workers 8
```
