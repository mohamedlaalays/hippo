from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Literal
from pydantic import BaseModel, Field, field_validator

class CallRequirement(BaseModel):
    customer_name: str
    avg_duration_sec: int = Field(gt=0)
    start_hour: int = Field(ge=0, le=23)
    end_hour: int = Field(ge=0, le=24)
    total_calls: int = Field(gt=0)
    priority: Literal[1, 2, 3, 4, 5]

    @field_validator("end_hour")
    def validate_hours(cls, v, info):
        start = info.data.get("start_hour")
        if start is not None and v <= start:
            # Allow end_hour == 24 even when start_hour == 0 (full day coverage)
            if not (v == 24 and start == 0):
                raise ValueError("end_hour must be > start_hour")
        return v

    @property
    def active_duration_hours(self):
        return self.end_hour - self.start_hour

    @property
    def calls_per_hour(self):
        if self.active_duration_hours <= 0:
            return 0
        return self.total_calls / self.active_duration_hours
    

class HourlyStat(BaseModel):
    hour: int = Field(ge=0, le=23, strict=True)
    total_agents: int = Field(default=0, ge=0, strict=True)
    breakdown: Dict[str, int] = Field(default_factory=dict)
