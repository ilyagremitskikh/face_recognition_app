from pydantic import BaseModel

class Star(BaseModel):
    face_location: tuple
    full_photo_filename: str
    data: dict
    distance: float = 0.0
    similarity: int = 0

