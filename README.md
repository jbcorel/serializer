"""
Техническое Задание. Пример.

Есть JSON:
"  
    {
        "phone_number": 12347,
        "name": "Max",
        "age": 23,
        "height": 180.5,
        "hobbies": ["hockey", "music", "touch_grass"],
        "favorite_game": {
            "name": "Hollow knight",
            "genre": "Metroidvania",
            "developer": "Team Cherry"
        }
    } 
"


Есть модели:

class Game:
    name: str,
    genre: str, 
    developer: str


class ExpectedInput:
    phone_number: PhoneNumber[Russia]
    name: str,
    age: int
    height: 180.5,
    hobbies: list[str],
    favorite_game: Game


пример того, как должно работать:

try:
    validated = ExpectedInput.from_json(json)
except ValidationFailed as e:
    print(e)
"""