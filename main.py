import base64
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from starlette.responses import FileResponse, StreamingResponse
import shutil
import os
from test import test
import requests
from pydantic import BaseModel
import aiohttp
from io import BytesIO
from PIL import Image
import io


app = FastAPI()

current_directory = os.path.dirname(__file__)

UPLOAD_DIR = f"{current_directory}/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class Base64Image(BaseModel):
    base64_string: str

async def fetch_image_from_url(url: str) -> io.BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=400, detail="Invalid URL")
            return BytesIO(await response.read())
        
def decode_base64_image(base64_string: str) -> BytesIO:
    image_data = base64.b64decode(base64_string)
    return BytesIO(image_data)
        
@app.post("/image-to-base64/")
async def image_to_base64(file: UploadFile = File(None), url: str = Form(None)):
    if file is None and url is None:
        raise HTTPException(status_code=400, detail="No image file or URL provided")

    if file:
        contents = await file.read()
        image_path = f"{UPLOAD_DIR}/{str(uuid.uuid4())}.png"
        with open(image_path, "wb") as f:
            f.write(contents)
    else:
        image_io = await fetch_image_from_url(url)
        image_path = f"{UPLOAD_DIR}/{str(uuid.uuid4())}.png"
        with open(image_path, "wb") as f:
            f.write(image_io.getvalue())

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    os.remove(image_path)
    
    return encoded_string

@app.post("/base64-to-image/")
async def base64_to_image(base64_image: Base64Image):
    try:
        base64_string = base64_image.base64_string
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        
        image_path = f"{UPLOAD_DIR}/{str(uuid.uuid4())}.png"
        image.save(image_path)
        
        return StreamingResponse(open(image_path, "rb"), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 string: {e}")

@app.post("/verify-image/")
async def test_image(base64_image: Base64Image):
    try:
        image_io = decode_base64_image(base64_image.base64_string)
        image_path = f"{UPLOAD_DIR}/{str(uuid.uuid4())}.png"
        with open(image_path, "wb") as f:
            f.write(image_io.getvalue())
        
        result = test(image_path, "./resources/anti_spoof_models", 0)

        os.remove(image_path)

        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 string: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
