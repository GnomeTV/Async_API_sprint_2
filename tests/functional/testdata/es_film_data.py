import json
import uuid
from datetime import datetime

with open("/home/ivan/Desktop/practicum/Async_API_sprint_2/tests/functional/testdata/es_index_movies.json", "rt") as f:
    films_index_body = json.load(f)

all_films_data = [{
    'id': str(uuid.uuid4()),
    'imdb_rating': 8.5,
    'genre': [
        {'id': str(uuid.uuid4()), 'name': 'Comedy'},
        {'id': str(uuid.uuid4()), 'name': 'Fantasy'}
    ],
    'title': 'The Star',
    'description': 'New World',
    'director': ['Stan'],
    'actors_names': ['Ann', 'Bob'],
    'writers_names': ['Ben', 'Howard'],
    'actors': [
        {'id': str(uuid.uuid4()), 'name': 'Ann'},
        {'id': str(uuid.uuid4()), 'name': 'Bob'}
    ],
    'writers': [
        {'id': str(uuid.uuid4()), 'name': 'Ben'},
        {'id': str(uuid.uuid4()), 'name': 'Howard'}
    ],
    'directors': [
        {'id': str(uuid.uuid4()), 'name': 'Stan'},
    ],
} for _ in range(60)]

film_by_id = [{
    'id': str(uuid.uuid4()),
    'imdb_rating': 2.0,
    'genre': [
        {'id': str(uuid.uuid4()), 'name': 'Comedy'},
    ],
    'title': 'Star wars',
    'description': 'Smth',
    'director': ['Stan'],
    'actors_names': ['Ann'],
    'writers_names': ['Ben'],
    'actors': [
        {'id': str(uuid.uuid4()), 'name': 'Ann'},
    ],
    'writers': [
        {'id': str(uuid.uuid4()), 'name': 'Ben'},
    ],
    'directors': [
        {'id': str(uuid.uuid4()), 'name': 'Stan'},
    ],
}]

rating_test_data = [
    {
        'id': str(uuid.uuid4()),
        'imdb_rating': 2.0,
        'genre': [
            {'id': str(uuid.uuid4()), 'name': 'Comedy'},
        ],
        'title': 'Star wars',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': str(uuid.uuid4()), 'name': 'Ann'},
        ],
        'writers': [
            {'id': str(uuid.uuid4()), 'name': 'Ben'},
        ],
        'directors': [
            {'id': str(uuid.uuid4()), 'name': 'Stan'},
        ],
    },
    {
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.0,
        'genre': [
            {'id': str(uuid.uuid4()), 'name': 'Comedy'},
        ],
        'title': 'Star wars',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': str(uuid.uuid4()), 'name': 'Ann'},
        ],
        'writers': [
            {'id': str(uuid.uuid4()), 'name': 'Ben'},
        ],
        'directors': [
            {'id': str(uuid.uuid4()), 'name': 'Stan'},
        ],
    }
]


