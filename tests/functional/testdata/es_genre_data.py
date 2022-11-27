import json

from faker import Faker

from functional.utils.funcs import gen_id

fake = Faker()
Faker.seed(42)

# Названия криптовалют в качестве названий жанров - просто for fun
genres_data = [dict(id=gen_id(), name=fake.cryptocurrency_name()) for _ in range(13)]

with open("./testdata/es_index_id_name.json", "rt") as f:
    genres_index_body = json.load(f)
