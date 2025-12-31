"""
cognitive_signature.py - Cognitive Signature Module

Bu modül, sorunun bilişsel imzasını belirler.

Amaç: "Bu soru hangi bilişsel becerileri ölçüyor?"

Etiket Seti (basit ama güçlü):
- computation_heavy: Hesaplama ağırlıklı (çok adım işlem)
- concept_heavy: Kavram ağırlıklı (tanım, özellik bilgisi)
- relation_building: İlişki kurma (karşılaştırma, analiz)
- reading_trap: Okuma tuzağı ("en az/en çok" gibi dikkat gerektiren)
- time_sink: Zaman yutucusu (uzun/karmaşık)
- pattern_recognition: Örüntü tanıma (seri, dizi, grafik yorumu)

ÖSYM zor soruları: düşük işlem + yüksek ilişki.
Bu modül, bu dengeyi yakalar.

Çıktı:
- cognitive_signature: { ...scores }
- dominant_type: En baskın bilişsel tip
- osym_difficulty_profile: ÖSYM zorluk profiline uyumluluk
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
import re


@dataclass
class CognitiveSignature:
    """Bilişsel imza sonucu."""
    computation_heavy: float  # 0-1
    concept_heavy: float  # 0-1
    relation_building: float  # 0-1
    reading_trap: float  # 0-1
    time_sink: float  # 0-1
    pattern_recognition: float  # 0-1
    
    dominant_type: str = ""
    osym_difficulty_profile: float = 0.0
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cognitive_signature": {
                "computation_heavy": round(self.computation_heavy, 2),
                "concept_heavy": round(self.concept_heavy, 2),
                "relation_building": round(self.relation_building, 2),
                "reading_trap": round(self.reading_trap, 2),
                "time_sink": round(self.time_sink, 2),
                "pattern_recognition": round(self.pattern_recognition, 2),
            },
            "dominant_type": self.dominant_type,
            "osym_difficulty_profile": round(self.osym_difficulty_profile, 2),
            "reasoning": self.reasoning
        }


# ============================================================================
# COGNITIVE INDICATORS (Pattern matching)
# ============================================================================

# Hesaplama göstergeleri
COMPUTATION_INDICATORS = [
    r'\bhesapla\b', r'\bbul\b', r'\bkaç\b', r'\bkaçtır\b',
    r'\btoplam\b', r'\bfark\b', r'\börtalama\b', r'\byüzde\b',
    r'[+\-*/=]', r'\d+\s*[+\-*/]\s*\d+',
    r'\bçarp\b', r'\bböl\b', r'\btopla\b', r'\bçıkar\b',
    r'\bx\s*=', r'\by\s*=',
    r'\beşitli[kğ]\b', r'\bdenklem\b',
]

# Kavram göstergeleri
CONCEPT_INDICATORS = [
    r'\bnedir\b', r'\btanım\b', r'\bözellik\b', r'\bkavram\b',
    r'\badlandır\b', r'\bbilgi\b', r'\bile\s+ilgili\b',
    r'\börnektir\b', r'\börneğidir\b', r'\bçeşit\b',
    r'\btür\b', r'\bsınıf\b', r'\bgrubu\b',
    r'\binceleme\b', r'\baçıkla\b',
]

# İlişki kurma göstergeleri
RELATION_INDICATORS = [
    r'\bkarşılaştır\b', r'\bfark\b', r'\bbenzer\b', r'\bilişki\b',
    r'\bbağlantı\b', r'\betki\b', r'\bneden\b', r'\bsonuç\b',
    r'\böyleyse\b', r'\bdolayısıyla\b', r'\bçünkü\b',
    r'\bI,?\s*II,?\s*(ve)?\s*III\b',  # Öncül yapısı
    r'\bhangisi.*değildir\b', r'\bhangisi.*yanlıştır\b',
    r'\bise\b.*\b(ise|de|da)\b',  # Koşullu yapı
]

# Okuma tuzağı göstergeleri
READING_TRAP_INDICATORS = [
    r'\ben\s+az\b', r'\ben\s+çok\b', r'\ben\s+fazla\b',
    r'\byalnız\b', r'\bsadece\b', r'\byalnızca\b',
    r'\bkesinlikle\b', r'\bmutlaka\b', r'\bher\s+zaman\b',
    r'\bhiçbir\b', r'\basla\b', r'\bhiç\b',
    r'\bdeğildir\b', r'\byanlıştır\b', r'\bolamaz\b',
    r'\bhepsi\b', r'\btümü\b', r'\btamamı\b',
]

# Zaman yutucusu göstergeleri
TIME_SINK_INDICATORS = [
    r'\badım\b', r'\bsırayla\b', r'\bönce.*sonra\b',
    r'\başama\b', r'\bişlem\b', r'\byöntem\b',
    # Uzunluk da zaman yutucusu göstergesi (base_features'dan alınacak)
]

# Örüntü tanıma göstergeleri
PATTERN_INDICATORS = [
    r'\bgrafik\b', r'\btablo\b', r'\bşekil\b', r'\bdiyagram\b',
    r'\bdizi\b', r'\bseri\b', r'\börüntü\b', r'\bkural\b',
    r'\bdevam\b', r'\bsonraki\b', r'\bbir\s+sonraki\b',
    r'\bartış\b', r'\bazalış\b', r'\beğilim\b', r'\btrend\b',
    r'\bkorelasyon\b', r'\bilişki\b',
]


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def count_pattern_matches(text: str, patterns: List[str]) -> int:
    """Pattern eşleşme sayısını hesapla."""
    count = 0
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        count += len(matches)
    return count


def score_computation(question_text: str, base_features: Dict[str, Any]) -> float:
    """Hesaplama ağırlığı skoru."""
    matches = count_pattern_matches(question_text, COMPUTATION_INDICATORS)
    
    # Sayısal şık oranı
    choice_types = base_features.get("choice_types", {})
    numeric_ratio = sum(1 for t in choice_types.values() if t == "numeric") / max(len(choice_types), 1)
    
    # Expression şık oranı
    expr_ratio = sum(1 for t in choice_types.values() if t == "expression") / max(len(choice_types), 1)
    
    # Normalize
    pattern_score = min(1.0, matches / 3)
    
    score = 0.4 * pattern_score + 0.3 * numeric_ratio + 0.3 * expr_ratio
    return min(1.0, score)


def score_concept(question_text: str, base_features: Dict[str, Any]) -> float:
    """Kavram ağırlığı skoru."""
    matches = count_pattern_matches(question_text, CONCEPT_INDICATORS)
    
    # Statement şık oranı (kavramsal sorular genelde statement şıklara sahip)
    choice_types = base_features.get("choice_types", {})
    statement_ratio = sum(1 for t in choice_types.values() if t == "statement") / max(len(choice_types), 1)
    
    pattern_score = min(1.0, matches / 2)
    
    score = 0.6 * pattern_score + 0.4 * statement_ratio
    return min(1.0, score)


def score_relation(question_text: str, base_features: Dict[str, Any]) -> float:
    """İlişki kurma skoru."""
    matches = count_pattern_matches(question_text, RELATION_INDICATORS)
    
    # Öncül sayısı (I, II, III tipi sorular ilişki kurma gerektirir)
    premise_count = base_features.get("premise_count_proxy", 0)
    premise_score = min(1.0, premise_count / 3)
    
    # Negatif soru (karşılaştırma/eleme gerektirir)
    is_negative = base_features.get("is_negative_question", False)
    negative_bonus = 0.2 if is_negative else 0
    
    pattern_score = min(1.0, matches / 2)
    
    score = 0.5 * pattern_score + 0.3 * premise_score + negative_bonus
    return min(1.0, score)


def score_reading_trap(question_text: str, base_features: Dict[str, Any]) -> float:
    """Okuma tuzağı skoru."""
    matches = count_pattern_matches(question_text, READING_TRAP_INDICATORS)
    
    # Negatif soru
    is_negative = base_features.get("is_negative_question", False)
    
    pattern_score = min(1.0, matches / 2)
    negative_bonus = 0.3 if is_negative else 0
    
    score = 0.7 * pattern_score + negative_bonus
    return min(1.0, score)


def score_time_sink(question_text: str, base_features: Dict[str, Any]) -> float:
    """Zaman yutucusu skoru."""
    matches = count_pattern_matches(question_text, TIME_SINK_INDICATORS)
    
    # Soru uzunluğu
    q_char_len = base_features.get("q_char_len", 0)
    length_score = min(1.0, q_char_len / 400)
    
    # Cümle sayısı
    q_sentence_count = base_features.get("q_sentence_count", 0)
    sentence_score = min(1.0, q_sentence_count / 5)
    
    pattern_score = min(1.0, matches / 2)
    
    score = 0.3 * pattern_score + 0.4 * length_score + 0.3 * sentence_score
    return min(1.0, score)


def score_pattern_recognition(question_text: str, base_features: Dict[str, Any]) -> float:
    """Örüntü tanıma skoru."""
    matches = count_pattern_matches(question_text, PATTERN_INDICATORS)
    
    # Şekil/grafik varlığı
    has_figure = base_features.get("has_figure", False)
    references_figure = base_features.get("references_figure_in_text", False)
    
    pattern_score = min(1.0, matches / 2)
    figure_bonus = 0.4 if (has_figure or references_figure) else 0
    
    score = 0.6 * pattern_score + figure_bonus
    return min(1.0, score)


# ============================================================================
# MAIN COGNITIVE ANALYSIS
# ============================================================================

def analyze_cognitive_signature(standardized_data: Dict[str, Any]) -> CognitiveSignature:
    """
    Ana bilişsel imza analiz fonksiyonu.
    
    Args:
        standardized_data: standardized_v1 formatında veri
        
    Returns:
        CognitiveSignature objesi
    """
    normalized = standardized_data.get("normalized", {})
    base_features = standardized_data.get("base_features", {})
    question_text = normalized.get("question_text", "")
    
    # Her boyutu skorla
    computation = score_computation(question_text, base_features)
    concept = score_concept(question_text, base_features)
    relation = score_relation(question_text, base_features)
    reading_trap = score_reading_trap(question_text, base_features)
    time_sink = score_time_sink(question_text, base_features)
    pattern = score_pattern_recognition(question_text, base_features)
    
    # Baskın tip belirle
    scores = {
        "computation_heavy": computation,
        "concept_heavy": concept,
        "relation_building": relation,
        "reading_trap": reading_trap,
        "time_sink": time_sink,
        "pattern_recognition": pattern,
    }
    dominant_type = max(scores, key=scores.get)
    
    # ÖSYM zorluk profili
    # ÖSYM zor soruları: düşük hesaplama + yüksek ilişki + okuma tuzağı
    osym_difficulty = (
        0.3 * (1 - computation) +  # Düşük hesaplama
        0.3 * relation +  # Yüksek ilişki
        0.2 * reading_trap +  # Okuma tuzağı
        0.2 * pattern  # Örüntü tanıma
    )
    
    # Reasoning oluştur
    top_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
    type_names = {
        "computation_heavy": "hesaplama ağırlıklı",
        "concept_heavy": "kavram ağırlıklı",
        "relation_building": "ilişki kurma",
        "reading_trap": "okuma tuzağı",
        "time_sink": "zaman yutucusu",
        "pattern_recognition": "örüntü tanıma",
    }
    
    reasoning_parts = [f"{type_names[t[0]]} ({t[1]:.0%})" for t in top_types]
    reasoning = f"Baskın bilişsel profil: {', '.join(reasoning_parts)}"
    
    return CognitiveSignature(
        computation_heavy=computation,
        concept_heavy=concept,
        relation_building=relation,
        reading_trap=reading_trap,
        time_sink=time_sink,
        pattern_recognition=pattern,
        dominant_type=dominant_type,
        osym_difficulty_profile=osym_difficulty,
        reasoning=reasoning
    )


def cognitive_signature_score(standardized_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience wrapper - dict döndürür.
    """
    result = analyze_cognitive_signature(standardized_data)
    return result.to_dict()
