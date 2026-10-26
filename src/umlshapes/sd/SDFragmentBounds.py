
from dataclasses import dataclass


@dataclass
class SDFragmentBounds:
    """
    Geometric bounds for a sequence diagram combined fragment.

    Follows wxOGL Shape conventions where the location is defined
    by center coordinates (centerX, centerY) alongside dimensions (width, height).
    """

    centerX: int
    centerY: int
    width:   int
    height:  int

    @property
    def left(self) -> int:
        """
        Left edge X coordinate.
        """
        return self.centerX - (self.width // 2)

    @property
    def right(self) -> int:
        """
        Right edge X coordinate.
        """
        return self.centerX + (self.width // 2)

    @property
    def top(self) -> int:
        """
        Top edge Y coordinate.
        """
        return self.centerY - (self.height // 2)

    @property
    def bottom(self) -> int:
        """
        Bottom edge Y coordinate.
        """
        return self.centerY + (self.height // 2)
