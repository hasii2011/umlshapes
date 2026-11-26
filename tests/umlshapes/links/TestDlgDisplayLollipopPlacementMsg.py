
from unittest import TestCase
from unittest import main as unitTestMain
from unittest.mock import MagicMock
from unittest.mock import patch

from wx import CommandEvent
from wx import EVT_CHECKBOX
from wx import ID_OK
from wx.lib.ogl import OGLInitialize
from wx.lib.sized_controls import SizedPanel

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.Class import Class
from umlmodel.ModelTypes import ClassName

from umlshapes.dialogs.DlgDisplayLollipopPlacementMsg import DlgDisplayLollipopPlacementMsg
from umlshapes.dialogs.DlgDisplayLollipopPlacementMsg import LOLLIPOP_PLACEMENT_CAPTION
from umlshapes.dialogs.DlgDisplayLollipopPlacementMsg import LOLLIPOP_PLACEMENT_CHECKBOX_LABEL
from umlshapes.dialogs.DlgDisplayLollipopPlacementMsg import LOLLIPOP_PLACEMENT_MESSAGE
from umlshapes.dialogs.preferences.valuepanels.LollipopPreferencesPanel import LollipopPreferencesPanel
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.shapes.UmlClass import UmlClass

CLASS_NAME: str = 'OrderService'


class TestDlgDisplayLollipopPlacementMsg(UnitTestBaseW):
    """
    Unit tests for DlgDisplayLollipopPlacementMsg, ClassDiagramFrame integration, and preferences.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()
        self._umlPubSubEngine: IUmlPubSubEngine = UmlPubSubEngine()
        self._classDiagramFrame: ClassDiagramFrame = ClassDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )
        self._preferences: UmlPreferences = self._classDiagramFrame._preferences
        modelClass: Class = Class(ClassName(CLASS_NAME))
        self._umlClass: UmlClass = UmlClass(modelClass=modelClass)

    def tearDown(self):
        super().tearDown()

    def testDlgDisplayLollipopPlacementMsgInitialization(self):
        """
        Verify that DlgDisplayLollipopPlacementMsg initializes with expected message, caption, and checkbox state.
        """
        self._preferences.showLollipopPlacementDialog = True
        with DlgDisplayLollipopPlacementMsg(parent=self._listeningWindow, preferences=self._preferences) as dlg:
            self.assertEqual(LOLLIPOP_PLACEMENT_MESSAGE, dlg.GetMessage())
            self.assertEqual(LOLLIPOP_PLACEMENT_CAPTION, dlg.GetTitle())
            self.assertEqual(LOLLIPOP_PLACEMENT_CHECKBOX_LABEL, dlg.GetCheckBoxText())
            self.assertTrue(dlg.IsCheckBoxChecked())

    def testOnCheckBoxChangedSetsPreferenceToFalseWhenUnchecked(self):
        """
        Verify that _onCheckBoxChanged callback sets showLollipopPlacementDialog to False
        when the checkbox is unchecked.
        """
        self._preferences.showLollipopPlacementDialog = True
        with DlgDisplayLollipopPlacementMsg(parent=self._listeningWindow, preferences=self._preferences) as dlg:
            commandEvent: CommandEvent = CommandEvent(EVT_CHECKBOX.typeId, dlg.GetId())
            commandEvent.SetInt(0)

            dlg._onCheckBoxChanged(commandEvent)

            self.assertFalse(self._preferences.showLollipopPlacementDialog)

    def testOnCheckBoxChangedSetsPreferenceToTrueWhenChecked(self):
        """
        Verify that _onCheckBoxChanged callback sets showLollipopPlacementDialog to True
        when the checkbox is checked.
        """
        self._preferences.showLollipopPlacementDialog = False
        with DlgDisplayLollipopPlacementMsg(parent=self._listeningWindow, preferences=self._preferences) as dlg:
            commandEvent: CommandEvent = CommandEvent(EVT_CHECKBOX.typeId, dlg.GetId())
            commandEvent.SetInt(1)

            dlg._onCheckBoxChanged(commandEvent)

            self.assertTrue(self._preferences.showLollipopPlacementDialog)

    def testOnCheckBoxChangedWithNonePreferences(self):
        """
        Verify that _onCheckBoxChanged operates safely when preferences is None.
        """
        with DlgDisplayLollipopPlacementMsg(parent=self._listeningWindow, preferences=None) as dlg:
            commandEvent: CommandEvent = CommandEvent(EVT_CHECKBOX.typeId, dlg.GetId())
            commandEvent.SetInt(0)

            dlg._onCheckBoxChanged(commandEvent)

    def testDlgDisplayLollipopPlacementMsgShowModalDispatchesToCallback(self):
        """
        Verify that ShowModal dispatches checkbox state to _onCheckBoxChanged.
        """
        self._preferences.showLollipopPlacementDialog = True
        with DlgDisplayLollipopPlacementMsg(parent=self._listeningWindow, preferences=self._preferences) as dlg:
            with patch.object(dlg, 'IsCheckBoxChecked', return_value=False):
                with patch('wx.RichMessageDialog.ShowModal', return_value=ID_OK):
                    with patch.object(dlg, '_onCheckBoxChanged') as mockCallback:
                        returnCode: int = dlg.ShowModal()

                        self.assertEqual(ID_OK, returnCode)
                        mockCallback.assert_called_once()
                        eventArg: CommandEvent = mockCallback.call_args.args[0]
                        self.assertFalse(eventArg.IsChecked())

    def testOnRequestLollipopLocationShowsDialogWhenPreferenceIsTrue(self):
        """
        Verify that _onRequestLollipopLocation invokes _showLollipopPlacementDialog
        when the preference showLollipopPlacementDialog is True.
        """
        self._preferences.showLollipopPlacementDialog = True

        with patch.object(self._classDiagramFrame, '_showLollipopPlacementDialog') as mockShowDialog:
            self._classDiagramFrame._onRequestLollipopLocation(requestingUmlClass=self._umlClass)

            self.assertTrue(self._classDiagramFrame._requestingLollipopLocation)
            self.assertEqual(self._umlClass, self._classDiagramFrame._requestingUmlClass)
            mockShowDialog.assert_called_once()

    def testOnRequestLollipopLocationDoesNotShowDialogWhenPreferenceIsFalse(self):
        """
        Verify that _onRequestLollipopLocation does not invoke _showLollipopPlacementDialog
        when the preference showLollipopPlacementDialog is False.
        """
        self._preferences.showLollipopPlacementDialog = False

        with patch.object(self._classDiagramFrame, '_showLollipopPlacementDialog') as mockShowDialog:
            self._classDiagramFrame._onRequestLollipopLocation(requestingUmlClass=self._umlClass)

            self.assertTrue(self._classDiagramFrame._requestingLollipopLocation)
            self.assertEqual(self._umlClass, self._classDiagramFrame._requestingUmlClass)
            mockShowDialog.assert_not_called()

    def testClassDiagramFrameShowLollipopPlacementDialog(self):
        """
        Verify that ClassDiagramFrame._showLollipopPlacementDialog instantiates DlgDisplayLollipopPlacementMsg
        with self and self._preferences and calls ShowModal.
        """
        with patch('umlshapes.frames.ClassDiagramFrame.DlgDisplayLollipopPlacementMsg') as mockDlgClass:
            mockDlgInstance: MagicMock = MagicMock()
            mockDlgClass.return_value = mockDlgInstance
            mockDlgInstance.__enter__.return_value = mockDlgInstance

            self._classDiagramFrame._showLollipopPlacementDialog()

            mockDlgClass.assert_called_once_with(
                parent=self._classDiagramFrame,
                preferences=self._preferences
            )
            mockDlgInstance.ShowModal.assert_called_once()

    def testLollipopPreferencesPanelCheckboxUpdatesPreference(self):
        """
        Verify that LollipopPreferencesPanel checkbox reflects preference and updates it on change.
        """
        containerPanel: SizedPanel = SizedPanel(parent=self._listeningWindow)
        prefPanel: LollipopPreferencesPanel = LollipopPreferencesPanel(parent=containerPanel)

        self._preferences.showLollipopPlacementDialog = True
        prefPanel._setControlValues()
        self.assertTrue(prefPanel._showPlacementDialog.GetValue())

        uncheckEvent: CommandEvent = CommandEvent(EVT_CHECKBOX.typeId, prefPanel._showPlacementDialog.GetId())
        uncheckEvent.SetInt(0)
        prefPanel._showPlacementDialog.SetValue(False)
        prefPanel._onShowPlacementDialogChanged(uncheckEvent)
        self.assertFalse(self._preferences.showLollipopPlacementDialog)

        checkEvent: CommandEvent = CommandEvent(EVT_CHECKBOX.typeId, prefPanel._showPlacementDialog.GetId())
        checkEvent.SetInt(1)
        prefPanel._showPlacementDialog.SetValue(True)
        prefPanel._onShowPlacementDialogChanged(checkEvent)
        self.assertTrue(self._preferences.showLollipopPlacementDialog)


if __name__ == '__main__':
    unitTestMain()
