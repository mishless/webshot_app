from datetime import datetime

from sqlalchemy import Integer, Column, ForeignKey, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from db.db import Base


class WebshotAppBase(Base):
    __abstract__ = True

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


class Request(WebshotAppBase):
    __tablename__ = "requests"

    request_id = Column(String, primary_key=True, index=True)
    url = Column(String)
    num_of_urls = Column(Integer)
    status = Column(String)
    created = Column(DateTime, default=lambda: datetime.now())
    updated = Column(DateTime, default=lambda: datetime.now())

    screenshots = relationship("Screenshot", back_populates="request")


class Screenshot(WebshotAppBase):
    __tablename__ = "screenshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String, ForeignKey("requests.request_id"))
    path = Column(String)
    url = Column(String)
    created = Column(DateTime, default=lambda: datetime.now())
    __table_args__ = (UniqueConstraint(request_id, path, url, name="id_path_url_uc"),)

    request = relationship("Request", back_populates="screenshots")
