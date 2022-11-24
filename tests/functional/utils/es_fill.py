import json


def get_es_bulk_query(data, es_index) -> list[str]:
    bulk_query = []
    for row in data:
        bulk_query.extend([
            json.dumps({'index': {'_index': es_index, '_id': row['id']}}),
            json.dumps(row)
        ])
    return bulk_query
