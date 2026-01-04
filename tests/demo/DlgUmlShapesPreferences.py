
from logging import Logger
from logging import getLogger

from wx import DEFAULT_DIALOG_STYLE
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import ID_CANCEL
from wx import ID_OK
from wx import NB_FIXEDWIDTH
from wx import NB_TOP
from wx import Notebook
from wx import OK
from wx import CANCEL

from wx import CommandEvent
from wx import RESIZE_BORDER
from wx import Size
from wx import StdDialogButtonSizer

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from umlshapes.dialogs.preferences.DefaultValuesPanel import DefaultValuesPanel
from umlshapes.dialogs.preferences.DiagramPreferencesPanel import DiagramPreferencesPanel


class DlgUmlShapesPreferences(SizedDialog):

    def __init__(self, parent):

        style:   int  = DEFAULT_DIALOG_STYLE | RESIZE_BORDER
        dlgSize: Size = Size(460, 500)

        super().__init__(parent, title='UML Shape Preferences', size=dlgSize, style=style)

        self.logger: Logger     = getLogger(__name__)
        sizedPanel:  SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('vertical')
        sizedPanel.SetSizerProps(proportion=1, expand=True)

        nbStyle: int = NB_TOP | NB_FIXEDWIDTH
        book: Notebook = Notebook(sizedPanel, style=nbStyle)
        book.SetSizerProps(expand=True, proportion=1)

        diagramPreferencesPanel:      DiagramPreferencesPanel = DiagramPreferencesPanel(parent=book)
        defaultValuesPreferencesPage: DefaultValuesPanel      = DefaultValuesPanel(parent=book)

        book.AddPage(diagramPreferencesPanel,      text=diagramPreferencesPanel.name,      select=False)
        book.AddPage(defaultValuesPreferencesPage, text=defaultValuesPreferencesPage.name, select=True)

        self._layoutStandardOkCancelButtonSizer()
        # self.Fit()
        # self.SetMinSize(self.GetSize())

    def _layoutStandardOkCancelButtonSizer(self):
        """
        Call this last when creating controls; Will take care of
        adding callbacks for the Ok and Cancel buttons
        """
        buttSizer: StdDialogButtonSizer = self.CreateStdDialogButtonSizer(OK | CANCEL)

        self.SetButtonSizer(buttSizer)
        self.Bind(EVT_BUTTON, self._onOk,    id=ID_OK)
        self.Bind(EVT_BUTTON, self._onClose, id=ID_CANCEL)
        self.Bind(EVT_CLOSE,  self._onClose)

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        """
        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def _onClose(self, event: CommandEvent):
        """
        """
        self.EndModal(CANCEL)
