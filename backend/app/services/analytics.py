from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.domain.models import Alert, AvailabilityHistory, City, Product, StockStatus

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def dashboard(self, company_id: int) -> dict:
        total_products = self.db.scalar(select(func.count(Product.id)).where(Product.company_id == company_id)) or 0
        cities_live = self.db.scalar(select(func.count(func.distinct(AvailabilityHistory.city_id))).where(AvailabilityHistory.company_id == company_id)) or 0
        out_of_stock = self.db.scalar(select(func.count(AvailabilityHistory.id)).where(AvailabilityHistory.company_id == company_id, AvailabilityHistory.stock_status == StockStatus.out_of_stock)) or 0
        available = self.db.scalar(select(func.count(AvailabilityHistory.id)).where(AvailabilityHistory.company_id == company_id, AvailabilityHistory.is_available.is_(True))) or 0
        total_observations = self.db.scalar(select(func.count(AvailabilityHistory.id)).where(AvailabilityHistory.company_id == company_id)) or 0
        alerts = list(self.db.scalars(select(Alert).where(Alert.company_id == company_id).order_by(Alert.created_at.desc()).limit(8)))
        top_cities = self.db.execute(select(City.name, func.count(AvailabilityHistory.id).label("observations")).join(AvailabilityHistory, AvailabilityHistory.city_id == City.id).where(AvailabilityHistory.company_id == company_id, AvailabilityHistory.is_available.is_(True)).group_by(City.name).order_by(func.count(AvailabilityHistory.id).desc()).limit(10)).all()
        return {
            "totalProducts": total_products,
            "coveragePercent": round((available / total_observations) * 100, 2) if total_observations else 0,
            "citiesLive": cities_live,
            "outOfStock": out_of_stock,
            "competitors": 0,
            "priceChanges": 0,
            "todaysScan": total_observations,
            "latestAlerts": [{"id": a.id, "severity": a.severity, "message": a.message, "createdAt": a.created_at.isoformat()} for a in alerts],
            "topCities": [{"name": name, "observations": count} for name, count in top_cities],
        }
