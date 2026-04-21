from typing import Annotated

import nh3
from pydantic import BeforeValidator, SecretStr, StringConstraints


def sanitize_html(v: str) -> str:
    return nh3.clean(v, tags=set(), attributes={})


Sanitized = BeforeValidator(sanitize_html)

NameStr = Annotated[
    str, Sanitized, StringConstraints(min_length=1, max_length=50, strip_whitespace=True)
]
TitleStr = Annotated[
    str, Sanitized, StringConstraints(min_length=3, max_length=70, strip_whitespace=True)
]
NicknameStr = Annotated[
    str,
    StringConstraints(
        min_length=3, max_length=16, strip_whitespace=True, ascii_only=True
    ),
]
DescriptionStr = Annotated[str, StringConstraints(min_length=3, max_length=250)]
BioString = Annotated[
    str,
    Sanitized,
    StringConstraints(min_length=3, max_length=1000, strip_whitespace=True),
]
BodyString = Annotated[
    str,
    Sanitized,
    StringConstraints(min_length=3, max_length=2000, strip_whitespace=True),
]
PasswordStr = Annotated[SecretStr, StringConstraints(min_length=8, max_length=100)]
PermissionSlug = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-z0-9]+([.:][a-z0-9]+)*$", min_length=1, max_length=64
    ),
]
