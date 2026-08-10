import uuid

def generate_uuid() -> str:
    """Generate a unique string identifier.
    """
    return str(uuid.uuid4())
