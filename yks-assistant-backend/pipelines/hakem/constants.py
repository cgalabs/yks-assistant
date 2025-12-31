"""
constants.py - Türkçe soru analizi için regex pattern'lar ve sabitler

Bu modül LLM kullanmadan, deterministik pattern matching için gerekli tüm sabitleri içerir.
"""

import re

# ============================================================================
# NEGATIVE QUESTION PATTERNS (Negatif Soru Tespiti)
# ============================================================================
# ÖSYM'de sıkça kullanılan negatif soru kalıpları
NEGATIVE_PATTERNS = [
    r'\bdeğildir\b',
    r'\byanlıştır\b',
    r'\bolamaz\b',
    r'\byoktur\b',
    r'\bsöylenemez\b',
    r'\bbulunamaz\b',
    r'\biçermez\b',
    r'\bgöstermez\b',
    r'\bbelirtmez\b',
    r'\bdoğru\s+değildir\b',
    r'\bgeçerli\s+değildir\b',
    r'\buygun\s+değildir\b',
    r'\başağıdakilerden\s+hangisi\s+.*\s+değildir\b',
    r'\bhangisi\s+.*\s+olamaz\b',
    r'\bhangisi\s+.*\s+yoktur\b',
]

# Compiled regex for performance
NEGATIVE_REGEX = re.compile('|'.join(NEGATIVE_PATTERNS), re.IGNORECASE)

# ============================================================================
# PREMISE PATTERNS (Öncül Sayısı Tespiti)
# ============================================================================
# Roman numerals: I, II, III, IV, V
ROMAN_NUMERAL_PATTERN = re.compile(r'\b(I{1,3}|IV|V|VI{0,3})\b(?:\s*[.)\-:]|\s+[A-ZÇĞİÖŞÜa-zçğıöşü])')

# Arabic numerals with markers: 1), 2., 1-, etc.
ARABIC_NUMERAL_PATTERN = re.compile(r'\b(\d+)\s*[.)\-:]')

# Bullet-style premises
BULLET_PATTERN = re.compile(r'[•●○◦]\s*')

# ============================================================================
# FIGURE REFERENCE PATTERNS (Şekil/Grafik/Tablo Referansı)
# ============================================================================
FIGURE_REFERENCE_PATTERNS = [
    r'\bşekil\b',
    r'\bşekilde\b',
    r'\bşekilden\b',
    r'\bgrafik\b',
    r'\bgrafikte\b',
    r'\bgrafikten\b',
    r'\btablo\b',
    r'\btabloda\b',
    r'\btablodan\b',
    r'\bdiyagram\b',
    r'\bgörsel\b',
    r'\bçizim\b',
    r'\bharita\b',
    r'\bharitada\b',
]

FIGURE_REFERENCE_REGEX = re.compile('|'.join(FIGURE_REFERENCE_PATTERNS), re.IGNORECASE)

# ============================================================================
# CHOICE TYPE PATTERNS (Şık Tipi Tespiti)
# ============================================================================
# Numeric patterns: "5", "3.14", "2/3", "√2", etc.
NUMERIC_PATTERN = re.compile(r'^[\d\s\.,/\+\-\*=<>√π²³]+$')

# Expression patterns: mathematical expressions with variables
EXPRESSION_PATTERN = re.compile(r'[a-zA-Z]\s*[=<>+\-*/^²³]|[=<>+\-*/^²³]\s*[a-zA-Z]|^\s*[a-zA-Z]\s*$')

# ============================================================================
# STANDARD CHOICES
# ============================================================================
STANDARD_CHOICES = ['A', 'B', 'C', 'D', 'E']

# ============================================================================
# SCHEMA VERSIONS
# ============================================================================
SCHEMA_INPUT = "extract_v1"
SCHEMA_OUTPUT = "standardized_v1"

# ============================================================================
# TOKEN SPLITTING (Basit Türkçe tokenization)
# ============================================================================
# Whitespace ve noktalama işaretlerine göre split
TOKEN_SPLIT_PATTERN = re.compile(r'[\s,;:!?\(\)\[\]\{\}"\']+')

# Sentence ending patterns
SENTENCE_END_PATTERN = re.compile(r'[.!?]+')
