from typing import cast

from logging import Logger
from logging import getLogger

from umlmodel.SDMessage import SDMessage

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.sd.eventhandlers.UmlSDLifeLineEventHandler import LifeLineClickDetails
from umlshapes.sd.eventhandlers.UmlSDMessageEventHandler import UmlSDMessageEventHandler

from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.sd.SDMessageType import SDMessageType
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
        return self._enableMessageCreation

    @enableMessageCreation.setter
    def enableMessageCreation(self, enable: bool):
        """
        Set to False, in order to stop the message creation workflow
        Args:
            enable: If True the 2-step message creation workflow is enabled

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
        clickedY:      int = self._startDetails.clickPosition.y
        snappedY:      int = self._layoutEngine.computeNearestSlotY(headerBottomY=headerBottomY, targetY=clickedY)

        startX: float = startLifeLine.GetX()
        endX:   float = destLifeLine.GetX()

        modelMessage: SDMessage = SDMessage(
            message=f'demoMessage-{self._messageCount:04d}',
            src=startLifeLine.umlInstanceName.sdInstance,
            sourceY=snappedY,
            dst=destLifeLine.umlInstanceName.sdInstance,
            destinationY=snappedY,
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

        umlSDMessage.fromY = snappedY
        umlSDMessage.toY   = snappedY
        umlSDMessage.SetEnds(
            x1=startX,
            y1=snappedY,
            x2=endX,
            y2=snappedY
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
