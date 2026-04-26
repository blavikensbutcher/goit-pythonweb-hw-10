

from types.contract import UpdateContactDto
from types.contract import ContactDto
from types.contract import ContactDtoResponse
from fastapi import Query
from typing import Optional
from typing import  List

from fastapi import APIRouter, Depends, HTTPException

from src.database import get_db
from src.models.user import UserModel
from src.services.contacts import get_contacts_service
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.users import get_current_user_from_token



router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
    dependencies=[Depends(get_current_user_from_token)] 
)


contactsService = get_contacts_service()

@router.get("", response_model=List[ContactDtoResponse])
async def get_contacts(
    name: Optional[str] = Query(default=None, description="Filter by first name"),
    surname: Optional[str] = Query(default=None, description="Filter by surname"),
    email: Optional[str] = Query(default=None, description="Filter by email"),
    db: AsyncSession = Depends(get_db),
):
    return await contactsService.get_contacts(
        db=db,
        name=name,
        surname=surname,
        email=email,
    )
    
@router.get("/birthdays/upcoming", response_model=List[ContactDtoResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    return await contactsService.find_contacts_birthday_in_week(db)
    
@router.post("", response_model=ContactDtoResponse)
async def create_contact(contact_data: ContactDto, db: AsyncSession = Depends(get_db), user: UserModel = Depends(get_current_user_from_token)):
    return await contactsService.create_contact(db, contact_data, user.id)

@router.get("/{contact_id}", response_model=ContactDtoResponse)
async def get_contact(contact_id: str, db: AsyncSession = Depends(get_db), user: UserModel = Depends(get_current_user_from_token)):
    try:
        contact = await contactsService.get_contact_by_id(db, contact_id, user.id   )
        return contact
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: str, db: AsyncSession = Depends(get_db), user: UserModel = Depends(get_current_user_from_token)):
    try:
        await contactsService.remove_contact_by_id(db, contact_id, user.id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{contact_id}", response_model=ContactDto)
async def update_contact(
    contact_id: str,
    contact_data: UpdateContactDto,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user_from_token)
):
    existing_contact = await contactsService.get_contact_by_id(db, contact_id, user.id)
    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact_data.model_dump(exclude_none=True).items():
        setattr(existing_contact, key, value)

    await db.commit()

    await db.refresh(existing_contact)

    return existing_contact