from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from typing import Union

# Database config
DB_HOST = "ls-2867d292ceed2c7ab16125c87c3b818f75a73a16.cw80mnlb8rfq.ap-southeast-1.rds.amazonaws.com"
DB_USER = "yollinkAdmin"
DB_PASSWORD = "yollinkAdmin"
DB_DATABASE = "dbyollink"

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Config:
    from_attributes = True

class BatchMaster(Base):
    __tablename__ = "batch_master"

    name = Column('batch_number', String(255), primary_key=True)  # batch_number in DB
    customer = Column('customer', String(255))
    drawing_revision = Column('rev', String(255))
    part_description = Column('comments', String(255))
    part_number = Column('job_number', String(255))
    line = Column('plant', String(255))
    lot_quantity = Column('quantity', Integer, nullable=True)  # mapped as Integer
    date_time_start = Column('projected_start', DateTime)
    date_time_end = Column('projected_end', DateTime)

class BatchMasterOut(BaseModel):
    name: str
    customer: Optional[str]
    drawing_revision: Optional[str]
    part_description: Optional[str]
    part_number: Optional[str]
    line: Optional[str]
    lot_quantity: Optional[str]
    date_time_start: Optional[datetime.datetime]
    date_time_end: Optional[datetime.datetime]

    class Config:
        from_attributes = True

app = FastAPI()

@app.get("/batch_masters/", response_model=List[BatchMasterOut])
def get_batch_masters():
    db = SessionLocal()
    try:
        batches = db.query(BatchMaster).all()
        for batch in batches:
            batch.lot_quantity = str(batch.lot_quantity) if batch.lot_quantity is not None else None
        return batches
    finally:
        db.close()


@app.get("/batch_masters/{batch_no}", response_model=BatchMasterOut)
def get_batch_master(batch_no: str):
    db = SessionLocal()
    try:
        batch = db.query(BatchMaster).filter(BatchMaster.name == batch_no).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        # Convert lot_quantity to string if not None
        if batch.lot_quantity is not None:
            batch.lot_quantity = str(batch.lot_quantity)
        return batch
    finally:
        db.close()

