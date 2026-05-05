from typing import Optional, Self

from pydantic import UUID7, ConfigDict
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import BaseEntity
from domain.validators import DescriptionStr


class Permission(BaseEntity):
    business_element_id: UUID7

    create_permission: bool = False
    read_permission: bool = False
    update_permission: bool = False
    delete_permission: bool = False

    read_own_permission: bool = False
    update_own_permission: bool = False
    delete_own_permission: bool = False

    description: Optional[DescriptionStr] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        business_element_id: UUID7,
        create_permission: bool = False,
        read_permission: bool = False,
        update_permission: bool = False,
        delete_permission: bool = False,
        read_own_permission: bool = False,
        update_own_permission: bool = False,
        delete_own_permission: bool = False,
        description: Optional[DescriptionStr] = None,
    ) -> Self:
        return cls(
            id=uuid7(),
            business_element_id=business_element_id,
            create_permission=create_permission,
            read_permission=read_permission,
            update_permission=update_permission,
            delete_permission=delete_permission,
            read_own_permission=read_own_permission,
            update_own_permission=update_own_permission,
            delete_own_permission=delete_own_permission,
            description=description,
        )
