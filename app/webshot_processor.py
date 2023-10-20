import multiprocessing

from sqlalchemy.orm import Session

from app.exceptions import ScreenshotEntryExists
from app.logger import logger
from app.webshot_driver import WebshotDriver
from db.constants import ScreenshotRequestStatus
from db.crud import create_screenshot_entry, get_todo_requests, update_request_entry
from db.db import SessionLocal
from db.schemas import Screenshot, Request
from root import ROOT_DIR


def process_screenshot(db_session: Session, request: Request):
    driver = WebshotDriver()
    urls = [request.url] + driver.get_links(url=request.url)[: request.num_of_urls]
    logger.info(f"URLs to be taken screenshot of: {urls}")
    for idx, url in enumerate(urls):
        screenshot_path = (
            f"{ROOT_DIR}/screenshots/{request.request_id}/screenshot_{idx}.png"
        )
        try:
            driver.save_screenshot(url, screenshot_path)
            create_screenshot_entry(
                db_session,
                Screenshot(request_id=request.request_id, path=screenshot_path, url=url),
            )
        except ScreenshotEntryExists:
            pass


def process_request(request: Request):
    db_session = SessionLocal()
    try:
        logger.info(
            f"Performing url gathering and screenshot for request {request.request_id} with starting "
            f"url {request.url} and maximum number of urls {request.num_of_urls}."
        )
        process_screenshot(db_session, request)
        request = update_request_entry(
            db_session, request.request_id, ScreenshotRequestStatus.DONE.name
        )
        logger.info(f"Processed request {request.request_id} successfully.")
    finally:
        db_session.close()


def log_processed_request(request: Request):
    logger.error(f"Request {request.request_id} processed successfully.")


def get_requests_scheduler_task():
    db_session = SessionLocal()
    try:
        requests = [
            Request(**request.to_dict()) for request in get_todo_requests(db_session)
        ]
        logger.info(f"Requests for processing: {len(requests)}.")
        for request in requests:
            update_request_entry(
                db_session, request.request_id, ScreenshotRequestStatus.PROCESSING.name
            )
        if len(requests):
            p = multiprocessing.Pool(len(requests))
            p.map_async(process_request, requests, callback=log_processed_request)
            p.close()
    finally:
        db_session.close()
