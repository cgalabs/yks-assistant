"""
osym_similarity.py - ÖSYM Similarity Score Module

Bu modül, bir sorunun ÖSYM tarzı sorulara ne kadar benzediğini ölçer.

Amaç: "Bu soru ÖSYM'nin dağılımına benziyor mu?"

Bu bir estetik değerlendirme değil, **feature distribution matching**.

Feature Set:
- Dil: kelime/cümle uzunluğu, bağlaç oranı
- Yapı: öncül→sonuç, "hangisi/doğru/yanlıştır" kalıpları
- Negatif soru flag'i
- Şekil/graph/table flag'i
- Şık stili: sayısal mı, ifadeli mi, statement mı

Çıktı:
- osym_similarity ∈ [0,1]
- top_feature_gaps[] (neden düşük/yüksek)
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
import re


@dataclass
class SimilarityResult:
    """ÖSYM Similarity sonucu."""
    osym_similarity: float  # 0-1 arası skor
    feature_scores: Dict[str, float] = field(default_factory=dict)
    top_feature_gaps: List[str] = field(default_factory=list)
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "osym_similarity": round(self.osym_similarity, 2),
            "feature_scores": {k: round(v, 2) for k, v in self.feature_scores.items()},
            "top_feature_gaps": self.top_feature_gaps,
            "reasoning": self.reasoning
        }


# ============================================================================
# ÖSYM REFERENCE DISTRIBUTIONS (Typical ÖSYM question characteristics)
# ============================================================================
# Bu değerler ÖSYM sınav analizlerinden çıkarılmış tipik değerlerdir.
# Gerçek implementasyonda bu değerler veri setinden hesaplanmalı.

OSYM_REFERENCE = {
    # Soru metni uzunluğu (karakter)
    "q_char_len": {
        "min": 50,      # Çok kısa sorular nadir
        "optimal_min": 100,
        "optimal_max": 350,
        "max": 500      # Çok uzun sorular nadir
    },
    
    # Token sayısı
    "q_token_len": {
        "min": 10,
        "optimal_min": 20,
        "optimal_max": 60,
        "max": 100
    },
    
    # Cümle sayısı
    "q_sentence_count": {
        "min": 1,
        "optimal_min": 2,
        "optimal_max": 5,
        "max": 8
    },
    
    # Negatif soru oranı (ÖSYM'de %20-30 civarı negatif soru var)
    "negative_question_ratio": 0.25,
    
    # Şekil/grafik oranı (ÖSYM'de %30-40 civarı görsel soru)
    "figure_ratio": 0.35,
    
    # Öncül soruları oranı (I, II, III tipi - %15-25)
    "premise_question_ratio": 0.20,
    
    # Şık tipi dağılımı (tipik ÖSYM sorusu)
    "choice_type_distribution": {
        "statement": 0.50,   # İfade/cümle şıkları
        "numeric": 0.35,     # Sayısal şıklar
        "expression": 0.15   # Matematiksel ifade şıkları
    }
}

# ÖSYM kalıp ifadeleri (soru kökünde beklenen)
OSYM_STEM_PATTERNS = [
    r'\başağıdakilerden\s+hangisi\b',
    r'\bhangisi\s+doğrudur\b',
    r'\bhangisi\s+yanlıştır\b',
    r'\bbuna\s+göre\b',
    r'\byukarıda\s+verilen\b',
    r'\başağıda\s+verilen\b',
    r'\byukarıdaki\b',
    r'\başağıdaki\b',
    r'\bhangileri\b',
    r'\byalnız\b',
    r'\ben\s+az\b',
    r'\ben\s+çok\b',
    r'\ben\s+fazla\b',
    r'\bkaç\s+tanesi\b',
    r'\bkaçıdır\b',
    r'\bkaçtır\b',
]

# ÖSYM bağlaç ve geçiş kelimeleri
OSYM_CONNECTORS = [
    r'\bve\b', r'\bveya\b', r'\bfakat\b', r'\bama\b', r'\bçünkü\b',
    r'\bdolayısıyla\b', r'\böyleyse\b', r'\bise\b', r'\bile\b',
    r'\bbuna\s+karşın\b', r'\böte\s+yandan\b', r'\bsonuç\s+olarak\b',
]


# ============================================================================
# FEATURE SCORING FUNCTIONS
# ============================================================================

def score_in_range(value: float, ref: Dict[str, float]) -> float:
    """
    Değerin referans aralığına uygunluğunu skorla.
    Artık 'flat' bir 1.0 yok. Optimal aralığın ortası 1.0, kenarlara doğru azalır.
    Bu sayede herkes %100 alamaz.
    """
    opt_min = ref["optimal_min"]
    opt_max = ref["optimal_max"]
    
    # Target is the center of the optimal range
    target = (opt_min + opt_max) / 2
    
    # If inside optimal range, score 0.90 - 1.0 based on distance to center
    if opt_min <= value <= opt_max:
        # Normalize distance to 0-1 within the half-range
        half_range = (opt_max - opt_min) / 2
        distance = abs(value - target)
        ratio = 1.0 - (distance / (half_range + 0.001)) # avoid div/0
        return 0.90 + (0.10 * ratio) # 0.90 at edges, 1.0 at center
        
    # If outside optimal but inside acceptable
    if ref["min"] <= value < opt_min:
        # 0.5 to 0.9
        ratio = (value - ref["min"]) / (opt_min - ref["min"])
        return 0.5 + (0.4 * ratio)
        
    if opt_max < value <= ref["max"]:
        # 0.9 to 0.5
        ratio = (ref["max"] - value) / (ref["max"] - opt_max)
        return 0.5 + (0.4 * ratio)
        
    # Outside acceptable
    return 0.0


def score_char_length(base_features: Dict[str, Any]) -> Tuple[float, str]:
    """Karakter uzunluğu skoru."""
    q_char_len = base_features.get("q_char_len", 0)
    score = score_in_range(q_char_len, OSYM_REFERENCE["q_char_len"])
    
    if score < 0.7:
        if q_char_len < OSYM_REFERENCE["q_char_len"]["optimal_min"]:
            gap = f"Soru çok kısa ({q_char_len} karakter). ÖSYM'de tipik: 100-350"
        else:
            gap = f"Soru çok uzun ({q_char_len} karakter). ÖSYM'de tipik: 100-350"
    else:
        gap = ""
    
    return score, gap


def score_token_length(base_features: Dict[str, Any]) -> Tuple[float, str]:
    """Token sayısı skoru."""
    q_token_len = base_features.get("q_token_len", 0)
    score = score_in_range(q_token_len, OSYM_REFERENCE["q_token_len"])
    
    if score < 0.7:
        if q_token_len < OSYM_REFERENCE["q_token_len"]["optimal_min"]:
            gap = f"Token sayısı düşük ({q_token_len}). ÖSYM'de tipik: 20-60"
        else:
            gap = f"Token sayısı yüksek ({q_token_len}). ÖSYM'de tipik: 20-60"
    else:
        gap = ""
    
    return score, gap


def score_sentence_count(base_features: Dict[str, Any]) -> Tuple[float, str]:
    """Cümle sayısı skoru."""
    q_sentence_count = base_features.get("q_sentence_count", 0)
    score = score_in_range(q_sentence_count, OSYM_REFERENCE["q_sentence_count"])
    
    if score < 0.7:
        gap = f"Cümle sayısı atipik ({q_sentence_count}). ÖSYM'de tipik: 2-5"
    else:
        gap = ""
    
    return score, gap


def score_stem_patterns(question_text: str) -> Tuple[float, str]:
    """
    Soru kökü kalıpları skoru.
    ÖSYM tipik kalıplarından kaç tanesi kullanılmış?
    """
    matches = 0
    for pattern in OSYM_STEM_PATTERNS:
        if re.search(pattern, question_text, re.IGNORECASE):
            matches += 1
    
    # En az 1 kalıp eşleşmeli
    if matches >= 3:
        score = 1.0
    elif matches == 2:
        score = 0.9
    elif matches == 1:
        score = 0.75
    else:
        score = 0.4
    
    if score < 0.7:
        gap = "ÖSYM tipik soru kalıpları eksik (hangisi, buna göre, vb.)"
    else:
        gap = ""
    
    return score, gap


def score_connectors(question_text: str) -> Tuple[float, str]:
    """
    Bağlaç kullanımı skoru.
    ÖSYM soruları genellikle iyi yapılandırılmış, bağlaçlı cümleler içerir.
    """
    matches = 0
    for pattern in OSYM_CONNECTORS:
        if re.search(pattern, question_text, re.IGNORECASE):
            matches += 1
    
    q_len = len(question_text)
    
    # Uzun sorularda daha fazla bağlaç beklenir
    if q_len > 200:
        expected_connectors = 2
    elif q_len > 100:
        expected_connectors = 1
    else:
        expected_connectors = 0
    
    if matches >= expected_connectors:
        score = 1.0
    elif matches > 0:
        score = 0.7
    else:
        score = 0.5 if q_len < 100 else 0.3
    
    gap = ""  # Bağlaç eksikliği genellikle kritik değil
    
    return score, gap


def score_choice_types(base_features: Dict[str, Any]) -> Tuple[float, str]:
    """
    Şık tipi tutarlılığı skoru.
    ÖSYM'de genellikle tüm şıklar aynı tipte.
    """
    choice_types = base_features.get("choice_types", {})
    
    if not choice_types:
        return 0.5, ""
    
    type_counts = {}
    for t in choice_types.values():
        type_counts[t] = type_counts.get(t, 0) + 1
    
    # En sık kullanılan tipin oranı
    max_count = max(type_counts.values()) if type_counts else 0
    total = sum(type_counts.values())
    
    if total == 0:
        return 0.5, ""
    
    homogeneity = max_count / total
    
    # ÖSYM'de şıklar genellikle homojen
    if homogeneity >= 0.8:
        score = 1.0
    elif homogeneity >= 0.6:
        score = 0.8
    else:
        score = 0.5
    
    if score < 0.7:
        gap = "Şık tipleri karışık (ÖSYM'de genellikle homojen)"
    else:
        gap = ""
    
    return score, gap


def score_figure_consistency(base_features: Dict[str, Any]) -> Tuple[float, str]:
    """
    Şekil-metin tutarlılığı skoru.
    Şekil varsa referans olmalı, yoksa olmamalı.
    """
    has_figure = base_features.get("has_figure", False)
    references_figure = base_features.get("references_figure_in_text", False)
    
    # Tutarlılık kontrolü
    if has_figure and references_figure:
        score = 1.0
        gap = ""
    elif not has_figure and not references_figure:
        score = 1.0
        gap = ""
    elif has_figure and not references_figure:
        score = 0.6
        gap = "Şekil var ama metinde referans yok"
    else:  # references_figure and not has_figure
        score = 0.4
        gap = "Metinde şekil referansı var ama şekil yok"
    
    return score, gap


def score_premise_structure(base_features: Dict[str, Any]) -> Tuple[float, str]:
    """
    Öncül yapısı skoru.
    I, II, III tipi sorularda yapı ÖSYM'ye uygun mu?
    """
    premise_count = base_features.get("premise_count_proxy", 0)
    q_char_len = base_features.get("q_char_len", 0)
    
    if premise_count == 0:
        # Öncül yoksa → nötr
        return 1.0, ""
    
    # Öncül varsa, soru yeterince uzun olmalı
    if premise_count >= 3 and q_char_len < 80:
        score = 0.5
        gap = "Çok öncül ama kısa soru (OCR/kırpma riski)"
    elif premise_count >= 2 and q_char_len >= 100:
        score = 1.0
        gap = ""
    else:
        score = 0.8
        gap = ""
    
    return score, gap


# ============================================================================
# MAIN SIMILARITY FUNCTION
# ============================================================================

def calculate_similarity(standardized_data: Dict[str, Any]) -> SimilarityResult:
    """
    Ana ÖSYM benzerlik hesaplama fonksiyonu.
    
    Args:
        standardized_data: standardized_v1 formatında veri
        
    Returns:
        SimilarityResult objesi
    """
    normalized = standardized_data.get("normalized", {})
    base_features = standardized_data.get("base_features", {})
    question_text = normalized.get("question_text", "")
    
    # Her feature'ı skorla
    feature_scores = {}
    gaps = []
    
    # 1. Karakter uzunluğu
    score, gap = score_char_length(base_features)
    feature_scores["char_length"] = score
    if gap:
        gaps.append(gap)
    
    # 2. Token uzunluğu
    score, gap = score_token_length(base_features)
    feature_scores["token_length"] = score
    if gap:
        gaps.append(gap)
    
    # 3. Cümle sayısı
    score, gap = score_sentence_count(base_features)
    feature_scores["sentence_count"] = score
    if gap:
        gaps.append(gap)
    
    # 4. Soru kalıpları
    score, gap = score_stem_patterns(question_text)
    feature_scores["stem_patterns"] = score
    if gap:
        gaps.append(gap)
    
    # 5. Bağlaç kullanımı
    score, gap = score_connectors(question_text)
    feature_scores["connectors"] = score
    if gap:
        gaps.append(gap)
    
    # 6. Şık tipi tutarlılığı
    score, gap = score_choice_types(base_features)
    feature_scores["choice_types"] = score
    if gap:
        gaps.append(gap)
    
    # 7. Şekil tutarlılığı
    score, gap = score_figure_consistency(base_features)
    feature_scores["figure_consistency"] = score
    if gap:
        gaps.append(gap)
    
    # 8. Öncül yapısı
    score, gap = score_premise_structure(base_features)
    feature_scores["premise_structure"] = score
    if gap:
        gaps.append(gap)
    
    # Ağırlıklı ortalama hesapla
    weights = {
        "char_length": 1.0,
        "token_length": 0.8,
        "sentence_count": 0.6,
        "stem_patterns": 1.5,  # Kalıplar önemli
        "connectors": 0.5,
        "choice_types": 1.0,
        "figure_consistency": 1.2,
        "premise_structure": 0.8,
    }
    
    total_weight = sum(weights.values())
    weighted_sum = sum(feature_scores[k] * weights[k] for k in feature_scores)
    osym_similarity = weighted_sum / total_weight
    
    # Reasoning oluştur
    if osym_similarity >= 0.90:
        base_msg = "Mükemmel! Soru ÖSYM standartlarına birebir uyumlu."
    elif osym_similarity >= 0.80:
        base_msg = "Çok Başarılı. Soru ÖSYM dil ve yapısına oldukça yakın."
    elif osym_similarity >= 0.70:
        base_msg = "İyi. Genel yapı uygun ancak bazı pürüzler var."
    elif osym_similarity >= 0.50:
        base_msg = "Orta. ÖSYM tarzından belirgin sapmalar mevcut."
    else:
        base_msg = "Zayıf. Soru yapısı ve dili ÖSYM standartlarından uzak."

    # Add specific gaps to reasoning
    if gaps:
        gap_text = " Tespit edilen eksikler: " + ", ".join(gaps[:2]) + "."
        reasoning = base_msg + gap_text
    else:
        reasoning = base_msg
    
    return SimilarityResult(
        osym_similarity=osym_similarity,
        feature_scores=feature_scores,
        top_feature_gaps=gaps[:3],  # En önemli 3 gap
        reasoning=reasoning
    )


def osym_similarity_score(standardized_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience wrapper - dict döndürür.
    """
    result = calculate_similarity(standardized_data)
    return result.to_dict()
