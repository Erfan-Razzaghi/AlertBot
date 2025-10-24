from pydantic import BaseModel
from typing import List


class AlertPrometheus(BaseModel):
    status: str = "firing default"
    labels: dict = {}
    annotations: dict = {}
    startsAt: str = ""
    endsAt: str = ""
    generator_url: str = ""
    fingerprint: str = ""

class AlertRequestPrometheus(BaseModel):
    receiver: str = "Default"
    status: str = "firing default"
    alerts: List[AlertPrometheus] = []
    commonLabels: dict = {}
    commonAnnotations: dict = {}