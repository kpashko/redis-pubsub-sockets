from pydantic import BaseModel, Field


class ResponseErrorSchema(BaseModel):
    """
    Common Error schema for error data objects
    """

    message: str = Field(example="Error message")
