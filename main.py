import requests
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, status, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.logger import logger
from app.webshot_processor import get_requests_scheduler_task
from db.crud import get_screenshots_by_request_id, create_request_entry
from db.db import SessionLocal, engine
from db.models import Base
from db.schemas import (
    RequestResponse,
    RequestCreate,
    Screenshot,
    ScreenshotResponse,
    Request,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()


class HealthCheck(BaseModel):
    status: str = "OK"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def init_data():
    scheduler = BackgroundScheduler(executors={"default": ProcessPoolExecutor(1)})
    scheduler.add_job(get_requests_scheduler_task, "cron", second="*/5")
    scheduler.start()


@app.get("/isalive", status_code=status.HTTP_200_OK)
def is_alive() -> HealthCheck:
    return HealthCheck(status="OK")


@app.post("/screenshot", response_model=RequestResponse)
def create_screenshot_request_endpoint(
    request: RequestCreate, db: Session = Depends(get_db)
):
    logger.info(f"Received new screenshot request: {request}.")
    try:
        response = requests.head(request.url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, detail=f"Page does not exist: {request.url}."
            )
    except Exception:
        raise HTTPException(status_code=422, detail=f"Invalid URL/page: {request.url}.")
    request_response = create_request_entry(
        db=db, request=Request(**request.model_dump())
    )
    return request_response


@app.get("/screenshot/{request_id}", response_model=list[ScreenshotResponse])
def get_screenshots_by_request_id_endpoint(
    request_id: str, db: Session = Depends(get_db)
):
    screenshots = [
        Screenshot(**screenshot.to_dict())
        for screenshot in get_screenshots_by_request_id(db, request_id)
    ]
    return [
        ScreenshotResponse(url=screenshot.url, data=screenshot.data)
        for screenshot in screenshots
    ]
