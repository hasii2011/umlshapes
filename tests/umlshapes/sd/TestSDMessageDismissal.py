
from typing import Optional

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain
from unittest.mock import MagicMock
from unittest.mock import patch

from wx import CommandEvent
from wx import EVT_TEXT_ENTER
from wx import ID_CANCEL
from wx import ID_OK
from wx import Window

from wx.lib.sized_controls import SizedDialog

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.SDInstance import SDInstance
from umlmodel.SDMessage import SDMessage

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog
from umlshapes.dialogs.DlgEditSDMessage import DlgEditSDMessage
from umlshapes.dialogs.DlgEditSDMessage import Message
from umlshapes.dialogs.DlgEditSDMessage import MessageList
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
from wx.lib.ogl import OGLInitialize
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.sd.SDMessageType import SDMessageType
from umlshapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.sd.UmlSDMessage import UmlSDMessage
from umlshapes.sd.eventhandlers.UmlSDMessageEventHandler import UmlSDMessageEventHandler

TEST_INSTANCE_NAME: str = 'testInstance'
INITIAL_FROM_Y:     int = 100
INITIAL_TO_Y:       int = 140
INSTANCE_DEFAULT_X: int = 100
INSTANCE_DEFAULT_Y: int = 50


class TestSDMessageDismissal(UnitTestBaseW):
    """
    Unit tests for DlgEditSDMessage dismissal behavior and UmlSDMessageEventHandler capture release.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()

        self._umlPubSubEngine: IUmlPubSubEngine     = UmlPubSubEngine()
        self._diagramFrame:    SequenceDiagramFrame = SequenceDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._umlSDInstance: UmlSDInstance = self._createTestInstance()
        self._lifeLine:      UmlSDLifeLine = self._umlSDInstance.umlSDLifeLine

    def tearDown(self):
        if self._diagramFrame.HasCapture():
            self._diagramFrame.ReleaseMouse()
        self._diagramFrame.Destroy()
        super().tearDown()

    def testBaseEditDialogEscapeIdAndReturnCodes(self):
        """
        Verify that BaseEditDialog configures EscapeId to ID_CANCEL and ends modal with ID_OK and ID_CANCEL.
        """
        with BaseEditDialog(parent=self._listeningWindow, title='TestBaseDlg') as baseDlg:
            baseDlg._layoutStandardOkCancelButtonSizer()
            self.assertEqual(baseDlg.GetEscapeId(), ID_CANCEL)

            with patch.object(baseDlg, 'EndModal') as mockEndModal:
                dummyEvent: CommandEvent = CommandEvent()
                baseDlg._onOk(dummyEvent)
                mockEndModal.assert_called_once_with(ID_OK)

            with patch.object(baseDlg, 'EndModal') as mockEndModal:
                dummyEvent = CommandEvent()
                baseDlg._onClose(dummyEvent)
                mockEndModal.assert_called_once_with(ID_CANCEL)

    def testBaseEditDialogShowModalReleasesParentCapture(self):
        """
        Verify that BaseEditDialog.ShowModal releases parent mouse capture before entering modal loop.
        """
        with BaseEditDialog(parent=self._listeningWindow, title='TestBaseDlg') as baseDlg:
            with patch.object(self._listeningWindow, 'HasCapture', return_value=True):
                with patch.object(self._listeningWindow, 'ReleaseMouse') as mockReleaseMouse:
                    with patch.object(SizedDialog, 'ShowModal', return_value=ID_OK):
                        returnCode: int = baseDlg.ShowModal()
                        self.assertEqual(returnCode, ID_OK)
                        mockReleaseMouse.assert_called_once()

    def testDlgEditSDMessageDefaultButton(self):
        """
        Verify that DlgEditSDMessage configures OK button as the default dialog item.
        """
        modelMessage: SDMessage = SDMessage(message='testMessage')
        messages:     MessageList = MessageList([Message('msg1'), Message('msg2')])

        with DlgEditSDMessage(parent=self._listeningWindow, sdMessage=modelMessage, messages=messages) as dlg:
            okBtn: Optional[Window] = dlg.FindWindow(ID_OK)
            self.assertIsNotNone(okBtn)
            self.assertIs(dlg.GetDefaultItem(), okBtn)

    def testDlgEditSDMessageEvtTextEnterEndsModal(self):
        """
        Verify that EvtTextEnter ends the modal dialog with ID_OK.
        """
        modelMessage: SDMessage = SDMessage(message='testMessage')
        messages:     MessageList = MessageList([Message('msg1')])

        with DlgEditSDMessage(parent=self._listeningWindow, sdMessage=modelMessage, messages=messages) as dlg:
            evt: CommandEvent = CommandEvent(EVT_TEXT_ENTER.typeId, dlg._cb.GetId())
            evt.SetString('enteredText')

            with patch.object(dlg, 'EndModal') as mockEndModal:
                dlg.EvtTextEnter(evt)
                mockEndModal.assert_called_once_with(ID_OK)

    def testUmlBaseEventHandlerOnLeftDoubleClickReleasesCapture(self):
        """
        Verify that UmlBaseEventHandler.OnLeftDoubleClick releases canvas mouse capture.
        """
        umlSDMessage: UmlSDMessage             = self._createReflexiveMessage(lifeLine=self._lifeLine)
        eventHandler: UmlSDMessageEventHandler = self._attachEventHandler(umlSDMessage=umlSDMessage)

        with patch.object(self._diagramFrame, 'HasCapture', return_value=True):
            with patch.object(self._diagramFrame, 'ReleaseMouse') as mockReleaseMouse:
                super(UmlSDMessageEventHandler, eventHandler).OnLeftDoubleClick(x=125, y=115)
                mockReleaseMouse.assert_called_once()

    def testOnLeftDoubleClickUpdatesMessageOnIdOk(self):
        """
        Verify that UmlSDMessageEventHandler.OnLeftDoubleClick
        accepts wx.ID_OK and updates the SD message and label.
        """
        umlSDMessage: UmlSDMessage             = self._createReflexiveMessage(lifeLine=self._lifeLine)
        eventHandler: UmlSDMessageEventHandler = self._attachEventHandler(umlSDMessage=umlSDMessage)

        updatedMessage: SDMessage = SDMessage(message='updatedViaIdOk')
        mockDlg: MagicMock = MagicMock()
        mockDlg.ShowModal.return_value = ID_OK
        mockDlg.sdMessage = updatedMessage
        mockDlg.__enter__.return_value = mockDlg
        mockDlg.__exit__.return_value = None

        with patch('umlshapes.sd.eventhandlers.UmlSDMessageEventHandler.DlgEditSDMessage', return_value=mockDlg):
            with patch.object(eventHandler, '_indicateFrameModified') as mockIndicateModified:
                eventHandler.OnLeftDoubleClick(x=125, y=115)
                self.assertEqual(umlSDMessage.sdMessage.message, 'updatedViaIdOk')
                self.assertEqual(umlSDMessage.messageLabel.label, 'updatedViaIdOk')
                mockIndicateModified.assert_called_once()

    def testOnLeftDoubleClickDoesNotUpdateOnCancel(self):
        """
        Verify that UmlSDMessageEventHandler.OnLeftDoubleClick
        does not update message on ID_CANCEL.
        """
        umlSDMessage: UmlSDMessage             = self._createReflexiveMessage(lifeLine=self._lifeLine)
        eventHandler: UmlSDMessageEventHandler = self._attachEventHandler(umlSDMessage=umlSDMessage)

        mockDlg: MagicMock = MagicMock()
        mockDlg.ShowModal.return_value = ID_CANCEL
        mockDlg.__enter__.return_value = mockDlg
        mockDlg.__exit__.return_value = None

        with patch('umlshapes.sd.eventhandlers.UmlSDMessageEventHandler.DlgEditSDMessage', return_value=mockDlg):
            with patch.object(eventHandler, '_indicateFrameModified') as mockIndicateModified:
                eventHandler.OnLeftDoubleClick(x=125, y=115)
                self.assertEqual(umlSDMessage.sdMessage.message, 'reflexiveCall')
                mockIndicateModified.assert_not_called()

    def _attachEventHandler(self, umlSDMessage: UmlSDMessage) -> UmlSDMessageEventHandler:
        eventHandler: UmlSDMessageEventHandler = UmlSDMessageEventHandler(
            umlSDMessage=umlSDMessage,
            previousEventHandler=umlSDMessage.GetEventHandler()
        )
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlSDMessage.SetEventHandler(eventHandler)
        return eventHandler

    def _createTestInstance(
        self,
        name: str = TEST_INSTANCE_NAME,
        x:    int = INSTANCE_DEFAULT_X,
        y:    int = INSTANCE_DEFAULT_Y
    ) -> UmlSDInstance:

        sdInstanceModel: SDInstance = SDInstance()
        sdInstanceModel.instanceName = name

        umlSDInstance: UmlSDInstance = UmlSDInstance(
            sdInstance=sdInstanceModel
        )
        umlSDInstance.umlFrame = self._diagramFrame
        umlSDInstance.SetX(x)
        umlSDInstance.SetY(y)
        umlSDInstance.umlSDLifeLine.SetX(x)
        self._diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.Show(True)

        return umlSDInstance

    def _createReflexiveMessage(
        self,
        lifeLine: UmlSDLifeLine,
        fromY:    int = INITIAL_FROM_Y,
        toY:      int = INITIAL_TO_Y
    ) -> UmlSDMessage:

        modelMessage: SDMessage = SDMessage(
            message='reflexiveCall',
            src=lifeLine.umlInstanceName.sdInstance,
            sourceY=fromY,
            dst=lifeLine.umlInstanceName.sdInstance,
            destinationY=toY
        )
        umlSDMessage: UmlSDMessage = UmlSDMessage(
            sdMessage=modelMessage,
            messageType=SDMessageType.SYNCHRONOUS
        )

        umlSDMessage.umlFrame = self._diagramFrame
        lifeLine.addMessage(umlSDMessage=umlSDMessage, destinationLifeLine=lifeLine)
        umlSDMessage.fromY = fromY
        umlSDMessage.toY   = toY

        lifeLineX: int = round(lifeLine.GetX())
        umlSDMessage.setReflexiveMessagePoints(lifeLineX=lifeLineX, fromY=fromY, toY=toY)
        self._diagramFrame.umlDiagram.AddShape(umlSDMessage)
        umlSDMessage.Show(True)

        return umlSDMessage


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(TestSDMessageDismissal))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
