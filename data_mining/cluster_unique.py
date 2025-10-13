from __future__ import annotations

import argparse
import json
import logging
import os
from collections import defaultdict
from typing import List, Optional

from concurrent.futures import ThreadPoolExecutor
import instructor
import numpy as np
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from tqdm.auto import tqdm

from utils import EventSeed, build_llm_client, OPENAI_MODEL, load_seeds_and_metadata

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Uniques(BaseModel):
    indexes: List[int] = Field(..., description="Indexes of the chosen canonical and uniqueevents in the provided list")


def _cluster_embeddings(embeddings: np.ndarray, distance_threshold: float) -> List[int]:
    if len(embeddings) == 0:
        return []
    # Agglomerative clustering with cosine distance
    model = AgglomerativeClustering(
        n_clusters=None,
        metric="cosine",
        linkage="average",
        distance_threshold=distance_threshold,
    )
    labels: List[int] = list(model.fit_predict(embeddings))
    return labels


def _pick_uniques_with_llm(
    client: instructor.Instructor,
    cluster_items: List[EventSeed],
) -> EventSeed:
    # Prepare concise options for the model
    options = [f"{i}. {it.name} — {it.url}" for i, it in enumerate(cluster_items)]
    system = (
        "You are given a list of Wikipedia pages that likely refer to the same historical event. "
        " Pick the most canonical pages to represent the unique events. Prefer the most authoritative, general page over narrow subtopics. "
        " If multiple languages exist for the same event, prefer English (en.wikipedia) if present. "
        " Return ONLY the index as a structured field. "
        " If you are not sure, return the first page."
    )
    user = "\n".join(options)

    # Use structured output to get an integer index
    resp: UniquePick = client.chat.completions.create(  # type: ignore
        model=OPENAI_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        response_model=Uniques,
        parallel_tool_calls=False,
    )
    uniques = [cluster_items[i] for i in resp.indexes if i < len(cluster_items) and i >= 0]
    return uniques


def cluster_and_select(
    input_json_path: str,
    output_json_path: str,
    distance_threshold: float = 0.3,
    embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
    workers: int = 4,
) -> List[EventSeed]:
    base_llm, instructor_llm = build_llm_client()

    seeds, metadata = load_seeds_and_metadata(input_json_path)
    if not seeds:
        logger.warning("No seeds found in input JSON.")
        if output_json_path:
            os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump({"seeds": []}, f, ensure_ascii=False, indent=4)
        return []

    # Build clustering inputs
    texts = [s.name for s in seeds]
    model = SentenceTransformer(embedding_model_name)
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    logger.info(f"Embeddings shape: {embeddings.shape}")

    labels = _cluster_embeddings(embeddings, distance_threshold)
    logger.info(f"Labels shape: {len(labels)}")
    
    clusters: dict[int, List[int]] = defaultdict(list)
    for idx, label in enumerate(labels):
        clusters[int(label)].append(idx)

    logger.info(f"Formed {len(clusters)} clusters from {len(seeds)} seeds.")

    unique_seeds: List[EventSeed] = []
    cluster_items = list(clusters.items())
    candidate_lists: List[List[EventSeed]] = [[seeds[i] for i in indices] for _, indices in cluster_items]

    def _process_candidates(candidates: List[EventSeed]) -> EventSeed:
        try:
            return _pick_uniques_with_llm(instructor_llm, candidates)
        except Exception as e:
            logger.error(f"Error picking unique seed for cluster {candidates}: {e}")
            return [candidates[0]]

    with ThreadPoolExecutor(max_workers=min(len(candidate_lists), workers)) as pool:
        for chosen in tqdm(
            pool.map(_process_candidates, candidate_lists),
            total=len(candidate_lists),
            desc="Picking unique seeds with LLM",
        ):
            unique_seeds.extend(chosen)

    # Deduplicate by URL in case multiple clusters pick same
    seen_urls = set()
    uniq: List[EventSeed] = []
    for s in unique_seeds:
        u = str(s.url)
        if u in seen_urls:
            continue
        seen_urls.add(u)
        uniq.append(s)

    payload = {
        "source": os.path.basename(input_json_path),
        "llm": OPENAI_MODEL,
        "embedding_model": embedding_model_name,
        "clusters": len(clusters),
        "seeds": [s.model_dump(mode="json") for s in uniq],
    }
    for key, value in metadata.items():
        if key not in payload:
            payload[key] = value

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)

    logger.info(f"Saved {len(uniq)} unique seeds to {output_json_path}")
    return uniq


def main() -> None:
    parser = argparse.ArgumentParser(description="Cluster discovered events and select unique representatives")
    parser.add_argument("--input", type=str, required=True, help="Path to discovered seeds JSON (from workflow --only-discover)")
    parser.add_argument("--output", type=str, required=True, help="Path to write unique seeds JSON")
    parser.add_argument("--threshold", type=float, default=0.3, help="Cosine distance threshold for clustering (lower = tighter)")
    parser.add_argument(
        "--embed-model",
        type=str,
        default="sentence-transformers/all-mpnet-base-v2",
        help="SentenceTransformer model for embeddings",
    )
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel threads")
    args = parser.parse_args()

    cluster_and_select(
        input_json_path=args.input,
        output_json_path=args.output,
        distance_threshold=args.threshold,
        embedding_model_name=args.embed_model,
        workers=int(args.workers),
    )


if __name__ == "__main__":
    main()


