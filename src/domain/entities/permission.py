from typing import Optional, Self

from pydantic import UUID7, ConfigDict
from uuid_extensions import uuid7  # type: ignore[import-untyped]

from domain.entities import BaseEntity
from domain.validators import DescriptionStr


class Permission(BaseEntity):
    business_element_id: UUID7

    read_permission: bool = False
    read_all_permission: bool = False
    create_permission: bool = False
    update_permission: bool = False
    update_all_permission: bool = False
    delete_permission: bool = False
    delete_all_permission: bool = False

    description: Optional[DescriptionStr] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        business_element_id: UUID7,
        read_permission: bool = False,
        read_all_permission: bool = False,
        create_permission: bool = False,
        update_permission: bool = False,
        update_all_permission: bool = False,
        delete_permission: bool = False,
        delete_all_permission: bool = False,
        description: Optional[DescriptionStr] = None,
    ) -> Self:
        return cls(
            id=uuid7(),
            business_element_id=business_element_id,
            read_permission=read_permission,
            read_all_permission=read_all_permission,
            create_permission=create_permission,
            update_permission=update_permission,
            update_all_permission=update_all_permission,
            delete_permission=delete_permission,
            delete_all_permission=delete_all_permission,
            description=description,
        )
