from typing import List, Optional, Any, Dict
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

class ProcurementNotice(SQLModel, table=True):
    __tablename__ = "procurement_notice"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Standard string fields
    submission_id: Optional[str] = Field(default=None, index=True)
    notice_name: Optional[str] = Field(default=None)
    form_type: Optional[str] = Field(default=None, index=True)
    buyer: Optional[str] = Field(default=None)
    order_title: Optional[str] = Field(default=None)
    procedure_type: Optional[str] = Field(default=None)

    # Boolean and Float fields
    is_eu_funded: bool = Field(default=False)
    estimated_value_eur: Optional[float] = Field(default=None)
    awarded_value_eur: Optional[float] = Field(default=None)

    # PostgreSQL-specific Array fields
    # We use sqlalchemy.dialects.postgresql.ARRAY to map Python lists to Postgres Arrays
    submissions_counts: List[int] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Integer))
    )

    flags: List[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String))
    )

    # PostgreSQL-specific JSONB field for the raw, flattened data
    # JSONB is highly optimized in Postgres for indexing and querying nested data
    raw_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
