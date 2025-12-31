"""
feature_extractors.py - Base Feature Extraction Functions

Bu modül, soru metni ve şıklardan feature çıkarma fonksiyonlarını içerir.
Tüm fonksiyonlar:
- LLM çağırmaz
- Deterministiktir (aynı input → aynı output)
- Pure Python'dur (harici dependency yok)
"""

from typing import Dict, List, Set, Tuple
from .constants import (
    NEGATIVE_REGEX,
    ROMAN_NUMERAL_PATTERN,
    ARABIC_NUMERAL_PATTERN,
    BULLET_PATTERN,
    FIGURE_REFERENCE_REGEX,
    NUMERIC_PATTERN,
    EXPRESSION_PATTERN,
    TOKEN_SPLIT_PATTERN,
    SENTENCE_END_PATTERN,
    STANDARD_CHOICES,
)


def count_characters(text: str) -> int:
    """Karakter sayısını döndürür (boşluklar dahil)."""
    return len(text)


def count_tokens(text: str) -> int:
    """
    Basit token sayısı.
    Whitespace ve noktalama işaretlerine göre split eder.
    """
    tokens = TOKEN_SPLIT_PATTERN.split(text)
    # Boş string'leri filtrele
    return len([t for t in tokens if t.strip()])


def count_sentences(text: str) -> int:
    """
    Cümle sayısı tahmini.
    . ! ? ile biten bölümleri sayar.
    """
    # Split by sentence endings
    parts = SENTENCE_END_PATTERN.split(text)
    # Filter out empty parts
    sentences = [p.strip() for p in parts if p.strip()]
    # En az 1 cümle var (noktalama olmasa bile)
    return max(1, len(sentences))


def is_negative_question(text: str) -> bool:
    """
    Negatif soru mu?
    "değildir", "yanlıştır", "olamaz", "yoktur" gibi kalıpları arar.
    """
    return bool(NEGATIVE_REGEX.search(text))


def count_premises(text: str) -> int:
    """
    Öncül sayısı proxy'si.
    I, II, III veya 1), 2), 3) gibi kalıpları sayar.
    """
    # Roman numerals
    roman_matches = ROMAN_NUMERAL_PATTERN.findall(text)
    
    # Arabic numerals
    arabic_matches = ARABIC_NUMERAL_PATTERN.findall(text)
    
    # Bullets
    bullet_matches = BULLET_PATTERN.findall(text)
    
    # En yüksek sayıyı döndür (hangisi daha çok varsa)
    counts = [len(roman_matches), len(arabic_matches), len(bullet_matches)]
    return max(counts)


def has_figure(figures_desc: str) -> bool:
    """Şekil/grafik/tablo var mı?"""
    return bool(figures_desc and figures_desc.strip())


def references_figure_in_text(text: str) -> bool:
    """
    Metin içinde şekil/grafik/tablo referansı var mı?
    "şekilde", "grafikte", "tabloda" gibi kalıpları arar.
    """
    return bool(FIGURE_REFERENCE_REGEX.search(text))


def classify_choice_type(choice_text: str) -> str:
    """
    Şık tipini belirle.
    - "numeric": Sadece sayısal değerler
    - "expression": Matematiksel ifadeler (değişkenli)
    - "statement": Metin/ifade
    """
    text = choice_text.strip()
    
    if not text:
        return "empty"
    
    # Check numeric first
    if NUMERIC_PATTERN.match(text):
        return "numeric"
    
    # Check expression
    if EXPRESSION_PATTERN.search(text):
        return "expression"
    
    # Default to statement
    return "statement"


def get_choice_types(choices: Dict[str, str]) -> Dict[str, str]:
    """Tüm şıkların tiplerini döndürür."""
    return {key: classify_choice_type(value) for key, value in choices.items()}


def check_choices_distinct(choices: Dict[str, str]) -> bool:
    """
    Şıklar birbirinden farklı mı?
    Duplicate varsa False döndürür.
    """
    values = [v.strip().lower() for v in choices.values() if v.strip()]
    return len(values) == len(set(values))


def tokenize_text(text: str) -> Set[str]:
    """Metni token set'ine dönüştürür (lowercase)."""
    tokens = TOKEN_SPLIT_PATTERN.split(text.lower())
    return {t for t in tokens if t.strip()}


def calculate_jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """İki set arasındaki Jaccard benzerliğini hesaplar."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def calculate_choice_similarity(choices: Dict[str, str]) -> float:
    """
    Şıklar arası ortalama benzerlik skoru.
    Yüksek değer = şıklar birbirine çok benziyor (kötü)
    """
    choice_values = [v for v in choices.values() if v.strip()]
    
    if len(choice_values) < 2:
        return 0.0
    
    # Tokenize all choices
    tokenized = [tokenize_text(v) for v in choice_values]
    
    # Calculate pairwise Jaccard similarities
    similarities = []
    for i in range(len(tokenized)):
        for j in range(i + 1, len(tokenized)):
            sim = calculate_jaccard_similarity(tokenized[i], tokenized[j])
            similarities.append(sim)
    
    return sum(similarities) / len(similarities) if similarities else 0.0


def extract_all_features(
    question_text: str,
    choices: Dict[str, str],
    figures_desc: str
) -> Dict:
    """
    Tüm base feature'ları çıkarır.
    
    Returns:
        Dict with all extracted features
    """
    return {
        "q_char_len": count_characters(question_text),
        "q_token_len": count_tokens(question_text),
        "q_sentence_count": count_sentences(question_text),
        "is_negative_question": is_negative_question(question_text),
        "premise_count_proxy": count_premises(question_text),
        "has_figure": has_figure(figures_desc),
        "references_figure_in_text": references_figure_in_text(question_text),
        "choice_types": get_choice_types(choices),
        "choices_are_distinct": check_choices_distinct(choices),
        "choice_similarity_score": round(calculate_choice_similarity(choices), 3),
    }
