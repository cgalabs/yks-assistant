"""
distractor_quality.py - Distractor Quality Score Module

Bu modül, çeldiricilerin (yanlış şıkların) kalitesini ölçer.

Amaç: "Çeldiriciler gerçek hata modellerinden mi geliyor?"

ÖSYM'nin gizli silahı çeldiricidir. İyi bir çeldirici:
- Tipik öğrenci hatalarını yakalar
- Görünüşte mantıklı ama yanlıştır
- Diğer çeldiricilerle çeşitlilik gösterir

Hızlı Proxy Metrikler (LLM'siz):
- Şıkların birbirine edit-distance/semantic yakınlığı
- Şıkların çeşitliliği (hepsi aynı tip sayı mı)
- "Bariz yanlış" sinyali (çok uç değer/outlier)

Çıktı:
- distractor_quality ∈ [0,1]
- distractor_analysis[] (her şık için analiz)
"""

from typing import Dict, List, Any, Tuple, Set, Optional
from dataclasses import dataclass, field
import re
from collections import Counter


@dataclass
class DistractorAnalysis:
    """Tek bir çeldirici analizi."""
    choice: str
    trap_type: str  # numeric_outlier, too_similar, too_different, balanced
    similarity_to_others: float
    notes: str = ""


@dataclass
class DistractorResult:
    """Distractor Quality sonucu."""
    distractor_quality: float  # 0-1 arası skor
    choice_diversity: float  # 0-1 arası çeşitlilik skoru
    has_outlier: bool  # Bariz yanlış var mı
    distractor_analysis: List[Dict[str, Any]] = field(default_factory=list)
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "distractor_quality": round(self.distractor_quality, 2),
            "choice_diversity": round(self.choice_diversity, 2),
            "has_outlier": self.has_outlier,
            "distractor_analysis": self.distractor_analysis,
            "reasoning": self.reasoning
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def tokenize(text: str) -> Set[str]:
    """Metni token set'ine dönüştür."""
    tokens = re.split(r'[\s,;:!?\(\)\[\]\{\}"\'<>=+\-*/]+', text.lower())
    return {t for t in tokens if t.strip() and len(t) > 1}


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """İki set arasındaki Jaccard benzerliği."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def levenshtein_distance(s1: str, s2: str) -> int:
    """İki string arasındaki Levenshtein mesafesi."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def normalized_edit_distance(s1: str, s2: str) -> float:
    """Normalize edilmiş edit distance (0-1 arası, 0 = aynı)."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 0.0
    return levenshtein_distance(s1, s2) / max_len


def extract_numeric_value(text: str) -> Optional[float]:
    """Metinden sayısal değer çıkar."""
    # Basit sayı pattern'ı
    match = re.search(r'[-+]?\d*[.,]?\d+', text.replace(',', '.'))
    if match:
        try:
            return float(match.group().replace(',', '.'))
        except ValueError:
            return None
    return None


# ============================================================================
# DISTRACTOR ANALYSIS FUNCTIONS
# ============================================================================

def analyze_numeric_choices(choices: Dict[str, str]) -> Tuple[float, bool, List[str]]:
    """
    Sayısal şıkları analiz et.
    
    Returns:
        Tuple of (diversity_score, has_outlier, notes)
    """
    values = {}
    for key, text in choices.items():
        val = extract_numeric_value(text)
        if val is not None:
            values[key] = val
    
    if len(values) < 3:
        return 1.0, False, []
    
    sorted_vals = sorted(values.values())
    notes = []
    
    # Outlier tespiti (IQR metodu)
    q1_idx = len(sorted_vals) // 4
    q3_idx = 3 * len(sorted_vals) // 4
    q1 = sorted_vals[q1_idx]
    q3 = sorted_vals[q3_idx]
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = [k for k, v in values.items() if v < lower_bound or v > upper_bound]
    has_outlier = len(outliers) > 0
    
    if has_outlier:
        notes.append(f"Outlier şıklar: {', '.join(outliers)}")
    
    # Çeşitlilik: değerler arası mesafe
    if len(sorted_vals) >= 2:
        diffs = [sorted_vals[i+1] - sorted_vals[i] for i in range(len(sorted_vals)-1)]
        avg_diff = sum(diffs) / len(diffs)
        
        # Çok yakın değerler (aynı şık gibi)
        if avg_diff == 0:
            diversity = 0.3
            notes.append("Şıklar çok yakın değerlere sahip")
        elif max(diffs) > 3 * min(diffs) if min(diffs) > 0 else False:
            # Düzensiz dağılım (bir şık çok uzak)
            diversity = 0.6
            notes.append("Değerler düzensiz dağılmış")
        else:
            # İyi dağılım
            diversity = 1.0
    else:
        diversity = 0.5
    
    return diversity, has_outlier, notes


def analyze_statement_choices(choices: Dict[str, str]) -> Tuple[float, List[str]]:
    """
    İfade/cümle şıkları analiz et.
    
    Returns:
        Tuple of (diversity_score, notes)
    """
    notes = []
    choice_values = list(choices.values())
    
    if len(choice_values) < 2:
        return 1.0, []
    
    # Token set'leri
    token_sets = [tokenize(v) for v in choice_values]
    
    # Pairwise similarity hesapla
    similarities = []
    for i in range(len(token_sets)):
        for j in range(i + 1, len(token_sets)):
            sim = jaccard_similarity(token_sets[i], token_sets[j])
            similarities.append(sim)
    
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0
    
    # Edit distance bazlı analiz
    edit_distances = []
    for i in range(len(choice_values)):
        for j in range(i + 1, len(choice_values)):
            ed = normalized_edit_distance(choice_values[i], choice_values[j])
            edit_distances.append(ed)
    
    avg_edit_dist = sum(edit_distances) / len(edit_distances) if edit_distances else 0
    
    # Çeşitlilik skoru
    if avg_similarity > 0.8:
        diversity = 0.3
        notes.append("Şıklar birbirine çok benziyor")
    elif avg_similarity > 0.5:
        diversity = 0.6
        notes.append("Şıklar orta düzeyde benzer")
    elif avg_similarity < 0.1:
        diversity = 0.7  # Çok farklı da iyi değil
        notes.append("Şıklar birbirinden çok farklı")
    else:
        diversity = 1.0  # İdeal çeşitlilik
    
    return diversity, notes


def analyze_choice_lengths(choices: Dict[str, str]) -> Tuple[float, List[str]]:
    """
    Şık uzunluklarını analiz et.
    
    Returns:
        Tuple of (balance_score, notes)
    """
    lengths = [len(v) for v in choices.values() if v]
    notes = []
    
    if len(lengths) < 3:
        return 1.0, []
    
    avg_len = sum(lengths) / len(lengths)
    
    # Varyans
    variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
    std_dev = variance ** 0.5
    
    # Coefficient of variation
    cv = std_dev / avg_len if avg_len > 0 else 0
    
    if cv < 0.1:
        # Çok uniform (potansiyel kalıp üretim)
        balance = 0.7
        notes.append("Şık uzunlukları çok uniform")
    elif cv > 0.8:
        # Çok değişken (bir şık çok uzun/kısa)
        balance = 0.6
        notes.append("Şık uzunlukları çok değişken")
    else:
        balance = 1.0
    
    return balance, notes


def classify_trap_type(
    choice_key: str,
    choice_value: str,
    all_choices: Dict[str, str],
    choice_types: Dict[str, str]
) -> Tuple[str, float]:
    """
    Çeldirici tipini sınıflandır.
    
    Returns:
        Tuple of (trap_type, similarity_to_others)
    """
    other_values = [v for k, v in all_choices.items() if k != choice_key]
    
    if not other_values:
        return "unknown", 0.0
    
    # Bu şıkkın diğerlerine benzerliği
    my_tokens = tokenize(choice_value)
    similarities = []
    for other in other_values:
        other_tokens = tokenize(other)
        sim = jaccard_similarity(my_tokens, other_tokens)
        similarities.append(sim)
    
    avg_sim = sum(similarities) / len(similarities)
    
    # Sayısal outlier kontrolü
    my_type = choice_types.get(choice_key, "statement")
    if my_type == "numeric":
        my_val = extract_numeric_value(choice_value)
        other_vals = [extract_numeric_value(v) for v in other_values]
        other_vals = [v for v in other_vals if v is not None]
        
        if my_val is not None and other_vals:
            avg_other = sum(other_vals) / len(other_vals)
            if abs(my_val - avg_other) > 2 * max(abs(v - avg_other) for v in other_vals):
                return "numeric_outlier", avg_sim
    
    # Benzerlik bazlı sınıflandırma
    if avg_sim > 0.7:
        return "too_similar", avg_sim
    elif avg_sim < 0.1:
        return "too_different", avg_sim
    else:
        return "balanced", avg_sim


# ============================================================================
# MAIN DISTRACTOR ANALYSIS
# ============================================================================

def analyze_distractors(standardized_data: Dict[str, Any]) -> DistractorResult:
    """
    Ana çeldirici analiz fonksiyonu.
    
    Args:
        standardized_data: standardized_v1 formatında veri
        
    Returns:
        DistractorResult objesi
    """
    normalized = standardized_data.get("normalized", {})
    base_features = standardized_data.get("base_features", {})
    choices = normalized.get("choices", {})
    choice_types = base_features.get("choice_types", {})
    
    # Dominant tip belirle
    type_counts = Counter(choice_types.values())
    dominant_type = type_counts.most_common(1)[0][0] if type_counts else "statement"
    
    # Tip bazlı analiz
    if dominant_type == "numeric":
        diversity, has_outlier, type_notes = analyze_numeric_choices(choices)
    else:
        diversity, type_notes = analyze_statement_choices(choices)
        has_outlier = False
    
    # Uzunluk analizi
    length_balance, length_notes = analyze_choice_lengths(choices)
    
    # Her şık için detaylı analiz
    distractor_analysis = []
    for key, value in choices.items():
        trap_type, similarity = classify_trap_type(key, value, choices, choice_types)
        analysis = {
            "choice": key,
            "trap_type": trap_type,
            "similarity_to_others": round(similarity, 2),
            "length": len(value)
        }
        distractor_analysis.append(analysis)
    
    # Genel kalite skoru
    # Balanced trap_type oranı
    balanced_count = sum(1 for a in distractor_analysis if a["trap_type"] == "balanced")
    balance_ratio = balanced_count / len(distractor_analysis) if distractor_analysis else 0
    
    # Ağırlıklı skor
    distractor_quality = (
        0.4 * diversity +
        0.3 * length_balance +
        0.3 * balance_ratio
    )
    
    # Outlier varsa düşür
    if has_outlier:
        distractor_quality *= 0.8
    
    # Reasoning oluştur
    all_notes = type_notes + length_notes
    
    if distractor_quality >= 0.8:
        reasoning = "Çeldiriciler iyi dengelenmiş ve çeşitli."
    elif distractor_quality >= 0.6:
        reasoning = "Çeldiriciler kabul edilebilir kalitede."
    elif distractor_quality >= 0.4:
        reasoning = "Çeldiriciler bazı sorunlar içeriyor: " + "; ".join(all_notes[:2])
    else:
        reasoning = "Çeldirici kalitesi düşük: " + "; ".join(all_notes[:2])
    
    return DistractorResult(
        distractor_quality=distractor_quality,
        choice_diversity=diversity,
        has_outlier=has_outlier,
        distractor_analysis=distractor_analysis,
        reasoning=reasoning
    )


def distractor_quality_score(standardized_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience wrapper - dict döndürür.
    """
    result = analyze_distractors(standardized_data)
    return result.to_dict()
