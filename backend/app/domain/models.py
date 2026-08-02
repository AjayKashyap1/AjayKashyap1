from datetime import datetime
from enum import StrEnum
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Role(StrEnum):
    admin = "admin"
    manager = "manager"
    viewer = "viewer"

class ProductStatus(StrEnum):
    active = "active"
    paused = "paused"
    archived = "archived"

class StockStatus(StrEnum):
    available = "available"
    low_stock = "low_stock"
    out_of_stock = "out_of_stock"
    not_serviceable = "not_serviceable"

class ScanStatus(StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    paused = "paused"

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    users = relationship("User", back_populates="company")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.viewer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    company = relationship("Company", back_populates="users")

class State(Base):
    __tablename__ = "states"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    code: Mapped[str] = mapped_column(String(8), unique=True)
    cities = relationship("City", back_populates="state")

class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(primary_key=True)
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    pincode: Mapped[str] = mapped_column(String(12), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata")
    state = relationship("State", back_populates="cities")
    __table_args__ = (UniqueConstraint("state_id", "name", "pincode", name="uq_city_pincode"),)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    sku: Mapped[str] = mapped_column(String(80), index=True)
    brand: Mapped[str] = mapped_column(String(120), index=True)
    category: Mapped[str] = mapped_column(String(120), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500))
    blinkit_url: Mapped[str] = mapped_column(String(800))
    blinkit_product_id: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[ProductStatus] = mapped_column(Enum(ProductStatus), default=ProductStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    competitors = relationship("Competitor", back_populates="product", cascade="all, delete-orphan")

class Competitor(Base):
    __tablename__ = "competitors"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    url: Mapped[str] = mapped_column(String(800))
    product = relationship("Product", back_populates="competitors")

class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    status: Mapped[ScanStatus] = mapped_column(Enum(ScanStatus), default=ScanStatus.queued)
    scan_type: Mapped[str] = mapped_column(String(40))
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AvailabilityHistory(Base):
    __tablename__ = "availability_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    scan_id: Mapped[int | None] = mapped_column(ForeignKey("scans.id"), index=True)
    is_available: Mapped[bool] = mapped_column(Boolean)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    mrp: Mapped[float | None] = mapped_column(Numeric(10, 2))
    discount_percent: Mapped[float | None] = mapped_column(Float)
    eta_minutes: Mapped[int | None] = mapped_column(Integer)
    dark_store: Mapped[str | None] = mapped_column(String(160))
    stock_status: Mapped[StockStatus] = mapped_column(Enum(StockStatus))
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    alert_type: Mapped[str] = mapped_column(String(80), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="info")
    message: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity: Mapped[str] = mapped_column(String(120))
    entity_id: Mapped[str | None] = mapped_column(String(80))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
