# pylint: disable=unused-variable
__all__: list[str] = ["UserPublicDto", "UserFullDto"]


class UserPublicDto:
    internalId: str
    estatalId: str
    firstName: str
    lastName: str
    phoneNumber: int
    email: str
    gender: str
    birthday: str


class UserFullDto(UserPublicDto):
    creation: str
    modification: str
    password: str
