
from logging import Logger
from logging import getLogger

from wx import DC

from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler

from umlshapes.types.Common import DESTINATION_CARDINALITY_IDX
from umlshapes.types.Common import SOURCE_CARDINALITY_IDX


class UmlAssociationEventHandler(UmlLinkEventHandler):

    def __init__(self, umlAssociation: 'UmlAssociation'):

        self.logger: Logger = getLogger(__name__)

        super().__init__(umlLink=umlAssociation)

    def OnMoveLink(self, dc: DC, moveControlPoints: bool = True):

        super().OnMoveLink(dc=dc, moveControlPoints=moveControlPoints)

        umlLink: UmlAssociation = self.GetShape()

        sourceCardinality:      UmlAssociationLabel = umlLink.sourceCardinality
        destinationCardinality: UmlAssociationLabel = umlLink.destinationCardinality

        if sourceCardinality is not None:
            srcCardX, srcCardY = umlLink.GetLabelPosition(SOURCE_CARDINALITY_IDX)
            sourceCardinality.position = self._computeRelativePosition(labelX=srcCardX, labelY=srcCardY, linkDelta=sourceCardinality.linkDelta)
        if destinationCardinality is not None:
            dstCardX, dstCardY = umlLink.GetLabelPosition(DESTINATION_CARDINALITY_IDX)
            destinationCardinality.position = self._computeRelativePosition(labelX=dstCardX, labelY=dstCardY, linkDelta=destinationCardinality.linkDelta)
