from __future__ import annotations

"""Check an operator-installed approval against the exact proposed model inputs."""

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, ValidationError

if TYPE_CHECKING:
    from .or_engine.models import ORBase
    from .schemas import OptimizeRequest


class ReviewRecord(BaseModel):
    revision: int = Field(ge=1)
    state: str
    effective_from: datetime
    expires_at: datetime
    change_note: str = Field(min_length=1)


def model_digest(request: OptimizeRequest | ORBase) -> str:
    payload = json.dumps([type(request).__name__, request.model_dump(mode="json")], sort_keys=True, allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def has_current_review(request: OptimizeRequest | ORBase) -> bool:
    directory = os.getenv("CLINOR_REVIEW_DIRECTORY")
    if not directory or not request.guideline_approval:
        return False
    try:
        path = Path(directory) / (model_digest(request) + ".json")
        record = ReviewRecord.model_validate_json(path.read_bytes())
        now = datetime.now(UTC)
        return record.state == "approved" and record.effective_from <= now < record.expires_at
    except (OSError, ValidationError, TypeError, ValueError):
        return False
