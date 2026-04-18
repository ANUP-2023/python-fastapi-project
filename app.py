# from fastapi import FastAPI
# from fastapi.responses import JSONResponse

# app = FastAPI()

# @app.get("/")
# def hello():
#     return "FastAPI running inside Docker!"

# @app.get("/health")
# def health():
#     return JSONResponse(
#         content={"status": "healthy", "app": "running"},
#         status_code=200
#     )

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

@app.get("/ping")
def ping():
    return JSONResponse(content={"message": "pong"}, status_code=200)
