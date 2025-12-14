"""
Vector storage and semantic search for draft retrieval.
Uses OpenAI embeddings for semantic similarity search.
"""
import json
import aiosqlite
import os
from typing import List, Optional, Dict, Any
from openai import OpenAI
from backend.models import ExerciseDraft, ReviewMetadata

EMBEDDING_MODEL = "text-embedding-3-small"
SIMILARITY_THRESHOLD = 0.75  # Minimum similarity score to return a match (increased for stricter matching)

# Lazy initialization of OpenAI client
_client = None

def get_openai_client():
    """Get or create OpenAI client (lazy initialization)."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        _client = OpenAI(api_key=api_key)
    return _client

def extract_topics(text: str) -> set:
    """Extract mental health topic keywords from text."""
    topics = [
        'anxiety', 'depression', 'stress', 'panic', 'phobia', 'ocd', 'ptsd',
        'trauma', 'grief', 'anger', 'sleep', 'insomnia', 'eating', 'addiction',
        'relationship', 'social', 'work', 'school', 'exam', 'presentation',
        'public speaking', 'confidence', 'self esteem', 'loneliness', 'guilt',
        'shame', 'worry', 'fear', 'anger management', 'mindfulness', 'relaxation'
    ]
    text_lower = text.lower()
    return {topic for topic in topics if topic in text_lower}


async def initialize_vector_store(db_path: str = "backend/checkpoints.db"):
    """Initialize the draft_embeddings table if it doesn't exist."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS draft_embeddings (
                draft_id TEXT PRIMARY KEY,
                normalized_message TEXT,
                draft_title TEXT,
                draft_content TEXT,
                embedding TEXT,
                original_message TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a given text using OpenAI."""
    client = get_openai_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


async def index_draft(
    draft: ExerciseDraft,
    original_message: str,
    metadata: Optional[ReviewMetadata] = None,
    db_path: str = "backend/checkpoints.db"
) -> str:
    """
    Index a draft with its embedding.
    
    Args:
        draft: The ExerciseDraft to index
        original_message: The original user message that generated this draft
        metadata: Optional metadata (scores, revisions, etc.)
        db_path: Path to SQLite database
    
    Returns:
        The draft_id (normalized message) used as the key
    """
    # Normalize the original message for consistent key
    normalized_msg = _normalize_message(original_message)
    
    # Create searchable text from draft
    searchable_text = f"{draft.title} {draft.content} {draft.instructions}"
    
    # Generate embedding
    embedding = generate_embedding(searchable_text)
    
    # Serialize metadata
    if metadata:
        if hasattr(metadata, "model_dump"):
            metadata_json = json.dumps(metadata.model_dump())
        elif hasattr(metadata, "__dict__"):
            metadata_json = json.dumps(metadata.__dict__)
        else:
            metadata_json = json.dumps({})
    else:
        metadata_json = json.dumps({})
    
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            INSERT OR REPLACE INTO draft_embeddings 
            (draft_id, normalized_message, draft_title, draft_content, embedding, 
             original_message, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            normalized_msg,
            normalized_msg,
            draft.title,
            json.dumps(draft.model_dump()),
            json.dumps(embedding),
            original_message,
            metadata_json
        ))
        await db.commit()
    
    return normalized_msg


async def search_drafts(
    query: str,
    limit: int = 5,
    threshold: float = SIMILARITY_THRESHOLD,
    db_path: str = "backend/checkpoints.db"
) -> List[Dict[str, Any]]:
    """
    Search for drafts using semantic similarity.
    
    Args:
        query: The search query text
        limit: Maximum number of results to return
        threshold: Minimum similarity score (0-1)
        db_path: Path to SQLite database
    
    Returns:
        List of matching drafts with similarity scores, sorted by score descending
    """
    # Generate embedding for query
    query_embedding = generate_embedding(query)
    
    # Fetch all drafts with embeddings
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT draft_id, normalized_message, draft_title, draft_content,
                   embedding, original_message, metadata
            FROM draft_embeddings
        """)
        rows = await cursor.fetchall()
    
    # Extract topics from query for validation
    query_topics = extract_topics(query)
    
    # Calculate similarities
    results = []
    for row in rows:
        stored_embedding = json.loads(row["embedding"])
        similarity = cosine_similarity(query_embedding, stored_embedding)
        
        if similarity >= threshold:
            # Topic validation: if query has topics, ensure draft matches at least one
            if query_topics:
                # Use original message as primary source for topic (most reliable)
                # Also check draft title, but original_message is the source of truth
                draft_title = row['draft_title'] or ''
                original_message = row['original_message'] or ''
                
                # Prioritize original_message for topic extraction (user's original request)
                # This ensures we match based on what the user originally asked for, not edited content
                draft_text_for_topics = f"{original_message} {draft_title}"
                draft_topics = extract_topics(draft_text_for_topics)
                
                # Require at least one topic match - strict validation
                if not query_topics.intersection(draft_topics):
                    continue  # Skip this match - topics don't align
            
            draft_data = json.loads(row["draft_content"])
            metadata_data = json.loads(row["metadata"]) if row["metadata"] else {}
            
            results.append({
                "draft_id": row["draft_id"],
                "normalized_message": row["normalized_message"],
                "draft": draft_data,
                "original_message": row["original_message"],
                "metadata": metadata_data,
                "similarity": similarity,
                "title": row["draft_title"]
            })
    
    # Sort by similarity descending and return top results
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:limit]


async def delete_draft(
    normalized_message: str,
    db_path: str = "backend/checkpoints.db"
):
    """Delete a draft from the vector store."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            DELETE FROM draft_embeddings
            WHERE normalized_message = ?
        """, (normalized_message,))
        await db.commit()


def _normalize_message(message: str) -> str:
    """Normalize user message for consistent key matching."""
    import re
    normalized = message.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)  # Replace multiple spaces with single space
    normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
    return normalized[:200]
