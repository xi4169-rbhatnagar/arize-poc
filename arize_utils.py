import os
from datetime import datetime, timezone
from typing import Any
from typing import List

import httpx
import pandas as pd
from httpx import Client

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


class AnnotationReporter:
    _query = """
    query ($projectId: GlobalID!, $after: String) {
      node(id: $projectId) {
        ... on Project {
          spans(first: 1000, after: $after) {
            pageInfo {
              endCursor
              hasNextPage
            }
            edges {
                node {
                  startTime
                  endTime
                  context {
                    spanId
                  }
                  spanAnnotations {
                    name
                    score
                    label
                    explanation
                    annotatorKind
                  }
                }
              }
          }
        }
      }
    }
    """

    @staticmethod
    def _get_df(spans: dict[str, Any]) -> pd.DataFrame:
        """Convert the spans output from GraphQL to a df"""
        df = pd.json_normalize(filter(lambda e: e["node"]["spanAnnotations"], spans['edges']))
        if df.empty:
            return df
        df = df.rename({"node.context.spanId": "span_id"}, axis=1).set_index("span_id")
        exploded = df.loc[:, "node.spanAnnotations"].explode()
        exploded = pd.json_normalize(exploded).set_index(exploded.index)
        exploded['startTime'] = pd.to_datetime(df['node.startTime'], errors='coerce', utc=True)
        exploded['endTime'] = pd.to_datetime(df['node.endTime'], errors='coerce', utc=True)
        return exploded

    @classmethod
    def _get_annotations(cls, project_id: str, base_url: str) -> pd.DataFrame:
        dfs = []
        has_next_page, after = True, ""
        while has_next_page:
            response = Client(base_url=base_url).post(
                "/graphql",
                json={
                    "query": cls._query,
                    "variables": {
                        "projectId": project_id,
                        "after": after,
                    },
                },
            )
            spans = response.json()["data"]["node"]["spans"]
            if not (df := cls._get_df(spans)).empty:
                dfs.append(df)
            has_next_page = spans["pageInfo"]["hasNextPage"]
            after = spans["pageInfo"]["endCursor"]
        return pd.concat(dfs)

    @classmethod
    def get_annotations_between(cls, project_id: str, start_time: datetime, end_time: datetime) -> pd.DataFrame:
        base_url = os.environ.get('ARIZE_URL')
        df = cls._get_annotations(project_id, base_url)
        if df.empty:
            return pd.DataFrame()

        if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        else:
            start_time = start_time.astimezone(timezone.utc)

        if end_time.tzinfo is None or end_time.tzinfo.utcoffset(end_time) is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        else:
            end_time = end_time.astimezone(timezone.utc)

        filtered_df = df[(df['startTime'] >= start_time) & (df['endTime'] <= end_time)]
        return filtered_df
