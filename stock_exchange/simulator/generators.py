from uuid import uuid4


def generate_key() -> str:
    generated_id = uuid4().hex
    return generated_id
