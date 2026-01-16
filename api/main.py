from fastapi import FastAPI, UploadFile
from services.extract import extract_plot_data

app = FastAPI(title="Construction Document Intelligence")

@app.post("/extract/plot")
async def extract_plot(file: UploadFile):
    result = await extract_plot_data(file)
    return result
