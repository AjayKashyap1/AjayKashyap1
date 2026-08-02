from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl
from app.domain.models import ProductStatus, Role, StockStatus

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    remember_me: bool = False

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int
    email: EmailStr
    full_name: str
    role: Role

class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    brand: str
    category: str
    image_url: HttpUrl | None = None
    blinkit_url: HttpUrl
    competitor_urls: list[HttpUrl] = []

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: str
    brand: str
    category: str
    image_url: str | None
    blinkit_url: str
    blinkit_product_id: str
    status: ProductStatus
    created_at: datetime

class ScanRequest(BaseModel):
    product_ids: list[int] = Field(min_length=1)
    city_ids: list[int] | None = None
    scheduled_at: datetime | None = None

class CityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    pincode: str
    latitude: float
    longitude: float
    timezone: str

class AvailabilityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    city_id: int
    is_available: bool
    price: float | None
    mrp: float | None
    discount_percent: float | None
    eta_minutes: int | None
    dark_store: str | None
    stock_status: StockStatus
    observed_at: datetime
