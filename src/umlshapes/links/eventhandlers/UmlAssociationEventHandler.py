
from logging import Logger
from logging import getLogger

from wx import DC


from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
from umlshapes.links.eventhandlers.UmlLinkEventHandler import UmlLinkEventHandler
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.Common import DESTINATION_CARDINALITY_IDX
from umlshapes.types.Common import SOURCE_CARDINALITY_IDX


class UmlAssociationEventHandler(UmlLinkEventHandler):

    def __init__(self, umlAssociation: 'UmlAssociation', umlPubSubEngine: IUmlPubSubEngine):
        """
        Associations all have this event handler as the additional event handler;  So.
        do the SetPreviousEventhandler, SetEventHandler dipsy do

        Args:
            umlAssociation:
            umlPubSubEngine:
        """

        self.logger: Logger = getLogger(__name__)

        super().__init__(umlLink=umlAssociation, previousEventHandler=umlAssociation.GetEventHandler())
        #
        # These two must come after the call the to parent constructor
        #
        umlAssociation.SetEventHandler(self)
        self._umlPubSubEngine = umlPubSubEngine

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
