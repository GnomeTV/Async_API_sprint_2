import json
import uuid

with open("functional/testdata/es_index_movies.json", "rt") as f:
    films_index_body = json.load(f)


def get_id():
    return str(uuid.uuid4())


all_films_data = [{
    'id': get_id(),
    'imdb_rating': 8.5,
    'genre': [
        {'id': get_id(), 'name': 'Comedy'},
        {'id': get_id(), 'name': 'Fantasy'}
    ],
    'title': 'The Star',
    'description': 'New World',
    'director': ['Stan'],
    'actors_names': ['Ann', 'Bob'],
    'writers_names': ['Ben', 'Howard'],
    'actors': [
        {'id': get_id(), 'name': 'Ann'},
        {'id': get_id(), 'name': 'Bob'}
    ],
    'writers': [
        {'id': get_id(), 'name': 'Ben'},
        {'id': get_id(), 'name': 'Howard'}
    ],
    'directors': [
        {'id': get_id(), 'name': 'Stan'},
    ],
} for _ in range(60)]

film_by_id = [{
    'id': get_id(),
    'imdb_rating': 2.0,
    'genre': [
        {'id': get_id(), 'name': 'Comedy'},
    ],
    'title': 'Star wars',
    'description': 'Smth',
    'director': ['Stan'],
    'actors_names': ['Ann'],
    'writers_names': ['Ben'],
    'actors': [
        {'id': get_id(), 'name': 'Ann'},
    ],
    'writers': [
        {'id': get_id(), 'name': 'Ben'},
    ],
    'directors': [
        {'id': get_id(), 'name': 'Stan'},
    ],
}]

rating_test_data = [
    {
        'id': get_id(),
        'imdb_rating': 1.0,
        'genre': [
            {'id': get_id(), 'name': 'Comedy'},
        ],
        'title': 'Star wars',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': get_id(), 'name': 'Ann'},
        ],
        'writers': [
            {'id': get_id(), 'name': 'Ben'},
        ],
        'directors': [
            {'id': get_id(), 'name': 'Stan'},
        ],
    },
    {
        'id': get_id(),
        'imdb_rating': 8.0,
        'genre': [
            {'id': get_id(), 'name': 'Comedy'},
        ],
        'title': 'Star wars',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': get_id(), 'name': 'Ann'},
        ],
        'writers': [
            {'id': get_id(), 'name': 'Ben'},
        ],
        'directors': [
            {'id': get_id(), 'name': 'Stan'},
        ],
    }
]

search_star_data = [
    {
        'id': get_id(),
        'imdb_rating': 8.0,
        'genre': [
            {'id': get_id(), 'name': 'Comedy'},
        ],
        'title': 'Star wars',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': get_id(), 'name': 'Ann'},
        ],
        'writers': [
            {'id': get_id(), 'name': 'Ben'},
        ],
        'directors': [
            {'id': get_id(), 'name': 'Stan'},
        ],
    },
    {
        'id': get_id(),
        'imdb_rating': 9.0,
        'genre': [
            {'id': get_id(), 'name': 'Comedy'},
        ],
        'title': 'Test',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': get_id(), 'name': 'Ann'},
        ],
        'writers': [
            {'id': get_id(), 'name': 'Ben'},
        ],
        'directors': [
            {'id': get_id(), 'name': 'Stan'},
        ],
    },
    {
        'id': get_id(),
        'imdb_rating': 1.0,
        'genre': [
            {'id': get_id(), 'name': 'Comedy'},
        ],
        'title': 'Star wars 2',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': get_id(), 'name': 'Ann'},
        ],
        'writers': [
            {'id': get_id(), 'name': 'Ben'},
        ],
        'directors': [
            {'id': get_id(), 'name': 'Stan'},
        ],
    }
]

genre_id = get_id()
search_star_genre_data = [
    {
        'id': get_id(),
        'imdb_rating': 8.0,
        'genre': [
            {'id': genre_id, 'name': 'Comedy'},
        ],
        'title': 'Star wars',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': get_id(), 'name': 'Ann'},
        ],
        'writers': [
            {'id': get_id(), 'name': 'Ben'},
        ],
        'directors': [
            {'id': get_id(), 'name': 'Stan'},
        ],
    },
    {
        'id': get_id(),
        'imdb_rating': 9.0,
        'genre': [
            {'id': genre_id, 'name': 'Comedy'},
        ],
        'title': 'Star wars 3',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': get_id(), 'name': 'Ann'},
        ],
        'writers': [
            {'id': get_id(), 'name': 'Ben'},
        ],
        'directors': [
            {'id': get_id(), 'name': 'Stan'},
        ],
    },
    {
        'id': get_id(),
        'imdb_rating': 1.0,
        'genre': [
            {'id': get_id(), 'name': 'WTF'},
        ],
        'title': 'Star wars 2',
        'description': 'Smth',
        'director': ['Stan'],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': get_id(), 'name': 'Ann'},
        ],
        'writers': [
            {'id': get_id(), 'name': 'Ben'},
        ],
        'directors': [
            {'id': get_id(), 'name': 'Stan'},
        ],
    }
]
