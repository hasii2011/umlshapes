
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from datetime import datetime

from wx import ClientDC
from wx import Command
from wx import Point

from umlshapes.ShapeTypes import MoveableUmlShape
from umlshapes.commands.shapemove.ShapeMoveInfo import MovedLinks
from umlshapes.commands.shapemove.ShapeMoveInfo import MovedShapes
from umlshapes.commands.shapemove.ShapeMoveRecorder import ShapeMoveRecorder
from umlshapes.types.Common import EndPositions
from umlshapes.types.UmlPosition import UmlPositions

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.links.UmlLink import UmlLink

DEFAULT_NAME_PREFIX: str = 'ShapeMove'


class ShapesMovedCommand(Command):
    """
    A command to undo/redo the movement of one or more shapes and any intermediate
    control points (bends) and endpoints on their attached links.
    """

    def __init__(self,
                 umlFrame:    'UmlFrame',
                 movedShapes: MovedShapes,
                 movedLinks:  MovedLinks,
                 name:        str = DEFAULT_NAME_PREFIX
                 ):
        """
        Args:
            umlFrame:    The diagram frame where shapes are being moved.
            movedShapes: A dictionary mapping shape IDs to ShapeMoveInfo
                         (containing the shape and its original and final positions).
            movedLinks:  A dictionary mapping link IDs to LinkMoveInfo
                         (containing the link and its original and final intermediate bend and end points).
            name:        An alternate name for the command to override default.
        """
        self.logger: Logger = getLogger(__name__)

        self._umlFrame:          UmlFrame    = umlFrame
        self._movedShapes:       MovedShapes = movedShapes
        self._movedLinks:        MovedLinks  = movedLinks
        self._initialDoComplete: bool        = False

        dt:         datetime = datetime.now()
        self._name: str      = f'{name}-{dt.microsecond}'

        ShapeMoveRecorder.recordFinalShapePositions(movedShapes=self._movedShapes)
        ShapeMoveRecorder.recordFinalLinkPositions(movedLinks=self._movedLinks)

        super().__init__(canUndo=True, name=self._name)

    @property
    def commandName(self) -> str:
        return self._name

    @commandName.setter
    def commandName(self, commandName: str):
        self._name = commandName

    def GetName(self) -> str:
        """
        Override to make sure to use MY NAME

        Returns:
            The command name.
        """
        return self._name

    def Do(self) -> bool:
        """
        The shapes have already been moved by mouse or programmatic interaction.
        This method is called when the command is submitted.
        However, Undo followed by redo will call this method again.
        """
        if not self._initialDoComplete:
            self._initialDoComplete = True
            self.logger.info(f'Do - {self._name}')
        else:
            self.Redo()

        return True

    def Undo(self) -> bool:
        """
        Restore shapes to their original positions and restore link intermediate bend and end points.
        """
        self.logger.info(f'Undo - {self._name}')

        dc: ClientDC = ClientDC(self._umlFrame)
        self._umlFrame.PrepareDC(dc)

        for linkMoveInfo in self._movedLinks.values():
            self._applyLinkBendPositions(
                umlLink=linkMoveInfo.umlLink,
                bendPositions=linkMoveInfo.originalBendPositions
            )

        for shapeMoveInfo in self._movedShapes.values():
            umlShape: MoveableUmlShape = shapeMoveInfo.umlShape
            umlShape.position = shapeMoveInfo.originalPosition
            umlShape.MoveLinks(dc)

        for linkMoveInfo in self._movedLinks.values():
            self._finalizeLinkState(
                dc=dc,
                umlLink=linkMoveInfo.umlLink,
                bendPositions=linkMoveInfo.originalBendPositions,
                endPositions=linkMoveInfo.originalEndPositions
            )

        self._umlFrame.refresh()
        return True

    def Redo(self) -> bool:
        """
        Move shapes back to their final positions and reapply final link intermediate bend and end points.
        """
        self.logger.info(f'Redo - {self._name}')

        dc: ClientDC = ClientDC(self._umlFrame)
        self._umlFrame.PrepareDC(dc)

        for linkMoveInfo in self._movedLinks.values():
            self._applyLinkBendPositions(
                umlLink=linkMoveInfo.umlLink,
                bendPositions=linkMoveInfo.finalBendPositions
            )

        for shapeMoveInfo in self._movedShapes.values():
            umlShape: MoveableUmlShape = shapeMoveInfo.umlShape
            umlShape.position = shapeMoveInfo.finalPosition
            umlShape.MoveLinks(dc)

        for linkMoveInfo in self._movedLinks.values():
            self._finalizeLinkState(
                dc=dc,
                umlLink=linkMoveInfo.umlLink,
                bendPositions=linkMoveInfo.finalBendPositions,
                endPositions=linkMoveInfo.finalEndPositions
            )

        self._umlFrame.refresh()
        return True

    def _applyLinkBendPositions(self, umlLink: 'UmlLink', bendPositions: UmlPositions):
        """
        Replace the intermediate bend points on umlLink while preserving its two endpoints.

        Args:
            umlLink:       The link to update.
            bendPositions: The intermediate bend positions to install.
        """
        umlLink.DeleteControlPoints()
        lineControlPoints: Optional[List[Point]] = umlLink.GetLineControlPoints()

        if lineControlPoints is not None and len(lineControlPoints) >= 2:

            firstPoint: Point = lineControlPoints[0]
            lastPoint:  Point = lineControlPoints[-1]

            lineControlPoints.clear()
            lineControlPoints.append(firstPoint)
            if bendPositions is not None:
                for bendPosition in bendPositions:
                    lineControlPoints.append(Point(bendPosition.x, bendPosition.y))
            lineControlPoints.append(lastPoint)

            if bendPositions is not None and len(bendPositions) > 0:
                umlLink._initialised = True
            else:
                umlLink._initialised = False

    def _finalizeLinkState(
        self,
        dc:            ClientDC,
        umlLink:       'UmlLink',
        bendPositions: UmlPositions,
        endPositions:  EndPositions
    ):
        """
        Update link endpoints, restore exact saved endpoint coordinates, recreate
        draggable control point handles if needed, and reposition association labels.

        Args:
            dc:            Prepared client device context.
            umlLink:       The link being finalized.
            bendPositions: The active intermediate bend positions on the link.
            endPositions:  The exact saved source and destination endpoint positions.
        """
        from umlshapes.links.UmlAssociation import UmlAssociation

        umlLink.GetEventHandler().OnMoveLink(dc, moveControlPoints=False)
        if endPositions is not None:
            umlLink.endPositions = endPositions
        if (bendPositions is not None and len(bendPositions) > 0) or umlLink.Selected() is True:
            umlLink.MakeControlPoints()
        if isinstance(umlLink, UmlAssociation):
            umlLink.smartPlaceLabels()
