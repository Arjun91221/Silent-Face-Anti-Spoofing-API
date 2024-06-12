import uuid
from fastapi import FastAPI, UploadFile, File, Form
from starlette.responses import FileResponse
import shutil
import os
from test import test
import requests

app = FastAPI()

UPLOAD_DIR = "./uploaded_images/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/verify-image/")
async def test_image(file: UploadFile = File(None), image_link: str = Form(None)):
    if file:
        unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[-1]
        filename = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(filename, "wb") as image:
            shutil.copyfileobj(file.file, image)

        result = test(filename, "./resources/anti_spoof_models", 0)

        os.remove(filename)

        return result
    
    elif image_link:
        try:
            response = requests.get(image_link)
            if response.status_code == 200:
                unique_filename = str(uuid.uuid4()) + os.path.splitext(image_link.split("/")[-1])[-1]
                filename = os.path.join(UPLOAD_DIR, unique_filename)
                with open(filename, "wb") as image_file:
                    image_file.write(response.content)

                # Process the downloaded image
                result = test(filename, "./resources/anti_spoof_models", 0)

                # Remove the locally saved image
                os.remove(filename)

                return result
            else:
                return {"error": "Failed to download the image"}
        except Exception as e:
            return {"error": f"An error occurred: {e}"}
    else:
        return {"error": "Please provide either an image file or an image link."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
