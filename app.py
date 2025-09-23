from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# -------------------------
# Config
# -------------------------
DB_HOST = "ls-2867d292ceed2c7ab16125c87c3b818f75a73a16.cw80mnlb8rfq.ap-southeast-1.rds.amazonaws.com"
DB_USER = "yollinkAdmin"
DB_PASSWORD = "yollinkAdmin"
DB_DATABASE = "dbyollink"
VALID_ACCESS_TOKEN = "testing123"

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_DATABASE}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# -------------------------
# DB Model (core fields only)
# -------------------------
class BatchMaster(Base):
    __tablename__ = "batch_master"

    order_id = Column(Integer)
    plant = Column(String(50))
    customer = Column(String(255))
    bay = Column(String(255))
    status = Column(String(50))
    job_number = Column(String(50))
    batch_number = Column(String(50), primary_key=True)
    quantity = Column(Integer)
    projected_start = Column(DateTime)
    projected_end = Column(DateTime)
    units_completed = Column(Integer)
    rev = Column(String(50))
    active = Column(Boolean)


# -------------------------
# Security
# -------------------------
def verify_token(access_token: str = Header(..., alias="Access-Token")):
    if access_token != VALID_ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Access-Token")
    return access_token


# -------------------------
# FastAPI App
# -------------------------
app = FastAPI()


def batch_to_dict(b: BatchMaster):
    """Map DB row → API response"""
    return {
        "id": b.order_id,
        "batch": b.batch_number,
        "part number": b.job_number,
        "revision": b.rev,
        "quantity": b.quantity,
        "bay": b.bay,
        "projected start": b.projected_start.strftime("%Y-%m-%d %H:%M:%S") if b.projected_start else None,
        "projected stop": b.projected_end.strftime("%Y-%m-%d %H:%M:%S") if b.projected_end else None,
        "units completed": b.units_completed,
        "status": b.status,
        "active": bool(b.active) if b.active is not None else None
    }


@app.get("/batch_masters/")
def get_batches(token: str = Depends(verify_token)):
    db = SessionLocal()
    try:
        batches = db.query(BatchMaster).all()
        return [batch_to_dict(b) for b in batches]
    finally:
        db.close()


@app.post("/batch_masters/lookup")
def lookup_batch(payload: dict, token: str = Depends(verify_token)):
    batch_no = payload.get("batch")
    if not batch_no:
        raise HTTPException(status_code=400, detail="batch required")

    db = SessionLocal()
    try:
        b = db.query(BatchMaster).filter(BatchMaster.batch_number == batch_no).first()
        if not b:
            raise HTTPException(status_code=404, detail="Batch not found")
        return batch_to_dict(b)
    finally:
        db.close()