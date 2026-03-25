from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models.user import UserCreate, UserResponse

router = APIRouter(tags=["users"])


@router.post("/users", response_model=UserResponse)
async def create_user(data: UserCreate):
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO users (name) VALUES (?)", (data.name,)
        )
        await db.commit()
        user_id = cursor.lastrowid
        row = await db.execute_fetchall(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        )
        return dict(row[0])
    finally:
        await db.close()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    db = await get_db()
    try:
        rows = await db.execute_fetchall(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        )
        if not rows:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(rows[0])
    finally:
        await db.close()


@router.get("/users", response_model=list[UserResponse])
async def list_users():
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(row) for row in rows]
    finally:
        await db.close()
