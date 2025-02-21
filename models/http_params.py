from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    user_id: str


class FeedbackRequest(BaseModel):
    span_id: str
    feedback: int
    category: Optional[str] = ''
    comment: Optional[str] = ''


class ReportRequest(BaseModel):
    start_time: str
    end_time: str
    project_id: str
