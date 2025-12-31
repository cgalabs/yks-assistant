"""
clarity_guard.py - Clarity & Validity Guard Module

LLM'siz, rule-based soru kalite kontrolü.

Görevler:
1. format_valid — A-E var mı, duplicate var mı, metin yeterli mi
2. clarity — muğlaklık proxy'leri (şekil referansı tutarsızlığı vb.)
3. single_answer_likelihood — tek doğru cevap olasılığı proxy
4. risk_flags — tespit edilen sorunların listesi

Bu modül %95 problemi LLM olmadan yakalar.
Sadece belirsiz durumlarda escalation yapılır (opsiyonel).
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    """Risk seviyeleri."""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class GuardResult:
    """Clarity Guard sonucu."""
    passed: bool
    format_valid: float  # 0-1 arası skor
    clarity: float  # 0-1 arası skor
    single_answer_likelihood: float  # 0-1 arası skor
    risk_flags: List[str] = field(default_factory=list)
    reason_short: str = ""
    needs_escalation: bool = False  # LLM escalation gerekiyor mu?
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pass": self.passed,
            "format_valid": round(self.format_valid, 2),
            "clarity": round(self.clarity, 2),
            "single_answer_likelihood": round(self.single_answer_likelihood, 2),
            "risk_flags": self.risk_flags,
            "reason_short": self.reason_short,
            "needs_escalation": self.needs_escalation
        }


# ============================================================================
# RISK FLAGS (Tespit edilebilecek sorunlar)
# ============================================================================

# Format sorunları
RISK_QUESTION_TOO_SHORT = "QUESTION_TOO_SHORT"
RISK_QUESTION_EMPTY = "QUESTION_EMPTY"
RISK_MISSING_CHOICES = "MISSING_CHOICES"
RISK_EMPTY_CHOICES = "EMPTY_CHOICES"
RISK_DUPLICATE_CHOICES = "DUPLICATE_CHOICES"
RISK_HIGH_CHOICE_SIMILARITY = "HIGH_CHOICE_SIMILARITY"
RISK_UNIFORM_CHOICE_LENGTH = "UNIFORM_CHOICE_LENGTH"

# Clarity sorunları
RISK_FIGURE_PRESENT_NO_REFERENCE = "FIGURE_PRESENT_NO_REFERENCE"
RISK_FIGURE_REFERENCED_BUT_MISSING = "FIGURE_REFERENCED_BUT_MISSING"
RISK_HIGH_PREMISE_SHORT_STEM = "HIGH_PREMISE_SHORT_STEM"
RISK_ALL_CHOICES_SINGLE_TOKEN = "ALL_CHOICES_SINGLE_TOKEN"
RISK_LONG_TEXT_NO_MATH = "LONG_TEXT_NO_MATH"
RISK_NEGATIVE_QUESTION_NUMERIC_CHOICES = "NEGATIVE_QUESTION_NUMERIC_CHOICES"

# Single answer sorunları
RISK_NEAR_IDENTICAL_NUMERIC = "NEAR_IDENTICAL_NUMERIC"


# ============================================================================
# THRESHOLDS (Eşik değerleri)
# ============================================================================

MIN_QUESTION_LENGTH = 15  # Minimum karakter sayısı
HIGH_SIMILARITY_THRESHOLD = 0.85  # Şık benzerliği eşiği
UNIFORM_LENGTH_VARIANCE = 0.1  # Şık uzunluğu varyansı eşiği
HIGH_PREMISE_THRESHOLD = 3  # Yüksek öncül sayısı
SHORT_STEM_THRESHOLD = 50  # Kısa soru kökü (karakter)
LONG_TEXT_THRESHOLD = 300  # Uzun metin eşiği
SINGLE_TOKEN_MAX_LEN = 5  # Tek token kabul edilen max karakter


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_ordering_question(question_text: str, choices: Dict[str, str]) -> bool:
    """
    Sıralama sorusu mu? (Şıklar aynı elemanları farklı sırada içerir)
    Bu tip sorularda yüksek similarity **beklenir** ve sorun değildir.
    """
    import re
    
    # Soru metninde sıralama ipuçları
    ordering_keywords = [
        r'\bsıralama\b', r'\bsırala\b', r'\bhangisi\s+doğru\b',
        r'\büçten\s+küçüğe\b', r'\bküçükten\s+büyüğe\b',
        r'\bartan\b', r'\bazalan\b', r'\bdoğru\s+sıra\b',
    ]
    has_ordering_keyword = any(re.search(p, question_text, re.IGNORECASE) for p in ordering_keywords)
    
    # Şıklarda < veya > sembolleri varsa (karşılaştırma/sıralama sorusu)
    comparison_operators = ['<', '>', '≤', '≥']
    choices_have_comparison = all(
        any(op in v for op in comparison_operators) 
        for v in choices.values() if v.strip()
    )
    
    return has_ordering_keyword or choices_have_comparison


# ============================================================================
# FORMAT VALIDATION (Rule-based)
# ============================================================================

def check_format_valid(
    normalized: Dict[str, Any],
    base_features: Dict[str, Any]
) -> Tuple[float, List[str]]:
    """
    Format geçerliliğini kontrol et.
    
    Returns:
        Tuple of (score, risk_flags)
        score: 0-1 arası (1 = tam geçerli)
    """
    flags = []
    penalties = 0.0
    
    question_text = normalized.get("question_text", "")
    choices = normalized.get("choices", {})
    
    # 1. Soru metni kontrolü
    if not question_text:
        flags.append(RISK_QUESTION_EMPTY)
        penalties += 1.0
    elif len(question_text) < MIN_QUESTION_LENGTH:
        flags.append(RISK_QUESTION_TOO_SHORT)
        penalties += 0.5
    
    # 2. Eksik şık kontrolü
    missing_choices = [k for k, v in choices.items() if not v.strip()]
    if missing_choices:
        flags.append(RISK_MISSING_CHOICES)
        penalties += 0.2 * len(missing_choices)
    
    # 3. Boş şık kontrolü (format_valid from base_features)
    if not base_features.get("format_valid", True):
        flags.append(RISK_EMPTY_CHOICES)
        penalties += 0.3
    
    # 4. Duplicate şık kontrolü
    if not base_features.get("choices_are_distinct", True):
        flags.append(RISK_DUPLICATE_CHOICES)
        penalties += 0.5
    
    # 5. Yüksek şık benzerliği (sıralama soruları hariç)
    similarity = base_features.get("choice_similarity_score", 0)
    is_ordering = is_ordering_question(question_text, choices)
    
    if similarity > HIGH_SIMILARITY_THRESHOLD and not is_ordering:
        flags.append(RISK_HIGH_CHOICE_SIMILARITY)
        penalties += 0.3
    
    # 6. Uniform şık uzunluğu (sıralama soruları hariç - kopya/kalıp üretim sinyali)
    choice_lengths = [len(v) for v in choices.values() if v.strip()]
    if len(choice_lengths) >= 3 and not is_ordering:
        avg_len = sum(choice_lengths) / len(choice_lengths)
        if avg_len > 0:
            variance = sum((l - avg_len) ** 2 for l in choice_lengths) / len(choice_lengths)
            normalized_variance = variance / (avg_len ** 2) if avg_len > 0 else 0
            if normalized_variance < UNIFORM_LENGTH_VARIANCE and all(l == choice_lengths[0] for l in choice_lengths):
                flags.append(RISK_UNIFORM_CHOICE_LENGTH)
                penalties += 0.2
    
    # 7. Negatif soru + sayısal şıklar (heuristic)
    if base_features.get("is_negative_question", False):
        choice_types = base_features.get("choice_types", {})
        numeric_count = sum(1 for t in choice_types.values() if t == "numeric")
        if numeric_count >= 4:  # 4+ şık sayısal
            flags.append(RISK_NEGATIVE_QUESTION_NUMERIC_CHOICES)
            penalties += 0.2
    
    # Score hesapla (max 1, min 0)
    score = max(0.0, 1.0 - penalties)
    
    return score, flags


# ============================================================================
# CLARITY CHECK (Muğlaklık proxy'leri)
# ============================================================================

def check_clarity(
    normalized: Dict[str, Any],
    base_features: Dict[str, Any]
) -> Tuple[float, List[str]]:
    """
    Muğlaklık proxy kontrolü.
    
    Returns:
        Tuple of (score, risk_flags)
        score: 0-1 arası (1 = net/açık)
    """
    flags = []
    penalties = 0.0
    
    question_text = normalized.get("question_text", "")
    figures_desc = normalized.get("figures_desc", "")
    choices = normalized.get("choices", {})
    
    has_figure = base_features.get("has_figure", False)
    references_figure = base_features.get("references_figure_in_text", False)
    premise_count = base_features.get("premise_count_proxy", 0)
    q_char_len = base_features.get("q_char_len", 0)
    
    # 1. Şekil var ama metinde referans yok
    if has_figure and not references_figure:
        flags.append(RISK_FIGURE_PRESENT_NO_REFERENCE)
        penalties += 0.3
    
    # 2. Metinde şekil referansı var ama figures_desc boş
    if references_figure and not has_figure:
        flags.append(RISK_FIGURE_REFERENCED_BUT_MISSING)
        penalties += 0.5
    
    # 3. Yüksek öncül + kısa soru kökü (kırpılmış OCR riski)
    if premise_count >= HIGH_PREMISE_THRESHOLD and q_char_len < SHORT_STEM_THRESHOLD:
        flags.append(RISK_HIGH_PREMISE_SHORT_STEM)
        penalties += 0.3
    
    # 4. Tüm şıklar çok kısa (tek kelime/sayı)
    choice_values = [v for v in choices.values() if v.strip()]
    if choice_values:
        all_short = all(len(v.strip()) <= SINGLE_TOKEN_MAX_LEN for v in choice_values)
        if all_short:
            flags.append(RISK_ALL_CHOICES_SINGLE_TOKEN)
            penalties += 0.2
    
    # 5. Uzun metin + hiç matematiksel token yok
    if q_char_len > LONG_TEXT_THRESHOLD:
        # Basit math token kontrolü
        import re
        math_pattern = r'[=<>+\-*/²³√πΣ∫∞≤≥≠∈∉⊂⊃∪∩]|\d+[.,]?\d*'
        has_math = bool(re.search(math_pattern, question_text))
        if not has_math:
            flags.append(RISK_LONG_TEXT_NO_MATH)
            penalties += 0.15
    
    score = max(0.0, 1.0 - penalties)
    
    return score, flags


# ============================================================================
# SINGLE ANSWER LIKELIHOOD (Proxy)
# ============================================================================

def check_single_answer_likelihood(
    normalized: Dict[str, Any],
    base_features: Dict[str, Any]
) -> Tuple[float, List[str]]:
    """
    Tek doğru cevap olasılığı proxy.
    
    Returns:
        Tuple of (score, risk_flags)
        score: 0-1 arası (1 = kesinlikle tek doğru var)
    """
    flags = []
    penalties = 0.0
    
    choices = normalized.get("choices", {})
    similarity = base_features.get("choice_similarity_score", 0)
    choices_distinct = base_features.get("choices_are_distinct", True)
    choice_types = base_features.get("choice_types", {})
    
    # 1. Duplicate varsa → çok düşük
    if not choices_distinct:
        penalties += 0.5
    
    # 2. Yüksek benzerlik → düşür
    if similarity > 0.7:
        penalties += 0.2 * (similarity - 0.7) / 0.3
    
    # 3. Numeric şıklarda yakın değer kümelenmesi
    if all(t == "numeric" for t in choice_types.values()):
        # Sayısal değerleri çıkar
        import re
        numeric_values = []
        for v in choices.values():
            match = re.search(r'[\d.,]+', v)
            if match:
                try:
                    val = float(match.group().replace(',', '.'))
                    numeric_values.append(val)
                except ValueError:
                    pass
        
        # Aynı değer var mı?
        if len(numeric_values) >= 2:
            unique_vals = set(numeric_values)
            if len(unique_vals) < len(numeric_values):
                flags.append(RISK_NEAR_IDENTICAL_NUMERIC)
                penalties += 0.4
    
    score = max(0.0, 1.0 - penalties)
    
    return score, flags


# ============================================================================
# MAIN GUARD FUNCTION
# ============================================================================

def evaluate_guard(standardized_data: Dict[str, Any]) -> GuardResult:
    """
    Ana Clarity Guard fonksiyonu.
    
    Args:
        standardized_data: standardized_v1 formatında veri
        
    Returns:
        GuardResult objesi
    """
    normalized = standardized_data.get("normalized", {})
    base_features = standardized_data.get("base_features", {})
    
    # Her kontrolü çalıştır
    format_score, format_flags = check_format_valid(normalized, base_features)
    clarity_score, clarity_flags = check_clarity(normalized, base_features)
    single_answer_score, single_flags = check_single_answer_likelihood(normalized, base_features)
    
    # Tüm flag'leri birleştir
    all_flags = format_flags + clarity_flags + single_flags
    
    # Pass/fail kararı
    # FAIL: format çok kötü veya kritik clarity sorunu
    critical_flags = {
        RISK_QUESTION_EMPTY, RISK_DUPLICATE_CHOICES, 
        RISK_FIGURE_REFERENCED_BUT_MISSING
    }
    has_critical = any(f in critical_flags for f in all_flags)
    
    passed = format_score > 0.5 and not has_critical
    
    # Escalation kararı
    # Format OK ama clarity WARN ve single_answer LOW → LLM gerekli
    needs_escalation = (
        format_score > 0.7 and
        clarity_score < 0.7 and
        single_answer_score < 0.6 and
        not has_critical
    )
    
    # Reason oluştur
    reason_parts = []
    if format_flags:
        reason_parts.append(f"Format sorunları: {', '.join(format_flags)}")
    if clarity_flags:
        reason_parts.append(f"Netlik sorunları: {', '.join(clarity_flags)}")
    if single_flags:
        reason_parts.append(f"Tek cevap riski: {', '.join(single_flags)}")
    
    if not reason_parts:
        reason_short = "Tüm kontroller geçti."
    else:
        reason_short = "; ".join(reason_parts)
    
    return GuardResult(
        passed=passed,
        format_valid=format_score,
        clarity=clarity_score,
        single_answer_likelihood=single_answer_score,
        risk_flags=all_flags,
        reason_short=reason_short,
        needs_escalation=needs_escalation
    )


def guard_question(standardized_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience wrapper - dict döndürür.
    """
    result = evaluate_guard(standardized_data)
    return result.to_dict()
