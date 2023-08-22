from pydantic import BaseModel


class UploadFileSchema(BaseModel):
    item_type: str
    item_id: int
    file_no: int
