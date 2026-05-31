from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class DemoItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    tenant_id: uuid.UUID
