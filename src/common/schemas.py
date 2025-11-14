from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseModelSchema(BaseModel):
    id: int = Field(description='The model id')

    created_at: datetime = Field(description='The date this model was created')
    updated_at: datetime = Field(description='The date this model was updated')

    model_config = ConfigDict(from_attributes=True)

