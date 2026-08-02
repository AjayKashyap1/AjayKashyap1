import asyncio
from datetime import datetime
from celery.utils.log import get_task_logger
from sqlalchemy import select
from app.core.database import SessionLocal
from app.domain.models import AvailabilityHistory, City, Product, Scan, ScanStatus
from app.services.scanner import BlinkitScanner
from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)

@celery_app.task(bind=True, autoretry_for=(TimeoutError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def run_scan(self, company_id: int, product_ids: list[int], city_ids: list[int] | None = None):
    db = SessionLocal()
    scanner = BlinkitScanner()
    scan = Scan(company_id=company_id, status=ScanStatus.running, scan_type="availability", parameters={"product_ids": product_ids, "city_ids": city_ids}, started_at=datetime.utcnow())
    db.add(scan)
    db.commit()
    try:
        products = list(db.scalars(select(Product).where(Product.company_id == company_id, Product.id.in_(product_ids))))
        city_query = select(City)
        if city_ids:
            city_query = city_query.where(City.id.in_(city_ids))
        cities = list(db.scalars(city_query))
        for product in products:
            for city in cities:
                snapshot = asyncio.run(scanner.scan_product_city(product.blinkit_url, city.latitude, city.longitude))
                db.add(AvailabilityHistory(company_id=company_id, product_id=product.id, city_id=city.id, scan_id=scan.id, is_available=snapshot.is_available, price=snapshot.price, mrp=snapshot.mrp, discount_percent=snapshot.discount_percent, eta_minutes=snapshot.eta_minutes, dark_store=snapshot.dark_store, stock_status=snapshot.stock_status))
                db.commit()
        scan.status = ScanStatus.completed
        scan.finished_at = datetime.utcnow()
        db.commit()
        return {"scan_id": scan.id, "status": scan.status.value}
    except Exception:
        logger.exception("Scan failed", extra={"scan_id": scan.id})
        scan.status = ScanStatus.failed
        scan.finished_at = datetime.utcnow()
        db.commit()
        raise
    finally:
        db.close()
