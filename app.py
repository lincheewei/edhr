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
DB_DATABASE = "jof_simulation"
VALID_ACCESS_TOKEN = "testing123"

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_DATABASE}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# -------------------------
# DB Model - Matches your updated table structure exactly
# -------------------------
class BatchMaster(Base):
    __tablename__ = "batch_master"

    id = Column(Integer, primary_key=True)
    batch = Column(String(50), unique=True, nullable=False)
    part_number = Column(String(100))
    revision = Column(String(50))
    quantity = Column(Integer)
    bay = Column(String(255))
    projected_start = Column(DateTime)
    projected_stop = Column(DateTime)
    units_completed = Column(Integer)
    status = Column(String(50))
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
    """Convert DB row to exact JSON format"""
    return {
        "id": b.id,
        "batch": b.batch,
        "part number": b.part_number,
        "revision": b.revision,
        "quantity": b.quantity,
        "bay": b.bay,
        "projected start": b.projected_start.strftime("%Y-%m-%d %H:%M:%S") if b.projected_start else None,
        "projected stop": b.projected_stop.strftime("%Y-%m-%d %H:%M:%S") if b.projected_stop else None,
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
        b = db.query(BatchMaster).filter(BatchMaster.batch == batch_no).first()
        if not b:
            raise HTTPException(status_code=404, detail="Batch not found")
        return batch_to_dict(b)
    finally:
        db.close()