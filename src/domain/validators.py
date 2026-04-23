"""
Модуль валидаторов данных.

Использует Annotated и Pydantic для декларативной проверки строк,
а также библиотеку nh3 для очистки строк от нежелательного HTML-кода (XSS protection).
"""

from typing import Annotated

import nh3
from pydantic import BeforeValidator, SecretStr, StringConstraints


def sanitize_html(v: str) -> str:
    return nh3.clean(v, tags=set(), attributes={})


Sanitized = BeforeValidator(sanitize_html)

NameStr = Annotated[
    str, Sanitized, StringConstraints(min_length=1, max_length=64, strip_whitespace=True)
]
TitleStr = Annotated[
    str, Sanitized, StringConstraints(min_length=3, max_length=70, strip_whitespace=True)
]
NicknameStr = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=16,
        strip_whitespace=True,
        ascii_only=True,
        pattern=r"^[a-zA-Z0-9_-]+$",
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
