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

# @app.get("/info")
# def info():
#     return JSONResponse(
#         content={
#             "service": "fastapi-docker",
#             "version": "1.0.0",
#             "docs": "/docs",
#         },
#         status_code=200,
#     )
