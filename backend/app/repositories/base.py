from typing import Generic, TypeVar
from sqlalchemy.orm import Session
from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)

class Repository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]):
        self.db = db
        self.model = model

    def get(self, object_id: int) -> ModelT | None:
        return self.db.get(self.model, object_id)

    def add(self, entity: ModelT) -> ModelT:
        self.db.add(entity)
        self.db.flush()
        return entity
