from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from router import route_solve, route_generate, route_coach, route_evaluate, route_measure, route_chat
from ingest import process_image

app = FastAPI(title="YKS AI Asistan Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    topic: str
    difficulty: str = "medium"

class CoachRequest(BaseModel):
    context: Dict[str, Any]

class EvaluateRequest(BaseModel):
    data: Dict[str, Any]

class ChatRequest(BaseModel):
    message: str
    history: Optional[list] = []
    context: Optional[dict] = {}



@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/solve")
async def solve_endpoint(file: UploadFile = File(...)):
    """
    Multimodal solve endpoint.
    Input: PNG Image
    Output: Solution JSON
    """

    image_bytes = await process_image(file)
    

    return await route_solve(image_bytes)

@app.post("/generate")
async def generate_endpoint(req: GenerateRequest):
    """
    Generate questions endpoint.
    """
    return await route_generate(req.topic, req.difficulty)

@app.post("/coach")
async def coach_endpoint(req: CoachRequest):
    """
    Coach advice endpoint.
    """
    return await route_coach(req.context)

@app.post("/events")
async def events_endpoint(event: Dict[str, Any] = Body(...)):
    """
    Fire-and-forget event logging endpoint.
    """

    print(f"[EVENT] {event}")
    return {"status": "received"}

@app.post("/evaluate")
async def evaluate_endpoint(req: EvaluateRequest):
    """
    Internal measure pipeline.
    """
    return await route_evaluate(req.data)

@app.post("/measure")
async def measure_endpoint(file: UploadFile = File(...)):
    """
    Measure OSYM Similarity endpoint.
    Input: Image
    Output: Similarity Score JSON
    """

    image_bytes = await process_image(file)
    

    return await route_measure(image_bytes)
@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """
    General chat endpoint.
    """
    return await route_chat(req.message, req.history, req.context)
