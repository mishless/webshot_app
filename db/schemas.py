import base64
from pathlib import Path
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field
from pydantic.types import datetime

from db.constants import ScreenshotRequestStatus


class Screenshot(BaseModel):
    request_id: str
    url: str
    path: str
    created: Optional[datetime] = None

    @computed_field  # type: ignore[misc]
    @property
    def data(self) -> bytes | None:
        if Path(self.path).exists():
            with open(self.path, "rb") as f:
                return base64.b64encode(f.read())
        return None

    class Config:
        from_attributes = True


class ScreenshotResponse(BaseModel):
    url: str
    data: bytes | None


class RequestBase(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))


class RequestCreate(BaseModel):
    url: str
    num_of_urls: int


class Request(RequestBase, RequestCreate):
    status: str = Field(default_factory=lambda: ScreenshotRequestStatus.TODO.name)
    updated: Optional[datetime] = None
    created: Optional[datetime] = None
    screenshots: list[Screenshot] = []

    class Config:
        from_attributes = True


class RequestResponse(RequestBase):
    pass
