
from typing import List
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import DC
from wx import OK

from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.dialogs.DlgEditLink import DlgEditLink
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.DeltaXY import DeltaXY
from umlshapes.links.LabelType import LabelType
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.eventhandlers.UmlBaseEventHandler import UmlBaseEventHandler

from umlshapes.types.Common import NAME_IDX

from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink
    from umlshapes.links.UmlAssociation import UmlAssociation

EditableLinkTypes: List[PyutLinkType] = [PyutLinkType.ASSOCIATION, PyutLinkType.AGGREGATION, PyutLinkType.COMPOSITION]


class UmlLinkEventHandler(UmlBaseEventHandler):
    """
    BTW, I hate local imports
    """

    def __init__(self, umlLink: 'UmlLink'):

        self.logger: Logger = getLogger(__name__)

        super().__init__(shape=umlLink)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlLink:  UmlAssociation = self.GetShape()
        pyutLink: PyutLink       = umlLink.pyutLink
        umlFrame: UmlFrame       = umlLink.GetCanvas()

        if self._isLinkEditable(linkType=pyutLink.linkType) is True:
            with DlgEditLink(parent=umlFrame, pyutLink=pyutLink) as dlg:
                if dlg.ShowModal() == OK:
                    umlFrame.refresh()
                    self.logger.info(f'{pyutLink=}')
                    self._updateAssociationLabels(umlLink=umlLink, pyutLink=dlg.value)

    def OnMoveLink(self, dc: DC, moveControlPoints: bool = True):

        super().OnMoveLink(dc=dc, moveControlPoints=moveControlPoints)

        umlLink: UmlAssociation = self.GetShape()
        associationName:        UmlAssociationLabel = umlLink.linkName
        #
        if associationName is not None and associationName.labelType == LabelType.ASSOCIATION_NAME:
            labelX, labelY = umlLink.GetLabelPosition(NAME_IDX)
            associationName.position = self._computeRelativePosition(labelX=labelX, labelY=labelY, linkDelta=associationName.linkDelta)

        self.GetShape().GetCanvas().refresh()

    def _computeRelativePosition(self, labelX: int, labelY: int, linkDelta: DeltaXY):

        newNamePosition: UmlPosition = UmlPosition(
            x=labelX - linkDelta.deltaX,
            y=labelY - linkDelta.deltaY
        )
        self.logger.debug(f'labelX,labelY=({labelX},{labelY})  deltaX,deltaY=({linkDelta.deltaX},{linkDelta.deltaY})')
        return newNamePosition

    def _updateAssociationLabels(self, umlLink: 'UmlAssociation', pyutLink: PyutLink):

        umlLink.sourceCardinality.label      = pyutLink.sourceCardinality
        umlLink.destinationCardinality.label = pyutLink.destinationCardinality
        umlLink.associationName.label        = pyutLink.name

    def _isLinkEditable(self, linkType: PyutLinkType) -> bool:
        """

        Args:
            linkType:

        Returns:  `True` if you are in the good-boy list, else `False`
        """
        answer: bool = False
        if linkType in EditableLinkTypes:
            answer = True
        return answer
