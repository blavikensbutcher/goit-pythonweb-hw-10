from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.contacts import ContactModel
from src.types.contract import ContactDto


class ContactsService:
    @staticmethod
    async def get_contacts(db: AsyncSession):
        result = await db.execute(select(ContactModel))
        contacts = result.scalars().all()
        return contacts
    
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