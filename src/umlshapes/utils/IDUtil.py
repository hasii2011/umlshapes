
from human_id import generate_id


class IDUtil:
    """
    Isolates ID generation
    """

    @classmethod
    def getID(cls) -> str:
        return generate_id()
