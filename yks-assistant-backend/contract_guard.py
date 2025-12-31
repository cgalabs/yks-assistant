import json
import time
from typing import Type, TypeVar, Optional, Callable, Dict, Any
from pydantic import BaseModel, ValidationError
from llm_client import call_llm, call_together

T = TypeVar('T', bound=BaseModel)

async def run_with_contract_guard(
    prompt: str,
    output_model: Type[T],
    api_key: str,
    image_b64: Optional[str] = None,
    image_mime_type: str = "image/jpeg",
    pipeline_name: str = "unknown",
    model_name: str = "unknown",
    request_id: str = "unknown",
    max_retries: int = 1,
    use_together: bool = False,
    model: Optional[str] = None
) -> T:
    """
    Executes an LLM call and enforces a strict Pydantic contract on the output.
    Follows the 1-retry policy:
    1. Call LLM
    2. Try to parse JSON and validate against output_model
    3. If fail, log and Retry ONCE (with same input)
    4. If fail again, raise Exception (caller handles graceful error)
    
    Returns the validated Pydantic model instance.
    """
    
    retries = 0
    
    while retries <= max_retries:
        start_time = time.time()
        raw_output = ""
        
        try:

            chunks = []
            if use_together:
                llm_args = {"prompt": prompt, "api_key": api_key}
                if model: llm_args["model"] = model
                for chunk in call_together(**llm_args):
                    chunks.append(chunk)
            else:
                llm_args = {"prompt": prompt, "api_key": api_key, "image_b64": image_b64, "image_mime_type": image_mime_type}
                if model: llm_args["model"] = model
                for chunk in call_llm(**llm_args):
                    chunks.append(chunk)
            raw_output = "".join(chunks)
            

            json_str = raw_output
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                 json_str = json_str.split("```")[1].split("```")[0].strip()


            parsed_json = json.loads(json_str)
            validated_obj = output_model(**parsed_json)
            

            latency = int((time.time() - start_time) * 1000)
            print(f"[LOG] req_id={request_id} pipeline={pipeline_name} model={model_name} latency={latency}ms parse_valid=True contract_valid=True retry={retries}")
            return validated_obj
            
        except (json.JSONDecodeError, ValidationError, Exception) as e:
            latency = int((time.time() - start_time) * 1000)
            print(f"[WARN] req_id={request_id} pipeline={pipeline_name} model={model_name} latency={latency}ms parse_valid=False contract_valid=False retry={retries} error={str(e)}")
            
            retries += 1
            if retries > max_retries:
                print(f"[ERROR] Max retries reached for {pipeline_name}/{model_name}")
                raise e # Let the caller handle the final failure

    raise Exception("Unreachable code")
