import requests
import json
import os
from together import Together
from config import MODEL_ID, TOGETHER_MODEL_ID

class LLMClientError(Exception):
    pass



def call_llm(prompt: str, api_key: str, image_b64: str = None, image_mime_type: str = "image/jpeg", max_tokens: int = 2000, temperature: float = 0.6, model: str = MODEL_ID):
    """
    Calls Fireworks AI API (Qwen3-VL) with streaming support.
    Yields chunks of text as they arrive.
    Enforces a strict limit locally.
    """
    if not api_key:
        raise LLMClientError("API Key is missing.")


    print(f"[Fireworks] Request being sent to {model} (STREAMING)...")


    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    
    # Construct content payload
    content = []
    

    content.append({
        "type": "text",
        "text": prompt
    })
    

    if image_b64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{image_mime_type};base64,{image_b64}"
            }
        })
    
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": temperature,
        "stream": True,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }


    try:
        with requests.post(url, headers=headers, data=json.dumps(payload), stream=True) as response:
            try:
                response.raise_for_status()
            except requests.RequestException as e:
                # Read error body if possible
                error_body = response.text
                print(f"[DEBUG API ERROR] {error_body}")
                raise LLMClientError(f"Fireworks API Request failed: {e}\nResponse: {error_body}")


            for line in response.iter_lines():
                if line:
                    line_decoded = line.decode("utf-8")
                    if line_decoded.startswith("data: "):
                        data_str = line_decoded[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data_json = json.loads(data_str)

                            if "choices" in data_json and len(data_json["choices"]) > 0:
                                delta = data_json["choices"][0].get("delta", {})
                                content_chunk = delta.get("content", "")
                                if content_chunk:
                                    yield content_chunk
                        except json.JSONDecodeError:
                            continue
                            
    except requests.RequestException as e:
         raise LLMClientError(f"Fireworks API Connection failed: {e}")


def call_together(prompt: str, api_key: str, model: str = TOGETHER_MODEL_ID, max_tokens: int = 2000, temperature: float = 0.6):
    """
    Calls Together AI API using the SDK.
    Yields chunks of text (streaming).
    """
    if not api_key:
        raise LLMClientError("Together API Key is missing.")


    print(f"[Together] Request being sent to {model} (STREAMING)...")


    client = Together(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )

        for chunk in response:
            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    
    except Exception as e:
         raise LLMClientError(f"Together AI API Request failed: {e}")

