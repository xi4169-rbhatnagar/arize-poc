import os
from typing import List

import httpx

from model import Annotation


def annotate(span_id: str, annotations: List[Annotation]):
    hclient = httpx.Client()

    annotation_payload = {
        "data": [*map(lambda a: a.to_payload(span_id), annotations)],
    }

    return hclient.post(
        os.environ.get('ARIZE_URL') + "/v1/span_annotations?sync=false",
        json=annotation_payload,
    )
