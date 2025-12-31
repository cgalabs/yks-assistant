from typing import List, Optional, Dict, Literal, Union
from pydantic import BaseModel, Field

# ------------------------------------------------------------------------
# 1. EXTRACT CONTRACT (VLM Output)
# ------------------------------------------------------------------------
class ExtractV1(BaseModel):
    schema: str = Field("extract_v1", alias="schema")
    id: str = Field("q_001", description="ID for the extracted question.")
    question_text: str = Field(..., min_length=1, description="The main text of the question extracted from the image.")
    choices: Dict[str, Optional[str]] = Field(..., description="Map of choices, e.g., {'A': '...', 'B': '...'}. Keys must be A-E.")
    figures_desc: Optional[str] = Field(None, description="Description of any figures or diagrams in the image.")
    topic_hint: Optional[str] = Field(None, description="Inferred topic or subject area.")
    constraints: Optional[List[str]] = Field(None, description="Any specific constraints mentioned in the question.")
    language: str = Field("tr", description="Language of the question.")
    extraction_notes: Optional[str] = Field(None, description="Notes about the extraction process.")
    extraction_confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score of the extraction.")

# ------------------------------------------------------------------------
# 2. SOLVE CONTRACT (Solver Output)
# ------------------------------------------------------------------------
class SolveV1(BaseModel):
    steps: List[str] = Field(..., min_items=1, description="Step-by-step solution steps.")
    final_answer: Literal["A", "B", "C", "D", "E"] = Field(..., description="The final answer option.")
    reasoning_checks: Optional[List[str]] = Field(None, description="Internal reasoning checks or verification.")
    common_traps: Optional[List[str]] = Field(None, description="Common pitfalls or traps for this type of question.")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score.")

# ------------------------------------------------------------------------
# 3. GENERATE CONTRACT (Generator Output)
# ------------------------------------------------------------------------
class GeneratedQuestion(BaseModel):
    problem_text: str = Field(..., min_length=1, description="The text of the generated problem.")
    choices: Dict[str, str] = Field(..., alias="answer_choices", description="Choices for the question (A-E).")
    correct_answer: Literal["A", "B", "C", "D", "E"] = Field(..., description="The correct answer.")
    solution: Union[str, List[str]] = Field(..., description="Solution steps or text.")
    topic: Optional[str] = None

class GenerateV1(BaseModel):
    questions: List[GeneratedQuestion] = Field(..., min_items=1, description="List of generated questions.")

# ------------------------------------------------------------------------
# 4. COACH CONTRACT (Coach Output)
# ------------------------------------------------------------------------
class CoachV1(BaseModel):
    daily_plan: str = Field(..., description="Actionable advice for 'Today'.")
    weekly_plan: str = Field(..., description="Actionable advice for 'This Week'.")
    focus_area: str = Field(..., description="Specific area to 'Watch Out' for.")

# ------------------------------------------------------------------------
# 5. EVALUATE CONTRACT (Evaluator Output - Internal)
# ------------------------------------------------------------------------
class EvalScores(BaseModel):
    osym_similarity: float = Field(..., ge=0, le=1, description="Similarity to OSYM style.")
    difficulty: float = Field(..., ge=0, le=1, description="Difficulty score.")
    kazanim_fit: Optional[float] = Field(None, ge=0, le=1, description="Fit to curriculum objectives.")

class EvalV1(BaseModel):
    scores: EvalScores
    short_justifications: List[str] = Field(..., min_items=1, description="Justifications for the scores.")
# ------------------------------------------------------------------------
# 6. CHAT CONTRACT (General Chat Output)
# ------------------------------------------------------------------------
class ChatV1(BaseModel):
    response: str = Field(..., description="The textual response from the assistant.")
