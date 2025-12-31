"""
standardizer.py - Ana Input Standardization Modülü

Bu modül extract_v1 → standardized_v1 dönüşümünü gerçekleştirir.

Görevler:
1. Metin normalizasyonu (whitespace temizliği)
2. figures_desc standartlaştırma (null → "")
3. Şık varlığı ve format doğrulama
4. Base feature extraction

Önemli: Bu modül LLM çağırmaz. Aynı input → her zaman aynı output.
"""

import re
from typing import Dict, List, Any, Optional
from .constants import STANDARD_CHOICES, SCHEMA_INPUT, SCHEMA_OUTPUT
from .feature_extractors import extract_all_features


def normalize_whitespace(text: str) -> str:
    """
    Whitespace normalizasyonu:
    - Baş/son boşlukları temizle
    - Ardışık boşlukları tekleştir
    - Gereksiz newline'ları normalize et
    """
    if not text:
        return ""
    
    # Normalize newlines to single space
    text = re.sub(r'\n+', ' ', text)
    
    # Collapse multiple spaces to single
    text = re.sub(r' +', ' ', text)
    
    # Trim
    return text.strip()


def normalize_figures_desc(figures_desc: Any) -> str:
    """
    figures_desc normalizasyonu:
    - None/null → ""
    - String → normalize edilmiş string
    """
    if figures_desc is None:
        return ""
    
    if not isinstance(figures_desc, str):
        return ""
    
    return normalize_whitespace(figures_desc)


def validate_and_fill_choices(choices: Optional[Dict[str, str]]) -> tuple[Dict[str, str], List[str], bool]:
    """
    Şıkları doğrula ve eksikleri doldur.
    
    Returns:
        Tuple of:
        - normalized_choices: A-E tamamlanmış şıklar
        - missing_choices: Eksik şık listesi
        - format_valid: Format geçerli mi
    """
    if choices is None:
        choices = {}
    
    normalized = {}
    missing = []
    
    for choice_key in STANDARD_CHOICES:
        if choice_key in choices and choices[choice_key]:
            normalized[choice_key] = normalize_whitespace(str(choices[choice_key]))
        else:
            normalized[choice_key] = ""
            missing.append(choice_key)
    
    # Format is valid only if all A-E exist and are non-empty
    format_valid = len(missing) == 0
    
    return normalized, missing, format_valid


def normalize_question_text(question_text: Any) -> str:
    """Soru metnini normalize et."""
    if question_text is None:
        return ""
    
    if not isinstance(question_text, str):
        return str(question_text)
    
    return normalize_whitespace(question_text)


def standardize(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ana standardizasyon fonksiyonu.
    
    extract_v1 → standardized_v1 dönüşümü yapar.
    
    Args:
        input_data: extract_v1 formatında soru verisi
        
    Returns:
        standardized_v1 formatında normalize edilmiş veri
        
    Example:
        >>> input_data = {
        ...     "schema": "extract_v1",
        ...     "id": "q_001",
        ...     "question_text": "Aşağıdakilerden hangisi yanlıştır?",
        ...     "choices": {"A": "Seçenek 1", "B": "Seçenek 2", ...},
        ...     "figures_desc": null
        ... }
        >>> result = standardize(input_data)
        >>> result["schema"]
        'standardized_v1'
    """
    # Extract fields with defaults
    question_id = input_data.get("id", "unknown")
    raw_question = input_data.get("question_text", "")
    raw_choices = input_data.get("choices", {})
    raw_figures = input_data.get("figures_desc")
    extraction_confidence = input_data.get("extraction_confidence", 1.0)
    extraction_notes = input_data.get("extraction_notes", "")
    
    # Normalize
    normalized_question = normalize_question_text(raw_question)
    normalized_figures = normalize_figures_desc(raw_figures)
    normalized_choices, missing_choices, choices_valid = validate_and_fill_choices(raw_choices)
    
    # Validation warnings
    warnings = []
    
    if not normalized_question:
        warnings.append("question_text is empty")
    
    if missing_choices:
        warnings.append(f"missing choices: {', '.join(missing_choices)}")
    
    if extraction_confidence < 0.5:
        warnings.append(f"low extraction confidence: {extraction_confidence}")
    
    # Extract base features
    base_features = extract_all_features(
        question_text=normalized_question,
        choices=normalized_choices,
        figures_desc=normalized_figures
    )
    
    # Add format_valid to features
    base_features["format_valid"] = choices_valid and bool(normalized_question)
    
    # Build output
    return {
        "schema": SCHEMA_OUTPUT,
        "id": question_id,
        "normalized": {
            "question_text": normalized_question,
            "choices": normalized_choices,
            "figures_desc": normalized_figures,
        },
        "base_features": base_features,
        "validation": {
            "format_valid": choices_valid and bool(normalized_question),
            "missing_choices": missing_choices,
            "warnings": warnings,
        },
        "metadata": {
            "extraction_confidence": extraction_confidence,
            "extraction_notes": normalize_whitespace(str(extraction_notes)) if extraction_notes else "",
        }
    }


def batch_standardize(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Birden fazla soruyu batch olarak standardize et.
    
    Args:
        items: extract_v1 formatında soru listesi
        
    Returns:
        standardized_v1 formatında normalize edilmiş liste
    """
    return [standardize(item) for item in items]
