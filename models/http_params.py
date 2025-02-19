from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    span_id: str
    feedback: str


class ReportRequest(BaseModel):
    start_time: str
    end_time: str
    project_id: str
