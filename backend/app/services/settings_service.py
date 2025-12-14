"""Settings service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.repositories.settings_repository import SettingsRepository
from app.schemas.settings import (
    SettingOut, PaymentCardInfo, PaymentCardInfoOut, PaymentCardUpdate
)
from app.models.settings import SettingKeys
from app.utils.logger import log_event


class SettingsService:
    """Service layer for settings business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = SettingsRepository(db)
    
    async def get_payment_card(self) -> Optional[PaymentCardInfoOut]:
        """Get payment card information."""
        card_number = await self.repository.get(SettingKeys.PAYMENT_CARD_NUMBER)
        card_holder = await self.repository.get(SettingKeys.PAYMENT_CARD_HOLDER)
        
        if not card_number or not card_holder:
            return None
        
        return PaymentCardInfoOut(
            card_number=card_number.value,
            card_holder=card_holder.value,
            updated_at=card_number.updated_at,
        )
    
    async def set_payment_card(
        self, 
        card_info: PaymentCardInfo, 
        admin_id: UUID
    ) -> PaymentCardInfoOut:
        """Set payment card information (admin only)."""
        await self.repository.set(
            SettingKeys.PAYMENT_CARD_NUMBER,
            card_info.card_number,
            admin_id
        )
        await self.repository.set(
            SettingKeys.PAYMENT_CARD_HOLDER,
            card_info.card_holder,
            admin_id
        )
        
        log_event(
            event_type="settings.payment_card_updated",
            admin_id=str(admin_id),
            card_number_masked=f"****{card_info.card_number[-4:]}",
        )
        
        return PaymentCardInfoOut(
            card_number=card_info.card_number,
            card_holder=card_info.card_holder,
        )
    
    async def update_payment_card(
        self,
        update_data: PaymentCardUpdate,
        admin_id: UUID
    ) -> Optional[PaymentCardInfoOut]:
        """Update payment card information partially."""
        if update_data.card_number:
            await self.repository.set(
                SettingKeys.PAYMENT_CARD_NUMBER,
                update_data.card_number,
                admin_id
            )
        
        if update_data.card_holder:
            await self.repository.set(
                SettingKeys.PAYMENT_CARD_HOLDER,
                update_data.card_holder,
                admin_id
            )
        
        log_event(
            event_type="settings.payment_card_updated",
            admin_id=str(admin_id),
        )
        
        return await self.get_payment_card()
    
    async def get_setting(self, key: str) -> Optional[SettingOut]:
        """Get a setting by key."""
        setting = await self.repository.get(key)
        if setting:
            return SettingOut.model_validate(setting)
        return None
    
    async def set_setting(
        self, 
        key: str, 
        value: str, 
        admin_id: UUID
    ) -> SettingOut:
        """Set a setting value."""
        setting = await self.repository.set(key, value, admin_id)
        return SettingOut.model_validate(setting)

