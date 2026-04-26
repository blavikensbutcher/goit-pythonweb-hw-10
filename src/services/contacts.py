from types.contract import ContactDto
from sqlalchemy import or_
from models.contacts import ContactModel
from sqlalchemy import func
from datetime import timedelta
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ContactsService:
    @staticmethod
    async def get_contacts(db: AsyncSession, name: str | None = None, surname: str | None = None, email: str | None = None):
        query = select(ContactModel)
        if name:
            query = query.where(ContactModel.name == name)
        if surname:
            query = query.where(ContactModel.surname == surname)
        if email:
            query = query.where(ContactModel.email == email)
        result = await db.execute(query)
        contacts = result.scalars().all()
        return contacts
    
    @staticmethod
    async def find_contacts_birthday_in_week(db: AsyncSession):
            today = date.today()
            next_week = today + timedelta(days=7)

            today_md = today.strftime("%m-%d")
            next_week_md = next_week.strftime("%m-%d")
            birthday_month_day = func.to_char(ContactModel.birthday, "MM-DD")

            if today_md <= next_week_md:
                query = select(ContactModel).where(
                    birthday_month_day.between(today_md, next_week_md)
                )
            else:
                query = select(ContactModel).where(
                    or_(
                        birthday_month_day >= today_md,
                        birthday_month_day <= next_week_md,
                    )
                )

            result = await db.execute(query)
            return result.scalars().all()
    
    
    @staticmethod
    async def create_contact(db: AsyncSession, contact_data: ContactDto, user_id: UUID):
        new_contact = ContactModel(**contact_data.model_dump(exclude_none=True), user_id=user_id)
        db.add(new_contact)
        await db.commit()
        await db.refresh(new_contact)
        return new_contact
    
    @staticmethod
    async def get_contact_by_id(db: AsyncSession, contact_id: str, user_id: UUID):
        result = await db.execute(select(ContactModel).where(ContactModel.id == contact_id, ContactModel.user_id == user_id))
        contact = result.scalar_one_or_none()
        return contact
    
    @staticmethod
    async def remove_contact_by_id( db: AsyncSession, contact_id: str, user_id: UUID):
        result = await db.execute(select(ContactModel).where(ContactModel.id == contact_id, ContactModel.user_id == user_id))
        contact = result.scalar_one_or_none()
        if contact:
            await db.delete(contact)
            await db.commit()
            return True
        return False
    
    @staticmethod
    async def update_contact(db: AsyncSession, contact_id: str, user_id: UUID, contact_data: ContactDto):
        result = await db.execute(select(ContactModel).where(ContactModel.id == contact_id, ContactModel.user_id == user_id))
        contact = result.scalar_one_or_none()
        if not contact:
            return None
        
        for key, value in contact_data.model_dump(exclude_none=True).items():
            setattr(contact, key, value)
        
        await db.commit()
        await db.refresh(contact)
        return contact

def get_contacts_service() -> ContactsService:
    """Dependency for ContactsService"""
    return ContactsService()