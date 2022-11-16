"""В модуле определяются большие запросы к Elastic."""

GET_PERSON_FILMS = """
{
    "query": {
        "bool": {
            "should":
                [{
                    "nested": {
                        "path": "actors",
                        "query": {
                            "term": {"actors.id": "%pers_id%"}
                        }
                    }
                 },
                 {
                    "nested": {
                        "path": "writers",
                        "query": {
                            "term": {"writers.id": "%pers_id%"}
                        }
                    }
                 },
                 {
                    "nested": {
                        "path": "directors",
                        "query": {
                            "term": {"directors.id": "%pers_id%"}
                        }
                    }
                 }
                ]
        }
    }
}
"""

PERSON_SEARCH_FUZZY = """
{
  "query": {
    "fuzzy": {
      "name": {
        "value": "%search_query%",
        "fuzziness": "AUTO"
      }
    }
  }
}
"""
