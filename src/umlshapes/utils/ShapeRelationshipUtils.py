from umlshapes.links.LollipopInflator import LollipopInflator

from umlshapes.types.Common import Rectangle
from umlshapes.types.Common import AttachmentSide
from umlshapes.types.Common import LollipopCoordinates

from umlshapes.types.UmlPosition import UmlPosition


class ShapeRelationshipUtils:

    @classmethod
    def lollipopHitTest(cls, x: int, y: int, attachmentSide: AttachmentSide, lollipopCoordinates: LollipopCoordinates) -> bool:
        """
        This located here for testability

        Args:
            x:
            y:
            attachmentSide:
            lollipopCoordinates:

        Returns:
        """
        ans: bool = False

        rectangle: Rectangle = LollipopInflator.inflateLollipop(
            attachmentSide=attachmentSide,
            lollipopCoordinates=lollipopCoordinates
        )

        left:   int = rectangle.left
        right:  int = rectangle.right
        top:    int = rectangle.top
        bottom: int = rectangle.bottom

        # noinspection PyChainedComparisons
        if x >= left and x <= right and y >= top and y <= bottom:
            ans = True

        return ans

    @classmethod
    def attachmentSide(cls, x, y, rectangle: Rectangle) -> AttachmentSide:

        if y == rectangle.top:
            return AttachmentSide.TOP
        if y == rectangle.bottom:
            return AttachmentSide.BOTTOM
        if x == rectangle.left:
            return AttachmentSide.LEFT
        if x == rectangle.right:
            return AttachmentSide.RIGHT

        assert False, 'Only works for points on the perimeter'

    @classmethod
    def isVerticalSide(cls, side: AttachmentSide) -> bool:
        """

        Args:
            side:

        Returns: 'True' if the side is vertical axis, else it returns 'False'
        """
        return side == AttachmentSide.LEFT or side == AttachmentSide.RIGHT

    @classmethod
    def computeLineCentum(cls, attachmentSide: AttachmentSide, umlPosition: UmlPosition, rectangle: Rectangle) -> float:
        """
        Computes a value between 0.1 and 0.9.  That value is the relative location of the input position
        Args:
            attachmentSide:
            umlPosition:  The xy position on the perimeter of the input rectangle
            rectangle:

        Returns:  A value 0.1 and 0.9
        """
        distance: float = 0.1
        if ShapeRelationshipUtils.isVerticalSide(side=attachmentSide):
            height:         int = rectangle.bottom - rectangle.top
            relativeHeight: int = umlPosition.y - rectangle.top
            distance = relativeHeight / height
        elif attachmentSide == AttachmentSide.TOP or attachmentSide == AttachmentSide.BOTTOM:
            width:         int = rectangle.right - rectangle.left
            relativeWidth: int = umlPosition.x - rectangle.left
            distance = relativeWidth / width

        distance = round(distance, 1)
        if distance < 0.1:
            distance = 0.1
        elif distance > 0.9:
            distance = 0.9

        return distance
