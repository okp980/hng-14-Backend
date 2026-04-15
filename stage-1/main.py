from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

GENDERIZE_API_KEY = os.getenv("GENDERIZE_API_KEY")


class CustomHTTPException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


app = FastAPI()


@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"status": "error", "message": exc.message}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422, content={"status": "error", "message": "name is not a string"}
    )


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/api/classify")
async def classify(name: str):
    if not name:
        raise CustomHTTPException(
            status_code=400,
            message="Missing or empty name parameter",
        )
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=3.0)
        ) as client:
            response = await client.get(
                f"https://api.genderize.io/?name={name}&key={GENDERIZE_API_KEY}"
            )
            data = response.json()
            if data["gender"] is None or data["count"] == 0:
                raise CustomHTTPException(
                    status_code=404,
                    message="No prediction available for the provided name",
                )
            response.raise_for_status()
            return {
                "status": "success",
                "data": {
                    "name": name,
                    "gender": data["gender"],
                    "probability": data["probability"],
                    "sample_size": data["count"],
                    "is_confident": True
                    if data["probability"] >= 0.7 and data["count"] >= 100
                    else False,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                },
            }
    except httpx.HTTPError:
        return CustomHTTPException(
            status_code=500,
            message="Upstream or server failure",
        )
