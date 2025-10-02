from enum import Enum


class UserRole(str, Enum):
    OBSERVER = "observer"
    VOTER = "voter"

    @classmethod
    def choices(cls):
        return [(member.value, member.value.capitalize()) for member in cls]
