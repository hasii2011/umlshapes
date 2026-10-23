
from typing import Optional
from typing import cast

from logging import Logger
from logging import getLogger

from umlmodel.SDMessage import SDMessage

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.sd.eventhandlers.UmlSDLifeLineEventHandler import LifeLineClickDetails
from umlshapes.sd.eventhandlers.UmlSDMessageEventHandler import UmlSDMessageEventHandler

from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.sd.SDMessageType import SDMessageType
from umlshapes.sd.UmlSDExecution import UmlSDExecution
from umlshapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.sd.UmlSDMessage import UmlSDMessage

NO_START_DETAILS: LifeLineClickDetails = cast(LifeLineClickDetails, None)   # noqa


class SDMessageCreationHandler:
    def __init__(self, sequenceDiagramFrame: SequenceDiagramFrame, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            sequenceDiagramFrame:  The sequence diagram frame we are handling
            umlPubSubEngine:       The pub sub engine where we can respond to message and send messages

        """
        self.logger: Logger = getLogger(__name__)

        self._sequenceDiagramFrame: SequenceDiagramFrame = sequenceDiagramFrame
        self._umlPubSubEngine:      IUmlPubSubEngine     = umlPubSubEngine
        self._layoutEngine:         SDLayoutEngine       = SDLayoutEngine()
        self._preferences:          UmlPreferences       = UmlPreferences()

        self._umlPubSubEngine.subscribe(
            UmlMessageType.SD_LIFELINE_CLICKED,
            frameId=sequenceDiagramFrame.id,
            listener=self._lifeLineClicked
        )

        self._startDetails: LifeLineClickDetails = NO_START_DETAILS

        self._messageCreationInProgress: bool          = False
        self._enableMessageCreation:     bool          = False
        self._messageType:               SDMessageType = SDMessageType.SYNCHRONOUS

        self._messageCount: int = 0     # temp until I get possible message names in

    @property
    def messageType(self) -> SDMessageType:
        return self._messageType

    @messageType.setter
    def messageType(self, messageType: SDMessageType):
        self._messageType = messageType

    @property
    def sequenceDiagramFrame(self) -> SequenceDiagramFrame:
        """

        Returns:  The sequence diagram frame we are currently handling

        """
        return self._sequenceDiagramFrame

    @sequenceDiagramFrame.setter
    def sequenceDiagramFrame(self, sequenceDiagramFrame: SequenceDiagramFrame):
        self._sequenceDiagramFrame = sequenceDiagramFrame

    @property
    def enableMessageCreation(self) -> bool:
        """
        Controls the interactive two-step message creation workflow for sequence diagrams.

        When enabled (True):
            Activates interactive message creation mode and prompts the user to select
            the source lifeline, followed by the destination lifeline, creating a message
            between them.

        When disabled (False):
            Cancels any in-progress creation workflow and ignores subsequent lifeline clicks.

        Returns:
            True if interactive message creation mode is active, False otherwise.
        """
        return self._enableMessageCreation

    @enableMessageCreation.setter
    def enableMessageCreation(self, enable: bool):
        """
        Enable or disable interactive message creation mode.

        Setting to True prompts the user to click the source lifeline.
        Setting to False stops and resets any in-progress message creation workflow.

        Args:
            enable: If True, activates the 2-step message creation workflow; if False, cancels it.
        """
        self._enableMessageCreation = enable
        if enable:
            self._umlPubSubEngine.sendMessage(
                UmlMessageType.UPDATE_APPLICATION_STATUS,
                frameId=self._sequenceDiagramFrame.id,
                message='Click on source lifeline'
            )
        else:
            self._reset()

    def _lifeLineClicked(self, clickDetails: LifeLineClickDetails):
        """

        Args:
            clickDetails:
        """
        if self._enableMessageCreation:
            if self._messageCreationInProgress:
                self._hookThemUp(endDetails=clickDetails)
                self._messageCreationInProgress = False
            else:
                self.logger.info(f'\n{clickDetails=}')
                self._startDetails = clickDetails
                self._messageCreationInProgress = True
                self._umlPubSubEngine.sendMessage(
                    UmlMessageType.UPDATE_APPLICATION_STATUS,
                    frameId=self._sequenceDiagramFrame.id,
                    message='Click on destination lifeline'
                )

    def _hookThemUp(self, endDetails: LifeLineClickDetails):
        """
        Place the message link between the two instances
        Args:
            endDetails:

        """
        self.logger.info(f'\n{endDetails=}')

        startLifeLine: UmlSDLifeLine = self._startDetails.lifeLine
        destLifeLine:  UmlSDLifeLine = endDetails.lifeLine

        headerBottomY: int = startLifeLine.rectangle.top
        clickedFromY:  int = self._startDetails.clickPosition.y
        clickedToY:    int = endDetails.clickPosition.y

        isReflexiveMessage: bool = (startLifeLine == destLifeLine)
        rawFromTimeStepIndex: int = self._layoutEngine.computeNearestTimeStepIndex(headerBottomY=headerBottomY, targetY=clickedFromY)

        fromTimeStepIndex: int = max(0, rawFromTimeStepIndex)
        toTimeStepIndex:   int
        if isReflexiveMessage:
            rawToTimeStepIndex: int = self._layoutEngine.computeNearestTimeStepIndex(headerBottomY=headerBottomY, targetY=clickedToY)
            if rawToTimeStepIndex <= fromTimeStepIndex:
                toTimeStepIndex = fromTimeStepIndex + 1
            else:
                toTimeStepIndex = rawToTimeStepIndex
        else:
            toTimeStepIndex = fromTimeStepIndex

        snappedFromY: int = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=fromTimeStepIndex)
        snappedToY:   int = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=toTimeStepIndex)

        maxRequiredY: int = max(snappedFromY, snappedToY)
        if self._preferences.autoGrowLifeLines:

            neededLifelineHeight: int = (maxRequiredY - headerBottomY) + self._layoutEngine.parameters.bottomPadding
            currentStartHeight:   int = startLifeLine.size.height
            currentDestHeight:    int = destLifeLine.size.height

            if (neededLifelineHeight > currentStartHeight) or (neededLifelineHeight > currentDestHeight):
                if self._preferences.uniformLifeLineLength:
                    self._sequenceDiagramFrame.setAllLifeLinesLength(neededLifelineHeight)
                else:
                    startSDInstance: UmlSDInstance | None = startLifeLine.umlSDInstance
                    if startSDInstance is not None:
                        startSDInstance.setLifeLineLength(neededLifelineHeight)

                    if not isReflexiveMessage:
                        destSDInstance: UmlSDInstance | None = destLifeLine.umlSDInstance
                        if destSDInstance is not None:
                            destSDInstance.setLifeLineLength(neededLifelineHeight)
        else:
            maxTimeStepIndex: int = max(
                0,
                (startLifeLine.size.height - self._layoutEngine.parameters.topPadding - self._layoutEngine.parameters.bottomPadding)
                // self._layoutEngine.parameters.timeStepHeight
            )
            if isReflexiveMessage:
                fromTimeStepIndex = max(0, min(fromTimeStepIndex, max(0, maxTimeStepIndex - 1)))
                toTimeStepIndex   = max(fromTimeStepIndex + 1, min(toTimeStepIndex, maxTimeStepIndex))
            else:
                fromTimeStepIndex = max(0, min(fromTimeStepIndex, maxTimeStepIndex))
                toTimeStepIndex   = fromTimeStepIndex

            snappedFromY = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=fromTimeStepIndex)
            snappedToY   = self._layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=toTimeStepIndex)

        startX: float = startLifeLine.GetX()
        endX:   float = destLifeLine.GetX()

        modelMessage: SDMessage = SDMessage(
            message=f'demoMessage-{self._messageCount:04d}',
            src=startLifeLine.umlInstanceName.sdInstance,
            sourceY=snappedFromY,
            dst=destLifeLine.umlInstanceName.sdInstance,
            destinationY=snappedToY,
        )
        self._messageCount += 1
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            messageType=self._messageType
        )
        umlSDMessage.umlFrame = self._sequenceDiagramFrame
        self.logger.info(f'Created message: {umlSDMessage.sdMessage.message}')

        startLifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=destLifeLine)

        umlSDMessage.fromY = snappedFromY
        umlSDMessage.toY   = snappedToY

        if self._preferences.autoGenerateExecutions:
            executionDuration: int
            if isReflexiveMessage:
                executionDuration = snappedToY - snappedFromY
            else:
                executionDuration = self._preferences.timeStepHeight

            execution: UmlSDExecution = UmlSDExecution(
                lifeLine=destLifeLine,
                startY=snappedFromY,
                endY=snappedFromY + executionDuration
            )
            destLifeLine.addExecution(execution=execution)
            umlSDMessage.execution = execution

        fromExecution: Optional[UmlSDExecution] = startLifeLine.getExecutionAtY(y=snappedFromY)
        toExecution:   Optional[UmlSDExecution] = destLifeLine.getExecutionAtY(y=snappedToY)

        if isReflexiveMessage:
            if fromExecution is not None:
                startX = fromExecution.GetX() + (fromExecution.GetWidth() / 2.0)
            umlSDMessage.setReflexiveMessagePoints(
                lifeLineX=round(startX),
                fromY=snappedFromY,
                toY=snappedToY
            )
        else:
            if startLifeLine.GetX() < destLifeLine.GetX():
                if fromExecution is not None:
                    startX = fromExecution.GetX() + (fromExecution.GetWidth() / 2.0)
                if toExecution is not None:
                    endX = toExecution.GetX() - (toExecution.GetWidth() / 2.0)
            else:
                if fromExecution is not None:
                    startX = fromExecution.GetX() - (fromExecution.GetWidth() / 2.0)
                if toExecution is not None:
                    endX = toExecution.GetX() + (toExecution.GetWidth() / 2.0)

            umlSDMessage.SetEnds(
                x1=startX,
                y1=snappedFromY,
                x2=endX,
                y2=snappedToY
            )

        umlSDMessage.Show(True)
        self._sequenceDiagramFrame.umlDiagram.AddShape(umlSDMessage)
        self._sequenceDiagramFrame.refresh()

        self._reset()

        eventHandler: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=umlSDMessage,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=umlSDMessage.GetEventHandler()
        )
        umlSDMessage.SetEventHandler(eventHandler)

        self._sequenceDiagramFrame.moveShapeToFront(umlSDMessage)

    def _reset(self):
        self._startDetails = NO_START_DETAILS
        self._messageCreationInProgress = False
        self._umlPubSubEngine.sendMessage(
            UmlMessageType.UPDATE_APPLICATION_STATUS,
            frameId=self._sequenceDiagramFrame.id,
            message=''
        )
