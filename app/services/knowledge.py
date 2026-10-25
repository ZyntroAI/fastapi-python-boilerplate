import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from schemas import (
    KnowledgeSearchResult,
    ValidationResponse,
)

VAULT_PATH = Path(
    os.getenv("OBSIDIAN_VAULT_PATH", "")
).resolve()

CACHE_DIR = VAULT_PATH / ".obsidian-mcp"
JSON_CACHE_PATH = CACHE_DIR / "semantic-index.json"
NPZ_CACHE_PATH = CACHE_DIR / "semantic-index.npz"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global model

    if model is None:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return model


def content_hash(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def split_markdown(text: str) -> list[dict]:
    chunks = []
    current_heading = ""
    current_content: list[str] = []

    for line in text.splitlines():
        if line.startswith("#"):
            if current_content:
                chunks.append(
                    {
                        "heading": current_heading,
                        "content": "\n".join(current_content).strip(),
                    }
                )

            current_heading = line.lstrip("#").strip()
            current_content = [line]
            continue

        current_content.append(line)

    if current_content:
        chunks.append(
            {
                "heading": current_heading,
                "content": "\n".join(current_content).strip(),
            }
        )

    return [chunk for chunk in chunks if chunk["content"]]


def build_semantic_index(
    folder: str = "",
    force_rebuild: bool = False,
) -> ReindexResponse:
    folder_path = VAULT_PATH / folder if folder else VAULT_PATH
    metadata: dict[str, dict] = {}
    chunk_ids: list[str] = []
    vectors: list[list[float]] = []

    for path in folder_path.rglob("*.md"):
        relative_path = path.relative_to(VAULT_PATH).as_posix()
        text = path.read_text(encoding="utf-8")
        file_hash = content_hash(text)

        for index, chunk in enumerate(split_markdown(text)):
            chunk_id = f"{relative_path}::{index}"
            chunk_hash = content_hash(chunk["content"])

            metadata[chunk_id] = {
                "relative_path": relative_path,
                "title": path.stem,
                "heading": chunk["heading"],
                "content": chunk["content"],
                "content_hash": chunk_hash,
                "file_hash": file_hash,
            }

            chunk_ids.append(chunk_id)

    if chunk_ids:
        model = get_model()
        texts = [
            metadata[chunk_id]["content"]
            for chunk_id in chunk_ids
        ]

        vectors = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    json_tmp = JSON_CACHE_PATH.with_suffix(".json.tmp")
    npz_tmp = NPZ_CACHE_PATH.with_suffix(".npz.tmp")

    json_tmp.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    np.savez_compressed(
        npz_tmp,
        chunk_ids=np.array(chunk_ids, dtype=object),
        vectors=np.array(
            vectors,
            dtype=np.float32,
        ),
    )

    json_tmp.replace(JSON_CACHE_PATH)
    npz_tmp.replace(NPZ_CACHE_PATH)

    return ReindexResponse(
        indexed_notes=len(list(folder_path.rglob("*.md"))),
        new_or_changed_chunks=len(chunk_ids),
        total_chunks=len(chunk_ids),
    )


def validate_semantic_cache() -> ValidationResponse:
    errors: list[str] = []
    warnings: list[str] = []

    if not JSON_CACHE_PATH.exists():
        errors.append("JSON cache file does not exist")

    if not NPZ_CACHE_PATH.exists():
        errors.append("NPZ cache file does not exist")

    if errors:
        return ValidationResponse(
            valid=False,
            errors=errors,
            warnings=warnings,
        )

    metadata = json.loads(
        JSON_CACHE_PATH.read_text(encoding="utf-8")
    )

    with np.load(NPZ_CACHE_PATH, allow_pickle=False) as data:
        chunk_ids = data["chunk_ids"].tolist()
        vectors = data["vectors"]

    if len(chunk_ids) != len(vectors):
        errors.append(
            "Chunk ID count does not match vector count"
        )

    if vectors.ndim != 2 or vectors.shape[1] != EMBEDDING_DIMENSION:
        errors.append(
            f"Invalid embedding shape: {vectors.shape}"
        )

    if not np.isfinite(vectors).all():
        errors.append("Vectors contain NaN or infinity values")

    missing_metadata = [
        chunk_id
        for chunk_id in chunk_ids
        if chunk_id not in metadata
    ]

    if missing_metadata:
        errors.append(
            f"Missing metadata for {len(missing_metadata)} chunks"
        )

    return ValidationResponse(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        chunk_count=len(chunk_ids),
        vector_dimension=(
            int(vectors.shape[1]) if vectors.ndim == 2 else None
        ),
    )


def search_semantic_index(
    query: str,
    folder: str = "",
    limit: int = 5,
    minimum_score: float = 0.30,
) -> list[KnowledgeSearchResult]:
    if not NPZ_CACHE_PATH.exists() or not JSON_CACHE_PATH.exists():
        return []

    metadata = json.loads(
        JSON_CACHE_PATH.read_text(encoding="utf-8")
    )

    with np.load(NPZ_CACHE_PATH, allow_pickle=False) as data:
        chunk_ids = data["chunk_ids"].tolist()
        vectors = data["vectors"]

    if len(chunk_ids) == 0:
        return []

    model = get_model()

    query_vector = model.encode(
        query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    similarities = model.similarity(
        query_vector,
        vectors,
    )[0]

    ranked_indices = np.argsort(similarities)[::-1]
    results: list[KnowledgeSearchResult] = []

    for index in ranked_indices:
        score = float(similarities[index])

        if score < minimum_score:
            break

        chunk_id = str(chunk_ids[index])
        chunk = metadata.get(chunk_id)

        if not chunk:
            continue

        results.append(
            KnowledgeSearchResult(
                score=round(float(score), 4),
                relative_path=chunk["relative_path"],
                title=chunk["title"],
                heading=chunk["heading"],
                chunk_id=chunk_id,
                excerpt=chunk["content"][:500],
            )
        )

        if len(results) >= limit:
            break

    return results