import json

from functional.utils.funcs import gen_id

# Логика тестовых данных: два Джорджа (для нечёткого поиска)
# Три фильма: в первом George Lucas - режиссёр и сценарист, во втором - режиссёр
# в третьем фильме никого.

persons_data = [{"id": gen_id(), "name": "George Lucas"},
                {"id": gen_id(), "name": "George Michael"},
                {"id": gen_id(), "name": "Jackie Chan"},
                {"id": gen_id(), "name": "Al Pacino"},
                ]

pers_film_data = [
    {
        "id": gen_id(),
        "imdb_rating": 8.4,
        "genre": [
            {"id": gen_id(), "name": "Comedy"},
        ],
        "title": "Star wars 4",
        "description": "Smth",
        "director": [],
        "actors_names": [],
        "writers_names": [],
        "actors": [
            {"id": persons_data[2]["id"], "name": persons_data[2]["name"]},
        ],
        "writers": [
            {"id": persons_data[0]["id"], "name": persons_data[0]["name"]},
        ],
        "directors": [
            {"id": persons_data[0]["id"], "name": persons_data[0]["name"]},
        ],
    },
    {
        "id": gen_id(),
        "imdb_rating": 8.5,
        "genre": [
            {"id": gen_id(), "name": "Comedy"},
        ],
        "title": "Star wars 5",
        "description": "Smth",
        "director": [],
        "actors_names": [],
        "writers_names": [],
        "actors": [
            {"id": persons_data[3]["id"], "name": persons_data[2]["name"]},
        ],
        "writers": [
        ],
        "directors": [
            {"id": persons_data[0]["id"], "name": persons_data[0]["name"]},
        ],
    },
    {
        "id": gen_id(),
        "imdb_rating": 8.6,
        "genre": [
            {"id": gen_id(), "name": "Comedy"},
        ],
        "title": "Star wars 6",
        "description": "Smth",
        "director": [],
        "actors_names": [],
        "writers_names": [],
        "actors": [
        ],
        "writers": [
        ],
        "directors": [
        ],
    },
]

with open("functional/testdata/es_index_id_name.json", "rt") as f:
    persons_index_body = json.load(f)
