from abc import ABC, abstractmethod
from typing import List, Tuple

import faiss
import numpy as np
from typing_extensions import Literal


class Index(ABC):
    @abstractmethod
    def index_len(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def add_vectors(self, vectors: List[np.ndarray]):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def get_neighbors(self, vector, n: int = 5) -> Tuple[List[int], List[float]]:
        pass


class Faiss(Index):
    def __init__(self,
                 metric: Literal["cosine", "euclidean"],
                 dimensions: int = 128,
                 index_path: str = "Faiss.index", ) -> None:
        self.metric = metric
        self.dimensions = dimensions
        self.index_path = index_path

    @property
    def index_len(self):
        if self.index_obj:
            return self.index_obj.ntotal
        else:
            return None

    def create(self):
        if self.metric == "euclidean":
            self.index_obj = faiss.IndexFlatL2(self.dimensions)
        elif self.metric == "cosine":
            self.index_obj = faiss.IndexFlatIP(self.dimensions)

    def add_vectors(self, vectors: List[List]):
        vectors = np.array(vectors, dtype="f")  # type: ignore
        if self.metric == "cosine":
            faiss.normalize_L2(vectors)
        self.index_obj.add(vectors)  # type: ignore

    def save(self):
        faiss.write_index(self.index_obj, self.index_path)

    def load(self):
        self.index_obj = faiss.read_index(self.index_path)

    def get_neighbors(self, vector, n: int = 5) -> Tuple[List[int], List[float]]:
        vector = np.array(vector, dtype="f")
        vector = np.expand_dims(vector, axis=0)
        distances, neighbors = self.index_obj.search(vector, n)  # type: ignore
        return neighbors.tolist()[0], distances.tolist()[0]
