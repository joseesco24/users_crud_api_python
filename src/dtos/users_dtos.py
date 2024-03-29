# !/usr/bin/python3
# type: ignore

__all__: list[str] = ["UserDto"]


class UserDto:
    internalId: str
    estatalId: str
    firstName: str
    lastName: str
    phoneNumber: int
    email: str
    gender: str
    birthday: str
