import http
from datetime import datetime, timedelta

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.http_params import FeedbackRequest, ReportRequest
from services.feedback.handler import mark_user_feedback, get_feedback_summary


def get_router() -> APIRouter:
    feedback_router = APIRouter(prefix="/feedback", tags=["feedback"])

    @feedback_router.post('/')
    def user_feedback(request: FeedbackRequest):
        if request.feedback not in (0, 1):
            return JSONResponse("feedback must be either 0/1", http.HTTPStatus.BAD_REQUEST)
        return mark_user_feedback(request.span_id, "thumbs-down" if request.feedback == 0 else "thumbs-up")

    @feedback_router.get('/report')
    def get_report(request: ReportRequest):
        ist_offset = timedelta(hours=5, minutes=30)
        start_time_dt = datetime.strptime(request.start_time, '%Y-%m-%d %H:%M:%S')
        end_time_dt = datetime.strptime(request.end_time, '%Y-%m-%d %H:%M:%S')

        start_time = start_time_dt - ist_offset
        end_time = end_time_dt - ist_offset
        return get_feedback_summary(start_time, end_time, request.project_id)

    return feedback_router
