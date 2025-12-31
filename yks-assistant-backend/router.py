from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from typing import Optional
from schemas_contracts.models import ExtractV1, SolveV1, GenerateV1, CoachV1
from pipelines.solve import solve_pipeline
from pipelines.generate import generate_pipeline
from pipelines.coach import coach_pipeline
from pipelines.evaluate import evaluate_pipeline
from pipelines.measure import measure_pipeline
from pipelines.chat import chat_pipeline

router = APIRouter()



async def route_solve(image_bytes: bytes) -> dict:
    """
    Routes the solve request to the Solve Pipeline.
    Process: VLM Extractor -> Solver Model -> Post-process
    """
    return await solve_pipeline(image_bytes)

async def route_generate(topic: str, difficulty: str) -> dict:
    """
    Routes the generate request to the Generate Pipeline.
    Process: Generator Model -> Validator
    """
    return await generate_pipeline(topic, difficulty)

async def route_coach(context: dict) -> dict:
    """
    Routes the coach request to the Coach Pipeline.
    Process: Coach LLM
    """
    return await coach_pipeline(context)

async def route_evaluate(data: dict) -> dict:
    """
    Routes internal evaluation requests.
    """
    return await evaluate_pipeline(data)

async def route_measure(image_bytes: bytes) -> dict:
    """
    Routes the measure request to the Measure Pipeline.
    Process: VLM Extractor -> Hakem Standardizer -> Hakem Scorer
    """
    return await measure_pipeline(image_bytes)

async def route_chat(message: str, history: list, context: dict) -> dict:
    """
    Routes the chat request to the Chat Pipeline.
    """
    return await chat_pipeline(message, history, context)

