from pydantic import BaseModel, SecretStr, model_validator

from domain.dto import PatchUpdateUserInput
from domain.validators import PasswordStr


class ChangePasswordDTO(BaseModel):
    old_password: SecretStr
    password: PasswordStr
    password_repeat: SecretStr

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_repeat:
            raise ValueError("Passwords must match")
        if self.password == self.old_password:
            raise ValueError("The new password must not match the old one")
        return self


class UpdateUserDTO(PatchUpdateUserInput):
    pass
