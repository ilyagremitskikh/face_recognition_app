from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile, status
from fastapi.staticfiles import StaticFiles
from PIL import UnidentifiedImageError
from utils.exceptions import NoFacesFoundError, WrongNumberOfFacesError
from classes.index import Faiss
from utils.base_logger import logger
from utils.config import load_config
from models import models
import json
import face_recognition

config = load_config()


async def verify_key(x_key: str = Header()):
    if x_key != config.secret_api_key:
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


app = FastAPI(dependencies=[Depends(verify_key)])
app.mount(
    "/static", StaticFiles(directory=f"{config.data_folder_path}/photos/"), name="static")


@app.on_event("startup")
async def startup_event():

    global data_dict
    data_json = Path(f"{config.data_folder_path}/stars_data.json")
    with open(data_json, "r") as f:
        data_dict = json.load(f)

    global faiss
    faiss = Faiss("euclidean", 128, f"{config.data_folder_path}/Faiss.index")
    if not Path(f"{config.data_folder_path}/Faiss.index").is_file():
        logger.error(
            f"Faiss index file not found! Please move it to the {config.data_folder_path} folder!")
    faiss.load()


@app.post(
    "/stars/",
    response_model=List[models.Star],
    summary="Get similar stars",
    response_description="List of Similar stars",
    responses={
        404: {"description": "Suitable results not found"},
        406: {"description": "Number of faces on given image is more than 1"},
        415: {"description": "Cannot identify image file"},
        422: {"description": "Can't find faces on image"},
    },
)
async def stars(file: UploadFile, number_of_neighbors: int = 10, similarity_threshold: int = 60):
    """
    Get similar stars for uploaded human face photo
     - **file**: human face photo
     - **number_of_neighbors**: number of similar stars to return
     - **similarity_threshold**: minimum similarity percentage to return
    """
    try:
        image = face_recognition.api.load_image_file(file.file)
        encodings = face_recognition.api.face_encodings(image)
        if len(encodings) > 1:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="Number of faces on given image is more than 1")
        encoding = encodings[0]
    except (
        UnidentifiedImageError
    ):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail="Cannot identify image file")
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Can't find faces on image")

    neighbors, distances = faiss.get_neighbors(
        vector=encoding, n=number_of_neighbors)
    stars = []
    for index, faiss_index_number in enumerate(neighbors):

        star = models.Star(**data_dict[str(faiss_index_number)])
        star.distance = distances[index]
        star.similarity = round((1 - star.distance) * 100)
        stars.append(star)

    result = [star for star in stars if star.similarity > similarity_threshold]

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Suitable results not found"
        )
    else:
        return result
