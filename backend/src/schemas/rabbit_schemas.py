from pydantic import BaseModel


class IncomingMessageSchema(BaseModel):
    project: str
    revision_id: str
    prev_revision_id: str | None = None
