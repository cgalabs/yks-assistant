"""
Anchor Selector - Selects random anchor questions from DB based on topic.
"""

import sqlite3
import json
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "questions.db")


def get_random_anchors(
    topic: str,
    k: int = 5
) -> list[dict]:
    """
    Get k random anchor questions for a given topic.
    """
    if not os.path.exists(DB_PATH):
        print(f"[WARN] DB_PATH not found: {DB_PATH}")
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query
    query = "SELECT * FROM questions WHERE topic = ? ORDER BY RANDOM() LIMIT ?"
    params = [topic, k]
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Fallback: If no questions found, try similar topics
    if not rows:
        similar_topics = _get_similar_topics(topic)
        for similar_topic in similar_topics:
            fallback_query = "SELECT * FROM questions WHERE topic = ? ORDER BY RANDOM() LIMIT ?"
            cursor.execute(fallback_query, [similar_topic, k])
            rows = cursor.fetchall()
            if rows:
                break
    
    # Last resort: Get any random questions
    if not rows:
        cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", [k])
        rows = cursor.fetchall()
    
    conn.close()
    
    # Convert to list of dicts
    anchors = []
    for row in rows:
        anchor = dict(row)
        # Parse choices if it's a JSON string
        if anchor.get("choices"):
            try:
                anchor["choices"] = json.loads(anchor["choices"])
            except:
                pass
        anchors.append(anchor)
    
    return anchors


def _get_similar_topics(topic: str) -> list[str]:
    """
    Get similar topics based on keyword matching.
    """
    similar_map = {
        "yüzde problemleri": ["oran - orantı", "kesir problemleri", "kar-zarar, yüzde, karışım, hareket problemleri"],
        "oran - orantı": ["yüzde problemleri", "kesir problemleri", "sayı problemleri"],
        "kesir problemleri": ["yüzde problemleri", "oran - orantı", "rasyonel sayılar"],
        "fonksiyonlar": ["fonksiyonun tersi", "fonksiyon kavramı ve özellikleri"],
        "hız problemleri": ["işçi problemleri", "kar-zarar, yüzde, karışım, hareket problemleri"],
        "işçi problemleri": ["hız problemleri", "sayı problemleri"],
    }
    return similar_map.get(topic, ["oran - orantı", "fonksiyonlar"])


def format_anchors_for_prompt(anchors: list[dict]) -> str:
    """
    Format anchor questions into a string for the LLM prompt.
    """
    formatted = []
    
    for i, anchor in enumerate(anchors, 1):
        parts = [f"### Örnek Soru {i}"]
        
        # Problem text
        if anchor.get("problem_text"):
            parts.append(f"**Soru:** {anchor['problem_text']}")
        
        # Answer choices
        choices = anchor.get("choices", {})
        if choices:
            if isinstance(choices, dict):
                choices_str = "\n".join([f"{k}) {v}" for k, v in sorted(choices.items())])
                parts.append(f"**Şıklar:**\n{choices_str}")
        
        # Solution (optional)
        if anchor.get("solution_steps"):
            try:
                steps = json.loads(anchor["solution_steps"])
                solution = "\n".join(steps)
                parts.append(f"**Çözüm:** {solution[:500]}")
            except:
                 parts.append(f"**Çözüm:** {anchor['solution_steps'][:500]}")
        
        # Correct answer
        if anchor.get("final_answer"):
            parts.append(f"**Doğru Cevap:** {anchor['final_answer']}")
        elif anchor.get("answer_key"):
            parts.append(f"**Doğru Cevap:** {anchor['answer_key']}")
        
        formatted.append("\n".join(parts))
    
    return "\n\n---\n\n".join(formatted)
