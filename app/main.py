from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
import uvicorn
from PIL import Image, UnidentifiedImageError
import io
from app.services.extractor_logic import DocumentAgent as DocumentExtractor


# Singleton instance of the logic layer
extractor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global extractor
    print("--- Startup: Loading QwenService Model to GPU ---")
    try:
        extractor = DocumentExtractor()
    except Exception as e:
        print(f"CRITICAL ERROR during model load: {e}")
    yield
    print("--- Shutdown: Cleaning up ---")

app = FastAPI(title="Quickplot Extraction API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "active", "hardware": "CUDA" if extractor and extractor.ai.device == "cuda" else "CPU"}

@app.post("/extract")
async def extract_plot_data(file: UploadFile = File(...)):
    if not extractor:
        raise HTTPException(status_code=503, detail="Model initialization failed.")

    try:
        # Read file into memory
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")

        # Open image
        image = Image.open(io.BytesIO(file_bytes))
        image.load() # Prevents lazy loading issues

        # Process through AI + Regex logic
        result = extractor.process(image)
        return result

    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image format. Please use JPG/PNG.")
    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Note: reload=False is required for GPU stability on Windows
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)