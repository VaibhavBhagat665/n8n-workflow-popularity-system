from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

Platform = Literal["YouTube", "Forum", "Google"]
Country = Literal["US", "IN"]


class WorkflowItem(BaseModel):
    workflow: str = Field(..., description="Workflow name or keyword")
    platform: Platform
    popularity_metrics: Dict[str, Any] = Field(
        ..., description="Platform-specific metrics and ratios"
    )
    country: Country
    popularity_score: float = Field(..., ge=0, le=1)
    source_url: Optional[str] = None
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowsResponse(BaseModel):
    total: int
    items: List[WorkflowItem]
    limit: int
    offset: int


class StatsResponse(BaseModel):
    updated_at: str
    by_platform: Dict[str, int]
    by_country: Dict[str, int]
    total: int
