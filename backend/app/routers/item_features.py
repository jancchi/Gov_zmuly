from fastapi import APIRouter

router = APIRouter(
    prefix="/contracts",
    tags=["contracts"]
)

@router.get("/")
def get_contracts():
    return {"message": "Nothing for now!"}
