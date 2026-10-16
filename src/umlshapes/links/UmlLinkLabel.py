
from typing import Optional
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.links.LabelType import LabelType
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.shapes.UmlBaseLabel import UmlBaseLabel
from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlDimensions import UmlDimensions

if TYPE_CHECKING:
    from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
    from umlshapes.links.UmlLink import UmlLink


class UmlLinkLabel(UmlBaseLabel):

    def __init__(self, label: str = '', size: Optional[UmlDimensions] = None, labelType: LabelType = LabelType.NOT_SET):
        """

        Args:
            label:
            size:
            labelType: Source or Destination Cardinality or association name
        """
        preferences: UmlPreferences = UmlPreferences()
        labelSize: UmlDimensions = size if size is not None else preferences.associationLabelSize

        super().__init__(
            label=label,
            size=labelSize,
            fontSize=preferences.associationTextFontSize,
            formatMode=preferences.associationLabelFormat
        )

        self.logger: Logger = getLogger(__name__)
        self._linkDelta: DeltaXY = DeltaXY()
        self._labelType: LabelType = labelType

    @property
    def umlFrame(self) -> 'ClassDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'ClassDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def parent(self) -> 'UmlLink':
        return self.GetParent()

    @parent.setter
    def parent(self, parent: 'UmlLink'):
        self.SetParent(parent)

    @property
    def linkDelta(self) -> DeltaXY:
        return self._linkDelta

    @linkDelta.setter
    def linkDelta(self, deltaXY: DeltaXY):
        self._linkDelta = deltaXY

    @property
    def labelType(self) -> LabelType:
        return self._labelType

    @labelType.setter
    def labelType(self, labelType: LabelType):
        self._labelType = labelType

    def coordinateToRelative(self, x: int, y: int):
        """
        Convert absolute coordinates to relative ones.
        Relative coordinates are coordinates relative to the origin of the
        shape.

        Args:
            x:
            y:

        Returns: Coordinates relative to the top left
        """
        from umlshapes.shapes.UmlClass import UmlClass

        if self.parent is not None:
            umlClass: UmlClass = cast(UmlClass, self.parent)  # noqa
            ox: int = umlClass.position.x
            oy: int = umlClass.position.y
            x -= ox
            y -= oy

        return x, y

    def __str__(self) -> str:
        return f'UmlLinkLabel - `{self.label}`'

    def __repr__(self) -> str:
        return f'UmlLinkLabel - `{self.label}` type={self.labelType}'

