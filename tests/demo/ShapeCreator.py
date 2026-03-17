
from logging import Logger
from logging import getLogger

from umlshapes.commands.CreateUmlActorCommand import CreateUmlActorCommand
from umlshapes.commands.CreateUmlClassCommand import CreateUmlClassCommand
from umlshapes.commands.CreateUmlNoteCommand import CreateUmlNoteCommand
from umlshapes.commands.CreateUmlTextCommand import CreateUmlTextCommand
from umlshapes.commands.CreateUmlUseCaseCommand import CreateUmlUseCaseCommand

from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlPosition import UmlPosition

from tests.demo.DemoCommon import INITIAL_X
from tests.demo.DemoCommon import INITIAL_Y


class ShapeCreator:

    def __init__(self, umlPubSubEngine: UmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        self._umlPubSubEngine: UmlPubSubEngine = umlPubSubEngine
        self._preferences:     UmlPreferences  = UmlPreferences()
        self._currentPosition: UmlPosition     = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

    def displayUndoableUmlClass(self, diagramFrame: ClassDiagramFrame):

        umlPosition: UmlPosition = self._computePosition()

        cmd: CreateUmlClassCommand = CreateUmlClassCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )
        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create class submission status: {submitStatus}')

    def displayUndoableUmlNote(self, diagramFrame: ClassDiagramFrame):

        umlPosition: UmlPosition = self._computePosition()

        cmd: CreateUmlNoteCommand = CreateUmlNoteCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )

        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create note submission status: {submitStatus}')

    def displayUndoableUmlText(self, diagramFrame: ClassDiagramFrame):

        umlPosition: UmlPosition = self._computePosition()

        cmd: CreateUmlTextCommand = CreateUmlTextCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )

        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create text submission status: {submitStatus}')

    def displayUndoableUmlActor(self, diagramFrame: UseCaseDiagramFrame):
        umlPosition: UmlPosition = self._computePosition()

        cmd: CreateUmlActorCommand = CreateUmlActorCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )

        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create actor submission status: {submitStatus}')

    def displayUndoableUmlUseCase(self, diagramFrame: UseCaseDiagramFrame):
        umlPosition: UmlPosition = self._computePosition()

        cmd: CreateUmlUseCaseCommand = CreateUmlUseCaseCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )

        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create use case submission status: {submitStatus}')

    def _computePosition(self) -> UmlPosition:
        """
        TODO: Put in an option to compute position or just put at a fixed
        place.  For UI testing we want fixed

        Returns:

        """

        currentPosition: UmlPosition = UmlPosition(x=self._currentPosition.x, y=self._currentPosition.y)

        # self._currentPosition.x += INCREMENT_X
        # self._currentPosition.y += INCREMENT_Y

        return currentPosition
