
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import cast

from wx import Point

from umlshapes.ShapeTypes import MoveableUmlShape
from umlshapes.commands.shapemove.ShapeMoveInfo import LinkId
from umlshapes.commands.shapemove.ShapeMoveInfo import LinkMoveInfo
from umlshapes.commands.shapemove.ShapeMoveInfo import MovedLinks
from umlshapes.commands.shapemove.ShapeMoveInfo import MovedShapes
from umlshapes.commands.shapemove.ShapeMoveInfo import ShapeId
from umlshapes.commands.shapemove.ShapeMoveInfo import ShapeMoveInfo
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions

if TYPE_CHECKING:
    from umlshapes.ShapeTypes import UmlShapes
    from umlshapes.links.UmlLink import UmlLink


class ShapeMoveRecorder:
    """
    Consolidates the recording of initial and final positions for moved diagram
    shapes and intermediate bend points and endpoints on attached links.
    """

    @classmethod
    def recordInitialShapePositions(
        cls,
        umlShapes:   'UmlShapes',
        masterShape: Optional[MoveableUmlShape] = None
    ) -> MovedShapes:
        """
        Record initial positions for the given shapes prior to moving.

        Args:
            umlShapes:   The collection of selected or targeted shapes before moving.
            masterShape: Optional primary dragged shape to include even if not in umlShapes.

        Returns:
            MovedShapes populated with each shape and its original position.
        """
        from umlshapes.links.UmlLink import UmlLink
        from umlshapes.mixins.TopLeftMixin import TopLeftMixin
        from umlshapes.sd.UmlSDExecution import UmlSDExecution
        from umlshapes.sd.UmlSDMessage import UmlSDMessage
        from umlshapes.shapes.UmlBaseLabel import UmlBaseLabel

        movedShapes: MovedShapes = MovedShapes({})

        candidateShapes: List[object] = list(umlShapes)
        if masterShape is not None and masterShape not in candidateShapes:
            candidateShapes.append(masterShape)

        for candidate in candidateShapes:
            if isinstance(candidate, UmlSDMessage):
                shapeId: ShapeId = ShapeId(candidate.id)
                if shapeId not in movedShapes:
                    movedShapes[shapeId] = ShapeMoveInfo(
                        umlShape=candidate,
                        originalPosition=candidate.position
                    )
            elif isinstance(candidate, TopLeftMixin) and not isinstance(candidate, (UmlLink, UmlBaseLabel, UmlSDExecution)):
                umlShape: MoveableUmlShape = cast(MoveableUmlShape, candidate)
                shapeId = ShapeId(umlShape.id)
                if shapeId not in movedShapes:
                    movedShapes[shapeId] = ShapeMoveInfo(
                        umlShape=umlShape,
                        originalPosition=umlShape.position
                    )

        return movedShapes

    @classmethod
    def recordInitialLinkPositions(
        cls,
        umlShapes:   'UmlShapes',
        masterShape: Optional[MoveableUmlShape] = None
    ) -> MovedLinks:
        """
        Record initial intermediate bend positions and endpoint positions for all
        links in or attached to the given shapes prior to moving.

        Args:
            umlShapes:   The collection of selected or targeted shapes/links before moving.
            masterShape: Optional primary dragged shape whose attached links should also be included.

        Returns:
            MovedLinks populated with each link and its original intermediate bend and end positions.
        """
        from umlshapes.links.UmlLink import UmlLink
        from umlshapes.mixins.TopLeftMixin import TopLeftMixin
        from umlshapes.sd.UmlSDExecution import UmlSDExecution
        from umlshapes.shapes.UmlBaseLabel import UmlBaseLabel

        movedLinks: MovedLinks = MovedLinks({})

        candidateShapes: List[object] = list(umlShapes)
        if masterShape is not None and masterShape not in candidateShapes:
            candidateShapes.append(masterShape)

        for candidate in candidateShapes:
            if isinstance(candidate, UmlLink):
                cls._addLinkToMovedLinks(umlLink=candidate, movedLinks=movedLinks)
            elif isinstance(candidate, TopLeftMixin) and not isinstance(candidate, (UmlBaseLabel, UmlSDExecution)):
                umlShape: MoveableUmlShape = cast(MoveableUmlShape, candidate)
                for attachedLine in umlShape.GetLines():
                    if isinstance(attachedLine, UmlLink):
                        cls._addLinkToMovedLinks(umlLink=attachedLine, movedLinks=movedLinks)

        return movedLinks

    @classmethod
    def recordFinalShapePositions(cls, movedShapes: MovedShapes):
        """
        Snapshot final positions for all tracked moved shapes after movement is complete.

        Args:
            movedShapes: Dictionary of tracked moved shapes to update with finalPosition.
        """
        for shapeMoveInfo in movedShapes.values():
            umlShape: MoveableUmlShape = shapeMoveInfo.umlShape
            shapeMoveInfo.finalPosition = umlShape.position

    @classmethod
    def recordFinalLinkPositions(cls, movedLinks: MovedLinks):
        """
        Snapshot final intermediate bend positions and endpoint positions for all
        tracked links after movement is complete.

        Args:
            movedLinks: Dictionary of tracked moved links to update with finalBendPositions and finalEndPositions.
        """
        for linkMoveInfo in movedLinks.values():
            linkMoveInfo.finalBendPositions = cls.extractBendPositions(
                umlLink=linkMoveInfo.umlLink
            )
            linkMoveInfo.finalEndPositions = linkMoveInfo.umlLink.endPositions

    @classmethod
    def extractBendPositions(cls, umlLink: 'UmlLink') -> UmlPositions:
        """
        Extract the intermediate bend points (excluding source and destination endpoints)
        from a UmlLink as a list of UmlPosition instances.

        Args:
            umlLink: The link whose intermediate bend points are to be extracted.

        Returns:
            UmlPositions containing the intermediate bend points in order.
        """
        bendPositions: UmlPositions = UmlPositions([])
        lineControlPoints: Optional[List[Point]] = umlLink.GetLineControlPoints()
        if lineControlPoints is not None and len(lineControlPoints) > 2:
            for point in lineControlPoints[1:-1]:
                bendPositions.append(UmlPosition(x=round(point.x), y=round(point.y)))

        return bendPositions

    @classmethod
    def _addLinkToMovedLinks(cls, umlLink: 'UmlLink', movedLinks: MovedLinks):
        """
        Add a link and its initial intermediate bend and end points to movedLinks if not already present.

        Args:
            umlLink:    The link we snapshot.
            movedLinks: Dictionary of tracked moved links.
        """
        linkId: LinkId = LinkId(umlLink.id)
        if linkId not in movedLinks:
            movedLinks[linkId] = LinkMoveInfo(
                umlLink=umlLink,
                originalBendPositions=cls.extractBendPositions(umlLink=umlLink),
                originalEndPositions=umlLink.endPositions
            )
