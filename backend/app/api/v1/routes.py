from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.domain.models import City, Product, User
from app.repositories.products import ProductRepository
from app.schemas.schemas import CityRead, LoginRequest, ProductCreate, ProductRead, ScanRequest, Token, UserRead
from app.services.analytics import AnalyticsService
from app.services.scanner import BlinkitScanner
from app.workers.tasks import run_scan

router = APIRouter()

@router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return Token(access_token=create_access_token(str(user.id), user.role.value, user.company_id))

@router.get("/auth/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user

@router.get("/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return AnalyticsService(db).dashboard(user.company_id)

@router.get("/products", response_model=list[ProductRead])
def list_products(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProductRepository(db).list_for_company(user.company_id)

@router.post("/products", response_model=ProductRead)
def create_product(payload: ProductCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scanner = BlinkitScanner()
    product = Product(company_id=user.company_id, sku=payload.sku, brand=payload.brand, category=payload.category, image_url=str(payload.image_url) if payload.image_url else None, blinkit_url=str(payload.blinkit_url), blinkit_product_id=scanner.extract_product_id(str(payload.blinkit_url)))
    ProductRepository(db).add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/cities", response_model=list[CityRead])
def cities(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return list(db.scalars(select(City).order_by(City.name)))

@router.post("/scans")
def queue_scan(payload: ScanRequest, user: User = Depends(get_current_user)):
    task = run_scan.delay(user.company_id, payload.product_ids, payload.city_ids)
    return {"taskId": task.id, "status": "queued"}
