import uuid
from fastapi import FastAPI, UploadFile, File
from starlette.responses import FileResponse
import shutil
import os
from test import test

app = FastAPI()

UPLOAD_DIR = "./uploaded_images/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/test-image/")
async def test_image(file: UploadFile = File(...)):
    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[-1]
    filename = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(filename, "wb") as image:
        shutil.copyfileobj(file.file, image)

    result = test(filename, "./resources/anti_spoof_models", 0)

    os.remove(filename)

    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
