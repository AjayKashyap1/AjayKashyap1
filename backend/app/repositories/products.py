from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domain.models import Product
from app.repositories.base import Repository

class ProductRepository(Repository[Product]):
    def __init__(self, db: Session):
        super().__init__(db, Product)

    def list_for_company(self, company_id: int) -> list[Product]:
        return list(self.db.scalars(select(Product).where(Product.company_id == company_id).order_by(Product.created_at.desc())))
