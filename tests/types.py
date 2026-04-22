from typing import Awaitable, Callable

from httpx import AsyncClient

from domain.entities.role import Role


AuthClientFactory = Callable[[str, str], Awaitable[AsyncClient]]
UserFactory = Callable[[str, str, str], Awaitable[dict[str, str]]]
RoleDict = dict[str, Role]
