from pydantic import BaseModel, EmailStr, SecretStr, model_validator

from domain.dto import LoginInput, RegisterInput


class LoginDTO(LoginInput):
    pass


class RegisterDTO(RegisterInput):
    password_repeat: SecretStr

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_repeat:
            raise ValueError("Passwords must match")
        return self
