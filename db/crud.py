from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ScreenshotEntryExists
from db import models, schemas
from db.constants import ScreenshotRequestStatus


def get_request(db: Session, request_id: str):
    return (
        db.query(models.Request).filter(models.Request.request_id == request_id).first()
    )


def get_todo_requests(db: Session):
    since = datetime.now() - timedelta(minutes=5)

    return (
        db.query(models.Request)
        .filter(
            or_(
                models.Request.status == ScreenshotRequestStatus.TODO.name,
                and_(
                    models.Request.status == ScreenshotRequestStatus.PROCESSING.name,
                    models.Request.updated < since,
                ),
            )
        )
        .all()
    )


def create_request_entry(db: Session, request: schemas.Request):
    db_request = models.Request(**request.model_dump())
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def update_request_entry(db: Session, request_id: str, status: str):
    db_request = (
        db.query(models.Request).filter(models.Request.request_id == request_id).first()
    )
    if not db_request:
        raise HTTPException(status_code=404, detail="Screenshot request not found")
    db_request.updated = datetime.now()
    db_request.status = status
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def get_screenshots_by_request_id(db: Session, request_id: str):
    return (
        db.query(models.Screenshot)
        .filter(models.Screenshot.request_id == request_id)
        .all()
    )


def create_screenshot_entry(db: Session, screenshot: schemas.Screenshot):
    db_screenshot = models.Screenshot(
        request_id=screenshot.request_id, path=screenshot.path, url=screenshot.url
    )
    db.add(db_screenshot)
    try:
        db.commit()
        db.refresh(db_screenshot)
    except IntegrityError:
        db.rollback()
        raise ScreenshotEntryExists
    return db_screenshot
