from dataclasses import dataclass
import os

@dataclass
class Config:
    secret_api_key: str
    data_folder_path: str

def load_config():
    config = Config(
        secret_api_key=os.getenv("SECRET_API_KEY"),
        data_folder_path=os.getenv("DATA_FOLDER_PATH")
    )
    return config