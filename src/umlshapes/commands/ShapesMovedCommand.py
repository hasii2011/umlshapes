
from typing import TYPE_CHECKING
from datetime import datetime

from wx import ClientDC
from wx import Command

from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.frames.ShapeMoveInfo import FinalPositions
from umlshapes.frames.ShapeMoveInfo import InitialPositions

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.frames.ShapeMoveInfo import MovedShapes


class ShapesMovedCommand(Command):
    """
    A command to undo/redo the movement of one or more shapes.
    """

    def __init__(self, umlFrame: 'UmlFrame', movedShapes: 'MovedShapes', initialPositions: InitialPositions):
        """
        Args:
            umlFrame: The diagram frame where shapes are being moved.
            movedShapes: A dictionary mapping shape IDs to ShapeMovedInfo 
                         (which contains the shape and its original position).
        """
        from umlshapes.frames.ShapeMoveInfo import MovedShapes
        from umlshapes.frames.ShapeMoveInfo import ShapeId

        self._umlFrame:          UmlFrame         = umlFrame
        self._movedShapes:       MovedShapes      = movedShapes
        self._initialPositions:  InitialPositions = initialPositions
        self._finalPositions:    FinalPositions   = FinalPositions({})
        self._initialDoComplete: bool             = False

        # Naming logic similar to BaseCommand
        dt: datetime = datetime.now()
        self._name = f'Move-{dt.microsecond}'

        #
        # Command is not created until shapes are completely moved
        #
        for shapeId, info in self._movedShapes.items():
            self._finalPositions[shapeId] = info.umlShape.position

        super().__init__(canUndo=True, name=self._name)

    def GetName(self) -> str:
        return self._name

    def Do(self) -> bool:
        """
        The shapes have already been moved by the mouse interaction.
        This method is called when the command is submitted.
        However, Undo followed by redo will call this method again
        """
        if self._initialDoComplete is False:
            self._initialDoComplete = True
        else:
            self.Redo()

        return True

    def Undo(self) -> bool:
        """
        Restore shapes to their original positions.
        """
        dc: ClientDC = ClientDC(self._umlFrame)
        self._umlFrame.PrepareDC(dc)

        from umlshapes.frames.ShapeMoveInfo import ShapeMoveInfo
        from umlshapes.ShapeTypes import UmlShapeGenre

        for shapeId, umlPosition in self._initialPositions.items():
            shapeMoveInfo: ShapeMoveInfo = self._movedShapes[shapeId]
            umlShape: UmlShapeGenre = shapeMoveInfo.umlShape
            umlShape.position = umlPosition
            umlShape.MoveLinks(dc)
            
        self._umlFrame.Refresh()
        return True

    def Redo(self) -> bool:
        """
        Move shapes back to their final positions.
        """
        dc: ClientDC = ClientDC(self._umlFrame)
        self._umlFrame.PrepareDC(dc)

        for sid, finalPos in self._finalPositions.items():
            info = self._movedShapes[sid]
            umlShape: UmlShapeGenre = info.umlShape

            umlShape.position = finalPos
            umlShape.MoveLinks(dc)

        self._umlFrame.Refresh()
        return True
