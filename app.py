from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def hello():
    return "Hello from EC2! Running FastAPI Application via systemd!"

@app.get("/health")
def health():
    return JSONResponse(
        content={"status": "healthy", "app": "running"},
        status_code=200
    )
