from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from .database import get_session
from .model import Contract
import os

router = APIRouter(
    prefix="/contracts",
    tags=["AI Features"]
)

# This would be your internal AI logic function
def generate_ai_summary(text: str) -> str:
    # In a real app, you'd call an API here:
    # response = client.models.generate_content(model="gemini-2.0-flash", contents=text)
    if not text:
        return "No content available to summarize."
    return f"AI Summary: This contract covers {text[:50]}... [Summary logic here]"

@router.get("/{contract_id}/summary")
def get_contract_summary(
    contract_id: int,
    session: Session = Depends(get_session) # This "injects" the DB connection
):
    # 1. Fetch the contract from PostgreSQL using SQLModel
    statement = select(Contract).where(Contract.id == contract_id)
    contract = session.exec(statement).first()

    # 2. Handle the case where the ID doesn't exist
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found in database")

    # 3. Pass the contract text to your AI function
    # Assuming your Contract model has a field called 'content'
    summary_text = generate_ai_summary(contract.content)

    # 4. Return the result
    return {
        "contract_id": contract.id,
        "title": contract.title,
        "summary": summary_text
    }