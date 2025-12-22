
from typing import List
from typing import NewType
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import DC
from wx import EVT_MENU
from wx import Menu
from wx import MenuItem
from wx import OK

from wx import CommandEvent
from wx import Point

from wx import NewIdRef as wxNewIdRef

from umlshapes.lib.ogl import LineShape

from umlmodel.Link import Link
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.UmlUtils import UmlUtils
from umlshapes.dialogs.DlgEditLink import DlgEditLink
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.LabelType import LabelType
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.Common import NAME_IDX
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions

if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink
    from umlshapes.links.UmlAssociation import UmlAssociation

EditableLinkTypes: List[LinkType] = [LinkType.ASSOCIATION, LinkType.AGGREGATION, LinkType.COMPOSITION]

MENU_ADD_BEND_ID:      int = wxNewIdRef()
MENU_REMOVE_BEND_ID:   int = wxNewIdRef()
MENU_TOGGLE_SPLINE_ID: int = wxNewIdRef()
MENU_STRAIGHTEN_ID:    int = wxNewIdRef()

LineControlPoints = NewType('LineControlPoints', List[Point])

MINIMUM_CP_TO_ALLOW_BEND:       int = 2
MINIMUM_CP_TO_ALLOW_STRAIGHTEN: int = 3     # Stole this from the straighten code; Is this good?


class UmlLinkEventHandler(UmlBaseEventHandler):
    """
    BTW, I hate local imports
    """

    def __init__(self, umlLink: 'UmlLink', previousEventHandler: ShapeEvtHandler):
        """

        Args:
            umlLink:   The link handled by this event handler
            previousEventHandler:
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(shape=umlLink, previousEventHandler=previousEventHandler)

        self._contextMenu:    Menu           = self._createContextMenu()

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """

        Args:
            x:
            y:
            keys:
            attachment:
        """

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlLink:  UmlAssociation = self.GetShape()
        link:     Link           = umlLink.modelLink
        umlFrame: UmlFrame       = umlLink.GetCanvas()

        if self._isLinkEditable(linkType=link.linkType):

            with DlgEditLink(parent=umlFrame, link=link) as dlg:
                if dlg.ShowModal() == OK:
                    umlFrame.refresh()
                    self.logger.info(f'{link=}')
                    self._updateAssociationLabels(umlLink=umlLink, modelLink=dlg.value)

    def OnRightClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """

        Args:
            x:
            y:
            keys:
            attachment:
        """
        # TODO:  May have to revisit this later
        # super().OnRightClick(x=x, y=y, keys=keys, attachment=attachment)

        line:    LineShape   = self.GetShape()
        cPoints: List[Point] = line.GetLineControlPoints()

        bendItem: MenuItem = self._contextMenu.FindItemById(MENU_REMOVE_BEND_ID)
        if len(cPoints) > MINIMUM_CP_TO_ALLOW_BEND:
            bendItem.Enable(enable=True)
        else:
            bendItem.Enable(enable=False)

        straightenItem: MenuItem = self._contextMenu.FindItemById(MENU_STRAIGHTEN_ID)
        if len(cPoints) < MINIMUM_CP_TO_ALLOW_STRAIGHTEN:
            straightenItem.Enable(enable=False)
        else:
            straightenItem.Enable(enable=True)

        self._contextMenu.Unbind(EVT_MENU)
        clickPosition: UmlPosition = UmlPosition(x=x, y=y)
        # I hate lambdas -- Humberto
        self._contextMenu.Bind(EVT_MENU, lambda evt, data=clickPosition: self._onMenuItemSelected(evt, clickPosition))

        frame: UmlFrame = self._getFrame()
        frame.PopupMenu(self._contextMenu, x, y)

    def OnMoveLink(self, dc: DC, moveControlPoints: bool = True):
        """

        Args:
            dc:
            moveControlPoints:
        """
        super().OnMoveLink(dc=dc, moveControlPoints=moveControlPoints)

        umlLink: UmlAssociation = self.GetShape()
        associationName:        UmlAssociationLabel = umlLink.linkName
        #
        if associationName is not None and associationName.labelType == LabelType.ASSOCIATION_NAME:
            labelX, labelY = umlLink.GetLabelPosition(NAME_IDX)
            associationName.position = self._computeRelativePosition(labelX=labelX, labelY=labelY, linkDelta=associationName.linkDelta)

        self.GetShape().GetCanvas().refresh()

    def _createContextMenu(self) -> Menu:

        menu: Menu = Menu()
        menu.Append(MENU_ADD_BEND_ID,      'Add Bend',      'Add Bend at right click point')
        menu.Append(MENU_REMOVE_BEND_ID,   'Remove Bend',   'Remove Bend closest to click point')
        menu.Append(MENU_TOGGLE_SPLINE_ID, 'Toggle Spline', 'Best with at least one bend')
        menu.Append(MENU_STRAIGHTEN_ID,    'Straighten',    'Wonder what this does')

        return menu

    def _onMenuItemSelected(self, event: CommandEvent, clickPoint: UmlPosition):

        eventId:           int         = event.GetId()
        umlLink:           UmlLink     = self.GetShape()

        if eventId == MENU_ADD_BEND_ID:
            self._addBend(clickPoint=clickPoint)
        elif eventId == MENU_REMOVE_BEND_ID:

            lineControlPoints: LineControlPoints = umlLink.GetLineControlPoints()
            self.logger.debug(f'{clickPoint=} {lineControlPoints}')
            self._removeBend(umlLink=umlLink, clickPoint=clickPoint, lineControlPoints=lineControlPoints)

        elif eventId == MENU_TOGGLE_SPLINE_ID:
            self._toggleSpline()
        elif eventId == MENU_STRAIGHTEN_ID:
            link: UmlLink = self.GetShape()
            link.Straighten()
            link.umlFrame.refresh()
            self._indicateFrameModified()

    def _computeRelativePosition(self, labelX: int, labelY: int, linkDelta: DeltaXY):

        newNamePosition: UmlPosition = UmlPosition(
            x=labelX - linkDelta.deltaX,
            y=labelY - linkDelta.deltaY
        )
        self.logger.debug(f'labelX,labelY=({labelX},{labelY})  deltaX,deltaY=({linkDelta.deltaX},{linkDelta.deltaY})')
        return newNamePosition

    def _updateAssociationLabels(self, umlLink: 'UmlAssociation', modelLink: Link):

        umlLink.sourceCardinality.label      = modelLink.sourceCardinality
        umlLink.destinationCardinality.label = modelLink.destinationCardinality
        umlLink.associationName.label        = modelLink.name

    def _isLinkEditable(self, linkType: LinkType) -> bool:
        """

        Args:
            linkType:

        Returns:  `True` if you are in the good-boy list, else `False`
        """
        answer: bool = False
        if linkType in EditableLinkTypes:
            answer = True
        return answer

    def _removeBend(self, umlLink: 'UmlLink', clickPoint: UmlPosition, lineControlPoints: LineControlPoints):
        """
        Removes the bend closet to the clickPoint
        Will not remove the end points;
        Args:
            umlLink:            The link we are working on
            clickPoint:         Where the developer clicked
            lineControlPoints:  The link line control points (bends)
        """
        searchPoints: List[Point] = self._createSearchPoints(umlLink, lineControlPoints)

        closestBend: UmlPosition = UmlUtils.closestPoint(referencePosition=clickPoint, umlPositions=self._toUmlPositions(searchPoints))
        self.logger.debug(f'{closestBend=}')

        frame: UmlFrame = self.GetShape().GetCanvas()

        for lineControlPoint in lineControlPoints:

            self.logger.debug(f'{lineControlPoint=}')
            if closestBend.x == lineControlPoint.x and closestBend.y == lineControlPoint.y:
                lineControlPoints.remove(Point(closestBend.x, closestBend.y))
                break

        umlLink.selected = False
        frame.Refresh()
        self._indicateFrameModified()

    def _addBend(self, clickPoint: UmlPosition):
        """

        Args:
            clickPoint:   Where to put the bend in
        """

        self.logger.debug(f'Add a bend.  {clickPoint=}')

        umlLink: UmlLink = self.GetShape()
        umlLink.addLineControlPoint(umlPosition=UmlPosition(x=clickPoint.x, y=clickPoint.y))

        frame: UmlFrame = self.GetShape().GetCanvas()
        frame.Refresh()
        self._indicateFrameModified()

    def _toggleSpline(self):

        line: UmlLink = self.GetShape()

        # line.SetSpline(not line.IsSpline())
        line.toggleSpline()

        frame: UmlFrame = self._getFrame()
        frame.Refresh()
        self._indicateFrameModified()

    def _indicateFrameModified(self):
        frame: UmlFrame = self._getFrame()
        assert self._umlPubSubEngine is not None, 'Developer error;  Remember to inject the UML PubSub Engine'
        self._umlPubSubEngine.sendMessage(UmlMessageType.FRAME_MODIFIED, frameId=frame.id, modifiedFrameId=frame.id)

    def _getFrame(self) -> UmlFrame:

        umlLink:  UmlLink  = self.GetShape()
        umlFrame: UmlFrame = umlLink.GetCanvas()

        return umlFrame

    def _toUmlPositions(self, wxPoints: List[Point]) -> UmlPositions:

        positions: UmlPositions = UmlPositions([])

        for pt in wxPoints:
            position: UmlPosition = UmlPosition(x=pt.x, y=pt.y)
            positions.append(position)

        return positions

    def _createSearchPoints(self, umlLink: 'UmlLink', lineControlPoints: LineControlPoints) -> LineControlPoints:
        """
        Do not consider the end points

        Args:
            umlLink:
            lineControlPoints:

        Returns:  The control points less the 2 end points
        """

        searchPoints: LineControlPoints = LineControlPoints(lineControlPoints[:])

        x1, y1, x2, y2 = umlLink.FindLineEndPoints()

        pt1: Point = Point(x1, y1)
        pt2: Point = Point(x2, y2)

        searchPoints.remove(pt1)
        searchPoints.remove(pt2)

        return searchPoints
