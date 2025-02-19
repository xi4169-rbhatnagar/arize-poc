from datetime import datetime

from models.model import Annotation
from modules.annotations import AnnotationHelper


def mark_user_feedback(span_id: str, feedback: str):
    AnnotationHelper.annotate(
        span_id,
        annotations=[
            Annotation('user-feedback', feedback, 1)
        ]
    )
    return f"Successfully processed the annotation request for span id: {span_id}"


def get_feedback_summary(start_time: datetime, end_time: datetime, project_id: str):
    df = AnnotationHelper.get_annotations_between(project_id, start_time, end_time)
    label_counts = df['label'].value_counts().to_dict()
    return dict(filter(lambda i: 'thumb' in i[0], label_counts.items()))
