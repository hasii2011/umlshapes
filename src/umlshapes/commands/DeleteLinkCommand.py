
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from datetime import datetime

from wx import Command

from umlmodel.Link import Link

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

if TYPE_CHECKING:
    from umlshapes.ShapeTypes import UmlLinkGenre
    from umlshapes.ShapeTypes import UmlShapeGenre


class DeleteLinkCommand(Command):

    def __init__(self, partialName: str, umlLink: 'UmlLinkGenre', umlPubSubEngine: IUmlPubSubEngine):

        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.frames.UmlFrame import UmlFrame

        self.logger: Logger = getLogger(__name__)

        self._name:            str              = f'{partialName}-{self.timeStamp}'      # Because Command.GetName() does not really work
        #
        # Only use this for deletion;  Will be re-created on Undo
        self._umlLink:         UmlLinkGenre     = umlLink
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        # So we can recreate the Link
        self._modelLink: Link = umlLink.modelLink
        #
        # Save the ends for Undo
        #
        self._sourceUmlShape:      UmlShapeGenre = umlLink.sourceShape
        self._destinationUmlShape: UmlShapeGenre = umlLink.destinationShape
        self._umlFrame:            UmlFrame      = umlLink.umlFrame

        super().__init__(canUndo=True, name=self._name)

    @property
    def timeStamp(self) -> int:

        dt = datetime.now()

        return dt.microsecond

    def Do(self) -> bool:
        from umlshapes.links.UmlAssociation import UmlAssociation
        from umlshapes.UmlDiagram import UmlDiagram

        if isinstance(self._umlLink, UmlAssociation):
            umlAssociation: UmlAssociation = self._umlLink
            umlDiagram:     UmlDiagram     = self._umlFrame.umlDiagram

            umlDiagram.RemoveShape(umlAssociation.associationName)
            umlDiagram.RemoveShape(umlAssociation.sourceCardinality)
            umlDiagram.RemoveShape(umlAssociation.destinationCardinality)

        self._umlLink.selected = False  # To remove handles
        self._umlLink.Delete()

        self._umlFrame.refresh()

        return True

    def Undo(self) -> bool:
        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.links.UmlAssociation import UmlAssociation
        from umlshapes.links.eventhandlers.UmlAssociationEventHandler import UmlAssociationEventHandler

        sourceUmlShape:      UmlClass = cast(UmlClass, self._sourceUmlShape)
        destinationUmlShape: UmlClass = cast(UmlClass, self._destinationUmlShape)

        #
        # HAVE TO HANDLE ALL THE OTHER LINKS,  INTERFACE, INHERITANCE, NOTE LINK
        #
        umlAssociation: UmlAssociation = UmlAssociation(link=self._modelLink)
        umlAssociation.umlFrame        = self._umlFrame
        umlAssociation.umlPubSubEngine = self._umlPubSubEngine
        umlAssociation.MakeLineControlPoints(n=2)       # Make this configurable

        associationEventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlAssociation)

        associationEventHandler.umlPubSubEngine = self._umlPubSubEngine
        associationEventHandler.SetPreviousHandler(umlAssociation.GetEventHandler())
        umlAssociation.SetEventHandler(associationEventHandler)

        sourceUmlShape.addLink(umlLink=umlAssociation, destinationClass=destinationUmlShape)

        self._umlFrame.umlDiagram.AddShape(umlAssociation)
        umlAssociation.Show(True)

        # RECREATED !!!
        self._umlLink = umlAssociation

        return True

    def GetName(self) -> str:
        return self._name

    def CanUndo(self):
        return True


"""
        umlAssociation.umlFrame = diagramFrame
        umlAssociation.umlPubSubEngine = self._umlPubSubEngine
        umlAssociation.MakeLineControlPoints(n=2)       # Make this configurable

        sourceUmlClass.addLink(umlLink=umlAssociation, destinationClass=destinationUmlClass)

        diagramFrame.umlDiagram.AddShape(umlAssociation)
        umlAssociation.Show(True)

        eventHandler: UmlAssociationEventHandler = UmlAssociationEventHandler(umlAssociation=umlAssociation)

        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlAssociation.GetEventHandler())
        umlAssociation.SetEventHandler(eventHandler)

"""
