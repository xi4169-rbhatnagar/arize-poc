from datetime import datetime, timedelta

from fastapi import APIRouter

from models.http_params import FeedbackRequest, ReportRequest
from services.feedback.handler import mark_user_feedback, get_feedback_summary


def get_router() -> APIRouter:
    feedback_router = APIRouter(prefix="/feedback", tags=["feedback"])

    @feedback_router.post('/create')
    def user_feedback(request: FeedbackRequest):
        return mark_user_feedback(request.span_id, request.feedback)

    @feedback_router.get('/report')
    def get_report(request: ReportRequest):
        ist_offset = timedelta(hours=5, minutes=30)
        start_time_dt = datetime.strptime(request.start_time, '%Y-%m-%d %H:%M:%S')
        end_time_dt = datetime.strptime(request.end_time, '%Y-%m-%d %H:%M:%S')

        start_time = start_time_dt - ist_offset
        end_time = end_time_dt - ist_offset
        return get_feedback_summary(start_time, end_time, request.project_id)

    return feedback_router
