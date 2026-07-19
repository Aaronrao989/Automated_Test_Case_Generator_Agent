"""Pydantic request/response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AnalysisStartRequest(_Base):
    source_type: Literal["github_url", "code_snippet"]
    source_data: str = Field(min_length=1, max_length=200_000)


class AnalysisJobResponse(_Base):
    job_id: str
    status: str
    created_at: datetime
