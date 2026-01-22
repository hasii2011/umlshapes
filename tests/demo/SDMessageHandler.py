
from logging import Logger
from logging import getLogger
from typing import cast

from umlmodel.SDMessage import SDMessage

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.shapes.sd.UmlSDLifeLineEventHandler import LifeLineClickDetails
from umlshapes.shapes.sd.UmlSDMessage import UmlSDMessage

NO_START_DETAILS = cast(LifeLineClickDetails, None)


class SDMessageHandler:
    def __init__(self, sequenceDiagramFrame: SequenceDiagramFrame, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            sequenceDiagramFrame:  The sequence diagram frame we are handling
            umlPubSubEngine:       The pub sub engine where we can respond to message and send messages

        """
        self.logger: Logger = getLogger(__name__)

        self._sequenceDiagramFrame: SequenceDiagramFrame = sequenceDiagramFrame
        self._umlPubSubEngine:      IUmlPubSubEngine     = umlPubSubEngine

        self._umlPubSubEngine.subscribe(
            UmlMessageType.SD_LIFE_LINE_CLICKED,
            frameId=sequenceDiagramFrame.id,
            listener=self._lifeLineClicked
        )

        self._startDetails:              LifeLineClickDetails = NO_START_DETAILS
        self._messageCreationInProgress: bool                 = False

    @property
    def sequenceDiagramFrame(self) -> SequenceDiagramFrame:
        """

        Returns:  The sequence diagram frame we are currently handling

        """
        return self._sequenceDiagramFrame

    @sequenceDiagramFrame.setter
    def sequenceDiagramFrame(self, sequenceDiagramFrame: SequenceDiagramFrame):
        self._sequenceDiagramFrame = sequenceDiagramFrame

    def reset(self):
        self._startDetails = NO_START_DETAILS
        self._messageCreationInProgress = False

    def _lifeLineClicked(self, clickDetails: LifeLineClickDetails):
        """

        Args:
            clickDetails:
        """

        if self._messageCreationInProgress is True:
            self._hookThemUp(endDetails=clickDetails)
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

        modelMessage: SDMessage    = SDMessage(
            message='demoMessage',
            src=self._startDetails.lifeLine.umlInstanceName.sdInstance,
            sourceY=self._startDetails.clickPosition.y,
            dst=endDetails.lifeLine.umlInstanceName.sdInstance,
            destinationY=endDetails.clickPosition.y,

        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(sdMessage=modelMessage)
        umlSDMessage.MakeLineControlPoints(n=2)

        self._startDetails.lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=endDetails.lifeLine)

        umlSDMessage.SetEnds(
            x1=self._startDetails.clickPosition.x,
            y1=self._startDetails.clickPosition.y,
            x2=endDetails.clickPosition.x,
            y2=endDetails.clickPosition.y
        )
        umlSDMessage.Show(True)
        self._sequenceDiagramFrame.umlDiagram.AddShape(umlSDMessage)
        self._sequenceDiagramFrame.refresh()
