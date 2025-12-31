import uuid
import io
from fastapi import UploadFile, HTTPException
from PIL import Image

def generate_request_id() -> str:
    """Generates a unique request ID."""
    return str(uuid.uuid4())

async def process_image(file: UploadFile, max_size=(1024, 1024)) -> bytes:
    """
    Validates and optionally resizes the uploaded image.
    Ensures the image is a PNG or converts it.
    Returns the image bytes.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        

        if image.mode != "RGB":
            image = image.convert("RGB")
            

        image.thumbnail(max_size)
        

        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
