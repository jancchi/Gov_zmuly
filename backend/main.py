from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, create_engine, select
from sqlalchemy.orm import selectinload
from app.models import SQLModel, ProcurementNotice
from app.parser import get_component_value, analyze_red_flags
import json
from typing import List
from datetime import datetime
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Logic here runs ON STARTUP
    SQLModel.metadata.create_all(engine)
    yield
    # Logic here runs ON SHUTDOWN (optional)
    # e.g., engine.dispose()

# 3. Pass the lifespan to the FastAPI constructor
app = FastAPI(title="Red Flag System Backend", lifespan=lifespan)

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/import-file")
def import_from_file(session: Session = Depends(get_session)):
    try:
        with open("../data/44_2026.json", 'r', encoding='utf-8') as f:
            print(f.read())
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Broken JSON file: {str(e)}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")


    # print("data", data)
    try:
        clean_date = data["bulletinPublishDate"].replace("Z", "+00:00")
        bulletin_date = datetime.fromisoformat(clean_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")

    count = 0

    for item in data["bulletinItemList"]:
        # Niektoré itemData sú stringy, iné dict (v závislosti od exportu)
        raw_item = item["itemData"]
        item_data = json.loads(raw_item) if isinstance(raw_item, str) else raw_item
        comps = item_data.get("components", [])

        # Extrakcia dát
        tender_id = item_data.get("id")
        title = get_component_value(comps, "DL-Metadata-Order") or item_data.get("name")
        org = get_component_value(comps, "DL-Metadata-Partner") or "Neznáma org."
        val_str = get_component_value(comps, "BT-27-Procedure_value")
        deadline_str = get_component_value(comps, "BT-131(d)-Lot")
        bids = get_component_value(comps, "BT-759-LotResult")

        tender = ProcurementNotice(
            id=tender_id,
            title=title,
            organization=org,
            estimated_value=float(val_str.replace(" ", "")) if val_str else None,
            deadline=datetime.fromisoformat(deadline_str) if deadline_str else None,
            bids_count=int(bids) if bids else None,
            publish_date=bulletin_date,
            raw_json=json.dumps(item_data)
        )
        #
        # # Standard string fields
        # submission_id: Optional[str] = Field(default=None, index=True)
        # notice_name: Optional[str] = Field(default=None)
        # form_type: Optional[str] = Field(default=None, index=True)
        # buyer: Optional[str] = Field(default=None)
        # order_title: Optional[str] = Field(default=None)
        # procedure_type: Optional[str] = Field(default=None)
        #
        # # Boolean and Float fields
        # is_eu_funded: bool = Field(default=False)
        # estimated_value_eur: Optional[float] = Field(default=None)
        # awarded_value_eur: Optional[float] = Field(default=None)
        #
        # # PostgreSQL-specific Array fields
        # # We use sqlalchemy.dialects.postgresql.ARRAY to map Python lists to Postgres Arrays
        # submissions_counts: List[int] = Field(
        #     default_factory=list,
        #     sa_column=Column(ARRAY(Integer))
        # )
        #
        # flags: List[str] = Field(
        #     default_factory=list,
        #     sa_column=Column(ARRAY(String))
        # )
        #
        # # PostgreSQL-specific JSONB field for the raw, flattened data
        # # JSONB is highly optimized in Postgres for indexing and querying nested data
        # raw_data: Dict[str, Any] = Field(
        #     default_factory=dict,
        #     sa_column=Column(JSONB)
        # )

        # Pridanie Red Flags
        flags_data = analyze_red_flags(tender.model_dump(), comps)
        for f in flags_data:
            session.add(f)

        session.add(tender)
        count += 1

    session.commit()
    return {"message": f"Importovaných {count} tendrov"}

@app.get("/notices", response_model=List[ProcurementNotice])
def list_notices(session: Session = Depends(get_session)):
    # This ensures red_flags are included in the JSON response
    statement = select(ProcurementNotice).options(selectinload(ProcurementNotice.flags))
    results = session.exec(statement).all()
    return results
