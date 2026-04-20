from typing import Annotated

from pydantic import SecretStr, StringConstraints


NameStr = Annotated[
    str, StringConstraints(min_length=1, max_length=50, strip_whitespace=True)
]
NicknameStr = Annotated[
    str, StringConstraints(min_length=3, max_length=16, strip_whitespace=True)
]
BioString = Annotated[
    str, StringConstraints(min_length=3, max_length=1000, strip_whitespace=True)
]
PasswordStr = Annotated[SecretStr, StringConstraints(min_length=8, max_length=100)]
PermissionSlug = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-z0-9]+([.:][a-z0-9]+)*$", min_length=1, max_length=64
    ),
]
