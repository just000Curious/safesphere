from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import UserResponse, ContactAdd, ContactResponse
from app.models.user import User, TrustedContact
from uuid import UUID

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return UserResponse.from_orm(current_user)

@router.post("/contacts", response_model=ContactResponse)
async def add_emergency_contact(
    contact: ContactAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if contact already exists
    result = await db.execute(
        select(TrustedContact).where(
            TrustedContact.user_id == current_user.id,
            TrustedContact.phone == contact.phone
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact already exists"
        )
    
    # Create contact
    new_contact = TrustedContact(
        user_id=current_user.id,
        name=contact.name,
        phone=contact.phone,
        email=contact.email,
        relationship=contact.relationship,
        is_primary=contact.is_primary
    )
    
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    
    return ContactResponse.from_orm(new_contact)

@router.get("/contacts", response_model=List[ContactResponse])
async def get_emergency_contacts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TrustedContact).where(TrustedContact.user_id == current_user.id)
    )
    contacts = result.scalars().all()
    
    return [ContactResponse.from_orm(contact) for contact in contacts]

@router.delete("/contacts/{contact_id}")
async def delete_emergency_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TrustedContact).where(
            TrustedContact.id == contact_id,
            TrustedContact.user_id == current_user.id
        )
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    await db.delete(contact)
    await db.commit()
    
    return {"message": "Contact deleted successfully"}
