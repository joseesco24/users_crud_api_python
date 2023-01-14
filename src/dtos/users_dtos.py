# pylint: disable=unused-variable
__all__: list[str] = ["UserPubDto", "UserFullDto"]


class UserPubDto:
    internalId: str
    estatalId: str
    firstName: str
    lastName: str
    phoneNumber: int
    email: str
    gender: str
    birthday: str


class UserFullDto(UserPubDto):
    creation: str
    modification: str
    password: str
