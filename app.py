from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def hello():
    return "FastAPI running inside Docker!"

@app.get("/health")
def health():
    return JSONResponse(
        content={"status": "healthy", "app": "running"},
        status_code=200
    )
