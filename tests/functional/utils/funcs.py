from uuid import uuid4


def gen_id() -> str:
    """Generated UUID and returns as string."""
    return str(uuid4())
