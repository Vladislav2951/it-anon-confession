from typing import Annotated

from pydantic import Field, SecretStr


NameStr = Annotated[str, Field(min_length=1, max_length=50, strip_whitespace=True)]
PasswordStr = Annotated[SecretStr, Field(min_length=8, max_length=100, ascii_only=True)]
