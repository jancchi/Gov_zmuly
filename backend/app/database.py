from typing import List
from sqlmodel import SQLModel, Session, create_engine
from models import ProcurementNotice
import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def insert_notices(parsed_notices: List[dict]):
    """Inserts a list of parsed dictionary notices into the database."""
    with Session(engine) as session:
        for notice_dict in parsed_notices:
            # Create a SQLModel instance from the dictionary
            notice = ProcurementNotice(**notice_dict)
            session.add(notice)

        # Commit all instances to the database
        session.commit()


if __name__ == "__main__":
    # 1. Initialize DB tables
    init_db()

    # 2. Mock data mimicking the parser's output
    mock_parsed_data = [{
        "submission_id": "1391671",
        "notice_name": "Oprava: Oznámenie o vyhlásení...",
        "form_type": "competition",
        "buyer": "Mesto Košice",
        "order_title": "Pasportizácia mestskej infraštruktúry",
        "procedure_type": "open",
        "is_eu_funded": False,
        "estimated_value_eur": 150000.0,
        "awarded_value_eur": None,
        "submissions_counts": [],
        "flags": ["NON_STANDARD_PROCEDURE_OPEN"],
        "raw_data": {"BT-02-notice": "cn-standard", "DL-Metadata-Partner": "Mesto Košice (ID: 30452)"}
    }]

    # 3. Save to database
    insert_notices(mock_parsed_data)
    print("Successfully inserted notices into PostgreSQL.")