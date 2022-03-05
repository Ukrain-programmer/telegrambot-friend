from dataclasses import dataclass

from typing import List


@dataclass
class UsersDto:
    id: int
    firstname: str
    lastname: str
    username: str
    additionalinfo: str
    isBlock: bool



class Mapper:
    def mapToUserDto(users):
        result = []
        for user in users:
            result.append(UsersDto(*user))
        return result

    def mapToList(elements: List[tuple]) -> list:
        result = []
        for elm in elements:
            result.append(elm[0])
        return result