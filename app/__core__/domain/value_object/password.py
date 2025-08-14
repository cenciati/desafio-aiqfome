from dataclasses import dataclass, field

from argon2 import PasswordHasher

from app.__core__.domain.exception.exception import ValidationError

ph = PasswordHasher()

PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH = 8, 32


@dataclass(frozen=True, slots=True, kw_only=True)
class Password:
    hash: str = field(compare=True, repr=False)

    @classmethod
    def _validate(cls, raw_password: str) -> None:
        if (
            not isinstance(raw_password, str)
            or len(raw_password) < PASSWORD_MIN_LENGTH
            or len(raw_password) > PASSWORD_MAX_LENGTH
        ):
            raise ValidationError(
                "password_must_be_a_string_between_{}_and_{}_characters".format(
                    PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH
                )
            )

    @classmethod
    def create(cls, raw_password: str) -> "Password":
        cls._validate(raw_password)
        return cls(hash=ph.hash(raw_password))

    def verify(self, raw_password: str) -> bool:
        try:
            return ph.verify(self.hash, raw_password)
        except Exception:
            return False
