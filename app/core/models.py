from typing import Any
from pydantic import BaseModel, Field

class JobCreateResponse(BaseModel):
    job_id: str
    task_id: str
    status: str

class JobStatusResponse(BaseModel):
    job_id: str
    task_id: str | None = None
    status: str
    progress: int = 0
    message: str | None = None
    mode: str | None = None
    profile: str | None = None
    analysis: dict[str, Any] = Field(default_factory=dict)
    decision: dict[str, Any] = Field(default_factory=dict)
    chain: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list)
    error: str | None = None
