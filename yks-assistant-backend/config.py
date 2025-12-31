import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_API_KEY = os.getenv("DEFAULT_API_KEY")

SOLVE_API_KEY = os.getenv("SOLVE_API_KEY")
GENERATE_API_KEY = os.getenv("GENERATE_API_KEY")
GENERATE_MODEL_ID = "accounts/fireworks/models/gpt-oss-120b"
COACH_API_KEY = os.getenv("COACH_API_KEY")
COACH_MODEL_ID = "accounts/fireworks/models/gpt-oss-120b"
EVALUATE_API_KEY = os.getenv("EVALUATE_API_KEY")
MEASURE_API_KEY = os.getenv("MEASURE_API_KEY")

EXTRACT_API_KEY = os.getenv("EXTRACT_API_KEY")
EXTRACT_MODEL_ID = "accounts/fireworks/models/qwen3-vl-235b-a22b-instruct"

MODEL_ID = "accounts/fireworks/models/qwen2p5-vl-32b-instruct"
TOGETHER_MODEL_ID = "kgegek_bb35/Qwen2.5-72B-Instruct-yks-llm-v3-456bd664"
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


