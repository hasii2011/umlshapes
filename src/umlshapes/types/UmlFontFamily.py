
from enum import Enum


class UmlFontFamily(Enum):
    """
    How we specify fonts for UML Elements
    """
    SWISS    = 'Swiss'
    MODERN   = 'Modern'
    ROMAN    = 'Roman'
    SCRIPT   = 'Script'
    TELETYPE = 'Teletype'

    @classmethod
    def deSerialize(cls, value: str) -> 'UmlFontFamily':
        return UmlFontFamily(value)
