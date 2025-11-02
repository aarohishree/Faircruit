"""
User models and schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from config import validate_object_id
from bson import ObjectId

class User(BaseModel):
    id: str = None
    username: str
    email: EmailStr
    role: str
    hashed_password: str
    company_id: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str}

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_recruiter(self) -> bool:
        return self.role == "recruiter"

    @property
    def is_applicant(self) -> bool:
        return self.role == "applicant"