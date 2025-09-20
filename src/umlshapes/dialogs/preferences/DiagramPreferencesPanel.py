
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from wx import CB_READONLY
from wx import EVT_CHECKBOX
from wx import EVT_CHOICE
from wx import EVT_COMBOBOX
from wx import EVT_SPINCTRL

from wx import CheckBox
from wx import Choice
from wx import ComboBox
from wx import Size
from wx import SpinCtrl
from wx import SpinEvent
from wx import Window
from wx import CommandEvent

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from umlshapes.dialogs.preferences.NamedSpinCtrl import NSCValueType
from umlshapes.dialogs.preferences.NamedSpinCtrl import NSC_CALLBACK_PARAMETER_TYPE
from umlshapes.dialogs.preferences.NamedSpinCtrl import NamedSpinControlDescription
from umlshapes.dialogs.preferences.NamedSpinCtrl import NamedSpinCtrl
from umlshapes.dialogs.preferences.BasePreferencesPanel import BasePreferencesPanel

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlPenStyle import UmlPenStyle

from umlshapes.preferences.UmlPreferences import UmlPreferences

SPINNER_WIDTH:  int = 60
SPINNER_HEIGHT: int = 35

DEFAULT_SPIN_CTRL_SIZE: Size = Size(width=75, height=SPINNER_HEIGHT)

MIN_VIRTUAL_WINDOW_WIDTH: int = 0
MAX_VIRTUAL_WINDOW_WIDTH: int = 50000


def virtualWindowWidthChanged(newValue: NSC_CALLBACK_PARAMETER_TYPE):
    UmlPreferences().virtualWindowWidth = newValue


virtualWindowLengthDescription: NamedSpinControlDescription = NamedSpinControlDescription(
    label='UML Frame Virtual Window Width',
    controlSize=DEFAULT_SPIN_CTRL_SIZE,
    minValue=MIN_VIRTUAL_WINDOW_WIDTH,
    maxValue=MAX_VIRTUAL_WINDOW_WIDTH,
    valueType=NSCValueType.INT,
    valueChangedCallback=virtualWindowWidthChanged
)


class DiagramPreferencesPanel(BasePreferencesPanel):
    """
    This is a complex layout.  The following description is good as of version 0.9.25;
    This is a complex layout.  The following description is good as of version 0.9.25;
    If you change the layout please update this (Yeah, I do not like this kind of brittle
    documentation either

        ----------------- Dialog Sized Panel --------------------------------------------------------------------------------------------------------
        |                                                                                                                                           |
        |   ----------------- HorizontalPanel ---------------------------------------------------------------------------------------------         |
        |  |     ------------------- Vertical Panel --------------   ------------------- darkMOdeSSB -------------------    |         |
        |  |     |                                               |   |                                                      |             |         |
        |  |     |                                               |   |                                                      |             |         |
        |  |     |                                               |   |                                                      |             |         |
        |  |     |                                               |   |                                                      |             |         |
        |  |     |                                               |   |                                                      |             |         |
        |  |     -------------------------------------------------   --------------------------------------------------------             |         |
        |  --------------------------------------------------------------------------------------------------------------------------------         |
        |                                                                                                                                           |
        |   ------------------------------------------gridPanel-------------------------------------------------------------------                  |
        |  |                                                                                                                     |                  |
        |  |    ----------- gridIntervalSSB --------- ---------- gridLineColorSSB ---   ----------- gridLineStyleSSB ---         |                  |
        |  |    |                                   | |                             |   |                              |         |                  |
        |  |    |                                   | |                             |   |                              |         |                  |
        |  |    |                                   | |                             |   |                              |         |                  |
        |  |    |                                   | |                             |   |                              |         |                  |
        |  |    |                                   | |                             |   |                              |         |                  |
        |  |    |                                   | |                             |   |                              |         |                  |
        |  |    ------------------------------------  ------------_------------------   --------------------------------         |                  |
        |  |                                                                                                                     |                  |
        |  |                                                                                                                     |                  |
        |   ----------------------------------------------------------------------------------------------------------------------                  |
        |                                                                                                                                           |
        |                                                                                                                                           |
        ----------------- Dialog Sized Panel --------------------------------------------------------------------------------------------------------

    """

    def __init__(self, parent: Window):

        self.logger: Logger = getLogger(__name__)

        super().__init__(parent)
        self.SetSizerType('vertical')

        self._enableBackgroundGrid: CheckBox = cast(CheckBox, None)
        self._snapToGrid:           CheckBox = cast(CheckBox, None)
        self._centerDiagramView:    CheckBox = cast(CheckBox, None)
        self._showParameters:       CheckBox = cast(CheckBox, None)

        self._virtualWindowWidth:   NamedSpinCtrl = cast(NamedSpinCtrl, None)

        self._gridInterval:         SpinCtrl = cast(SpinCtrl, None)
        self._gridLineColor:        ComboBox = cast(ComboBox, None)
        self._gridStyleChoice:      Choice   = cast(Choice, None)

        self._normalBackgroundColor:   ComboBox = cast(ComboBox, None)
        self._darkModeBackgroundColor: ComboBox = cast(ComboBox, None)
        self._darkModeGridLineColor:   ComboBox = cast(ComboBox, None)

        self._layoutControls(self)
        self._setControlValues()
        self._bindCallbacks(parent=self)

    def _layoutControls(self, parentSizedPanel: SizedPanel):

        horizontalPanel: SizedPanel = SizedPanel(parentSizedPanel)
        verticalPanel:   SizedPanel = SizedPanel(horizontalPanel)
        horizontalPanel.SetSizerType('horizontal')
        horizontalPanel.SetSizerProps(expand=True, proportion=3)
        verticalPanel.SetSizerType('vertical')

        self._layoutDiagramPreferences(verticalPanel=verticalPanel)
        self._layoutDarkModeOptions(horizontalPanel=horizontalPanel)
        self._layoutGridOptions(panel=parentSizedPanel)

        self._fixPanelSize(panel=self)

    @property
    def name(self) -> str:
        return 'Diagram'

    def _setControlValues(self):
        """
        """
        self._resetSnapToGridControl()

        self._enableBackgroundGrid.SetValue(self._preferences.backGroundGridEnabled)
        self._snapToGrid.SetValue(self._preferences.snapToGrid)
        self._centerDiagramView.SetValue(self._preferences.centerDiagram)
        self._showParameters.SetValue(self._preferences.showParameters)
        self._virtualWindowWidth.value = self._preferences.virtualWindowWidth

        self._gridInterval.SetValue(self._preferences.backgroundGridInterval)
        self._gridLineColor.SetValue(self._preferences.gridLineColor.value)

        gridLineStyles: List[str] = self._gridStyleChoice.GetItems()
        selectedIndex:  int       = gridLineStyles.index(self._preferences.gridLineStyle.value)
        self._gridStyleChoice.SetSelection(selectedIndex)

        self._normalBackgroundColor.SetValue(self._preferences.backGroundColor.value)
        self._darkModeBackgroundColor.SetValue(self._preferences.darkModeBackGroundColor.value)
        self._darkModeGridLineColor.SetValue(self._preferences.darkModeGridLineColor.value)

    def _bindCallbacks(self, parent):

        parent.Bind(EVT_CHECKBOX, self._onEnableBackgroundGridChanged,   self._enableBackgroundGrid)
        parent.Bind(EVT_CHECKBOX, self._onSnapToGridChanged,             self._snapToGrid)
        parent.Bind(EVT_CHECKBOX, self._onCenterDiagramViewChanged,      self._centerDiagramView)
        parent.Bind(EVT_CHECKBOX, self._onShowParametersChanged,         self._showParameters)
        parent.Bind(EVT_COMBOBOX, self._onGridLineColorSelectionChanged, self._gridLineColor)
        parent.Bind(EVT_SPINCTRL, self._onGridIntervalChanged,           self._gridInterval)
        parent.Bind(EVT_CHOICE,   self._onGridStyleChanged,              self._gridStyleChoice)

        parent.Bind(EVT_COMBOBOX, self._onNormalBackGroundColorChanged,   self._normalBackgroundColor)
        parent.Bind(EVT_COMBOBOX, self._onDarkModeBackgroundColorChanged, self._darkModeBackgroundColor)
        parent.Bind(EVT_COMBOBOX, self._onDarkModeGridLineColorChanged,   self._darkModeGridLineColor)

    def _layoutDiagramPreferences(self, verticalPanel: SizedPanel):

        self._enableBackgroundGrid = CheckBox(verticalPanel, label='Enable Background Grid')
        self._snapToGrid           = CheckBox(verticalPanel, label='Snap Shapes to Grid')
        self._centerDiagramView    = CheckBox(verticalPanel, label='Center Diagram View')
        self._showParameters       = CheckBox(verticalPanel, label='Show Method Parameters')

        self._virtualWindowWidth = NamedSpinCtrl(parent=verticalPanel, description=virtualWindowLengthDescription)
        # noinspection PyUnresolvedReferences
        # self._virtualWindowWidth.SetSizerProps(proportion=4)

        self._enableBackgroundGrid.SetToolTip('Turn on a diagram grid in the UML Frame')
        self._snapToGrid.SetToolTip('Snap class diagram shapes to the closest grid corner')
        self._centerDiagramView.SetToolTip('Center the view in the virtual frame')
        self._showParameters.SetToolTip('Global value to display method parameters;  Unless overridden by the class')
        self._virtualWindowWidth.SetToolTip('Determines the virtual window width and height of the UML Frame')

        self._fixPanelSize(verticalPanel)

    def _layoutDarkModeOptions(self, horizontalPanel: SizedPanel):

        darkModeOptionsSSB: SizedStaticBox = SizedStaticBox(horizontalPanel, label='Dark Mode Options')
        darkModeOptionsSSB.SetSizerProps(expand=True, proportion=1)

        verticalPanel: SizedPanel = SizedPanel(darkModeOptionsSSB)
        verticalPanel.SetSizerProps(expand=True, proportion=1)

        colorChoices = []
        for cc in UmlColor:
            colorChoices.append(cc.value)

        # Normal Background Color
        normalBackColorSSB: SizedStaticBox = SizedStaticBox(verticalPanel, label='Normal Background Color')
        normalBackColorSSB.SetSizerProps(expand=True, proportion=1)
        self._normalBackgroundColor = ComboBox(normalBackColorSSB, choices=colorChoices, style=CB_READONLY)

        # Dark Mode Background Color
        darkModeBackColorSSB: SizedStaticBox = SizedStaticBox(verticalPanel, label='Dark Mode Background Color')
        darkModeBackColorSSB.SetSizerProps(expand=True, proportion=1)
        self._darkModeBackgroundColor = ComboBox(darkModeBackColorSSB, choices=colorChoices, style=CB_READONLY)

        # Dark Mode Grid Line Color
        darkModeGridLineColorSSB: SizedStaticBox = SizedStaticBox(verticalPanel, label='Dark Mode Grid Line Color')
        darkModeGridLineColorSSB.SetSizerProps(expand=True, proportion=1)
        self._darkModeGridLineColor = ComboBox(darkModeGridLineColorSSB, choices=colorChoices, style=CB_READONLY)

    def _layoutGridIntervalControl(self, sizedPanel):
        gridIntervalSSB: SizedStaticBox = SizedStaticBox(sizedPanel, label='Grid Interval')
        gridIntervalSSB.SetSizerProps(expand=True)
        self._gridInterval = SpinCtrl(parent=gridIntervalSSB)

    def _layoutGridOptions(self, panel: SizedPanel):

        staticBox: SizedStaticBox = SizedStaticBox(panel, label='Grid Options')
        staticBox.SetSizerProps(expand=True, proportion=2)

        gridPanel: SizedPanel = SizedPanel(staticBox)
        gridPanel.SetSizerType('horizontal')
        gridPanel.SetSizerProps(expand=True, proportion=2)

        self._layoutGridIntervalControl(sizedPanel=gridPanel)
        self._layoutGridLineColorControl(panel=gridPanel)
        self._layoutGridStyleChoice(panel=gridPanel)

    def _layoutGridLineColorControl(self, panel: SizedPanel):

        colorChoices = []
        for cc in UmlColor:
            colorChoices.append(cc.value)

        gridLineColorSSB: SizedStaticBox = SizedStaticBox(panel, label='Grid Line Color')
        gridLineColorSSB.SetSizerProps(expand=True, proportion=1)

        self._gridLineColor = ComboBox(gridLineColorSSB, choices=colorChoices, style=CB_READONLY)

    def _layoutGridStyleChoice(self, panel: SizedPanel):

        gridStyles = [s.value for s in UmlPenStyle]

        gridLineStyleSSB: SizedStaticBox = SizedStaticBox(panel, label='Grid Line Style')
        gridLineStyleSSB.SetSizerProps(expand=True, proportion=1)

        self._gridStyleChoice = Choice(gridLineStyleSSB, choices=gridStyles)

    def _onEnableBackgroundGridChanged(self, event: CommandEvent):

        newValue: bool = event.IsChecked()
        self.logger.debug(f'onEnableBackgroundGridChanged - {newValue=}')
        self._preferences.backGroundGridEnabled = newValue
        self._resetSnapToGridControl()

    def _onSnapToGridChanged(self, event: CommandEvent):

        newValue: bool = event.IsChecked()
        self.logger.debug(f'onSnapToGridChanged - {newValue=}')
        self._preferences.snapToGrid = newValue

    def _onCenterDiagramViewChanged(self, event: CommandEvent):
        newValue: bool = event.IsChecked()
        self._preferences.centerDiagram = newValue

    def _onShowParametersChanged(self, event: CommandEvent):
        newValue: bool = event.IsChecked()
        self._preferences.showParameters = newValue

    def _onGridLineColorSelectionChanged(self, event: CommandEvent):

        colorValue:    str              = event.GetString()
        pyutColorEnum: UmlColor = UmlColor(colorValue)

        self._preferences.gridLineColor = pyutColorEnum

    def _onGridIntervalChanged(self, event: SpinEvent):

        newInterval: int = event.GetInt()
        self._preferences.backgroundGridInterval = newInterval

    def _onGridStyleChanged(self, event: CommandEvent):

        styleText: str = event.GetString()
        self.logger.warning(f'{styleText=}')

        pyutPenStyle: UmlPenStyle = UmlPenStyle(styleText)

        self._preferences.gridLineStyle = pyutPenStyle

    def _resetSnapToGridControl(self):
        """
        Make the UI consistent when the background grid is used or not
        If no background grid there is nothing to snap to
        """
        if self._preferences.backGroundGridEnabled is True:
            self._snapToGrid.Enabled = True
        else:
            self._snapToGrid.SetValue(False)
            self._snapToGrid.Enabled = False
            self._preferences.snapToGrid = False

    def _onNormalBackGroundColorChanged(self, event: CommandEvent):
        colorValue:    str      = event.GetString()
        pyutColorEnum: UmlColor = UmlColor(colorValue)

        self._preferences.backGroundColor = pyutColorEnum

    def _onDarkModeBackgroundColorChanged(self, event: CommandEvent):
        colorValue:    str      = event.GetString()
        pyutColorEnum: UmlColor = UmlColor(colorValue)

        self._preferences.darkModeBackGroundColor = pyutColorEnum

    def _onDarkModeGridLineColorChanged(self, event: CommandEvent):
        colorValue:    str      = event.GetString()
        pyutColorEnum: UmlColor = UmlColor(colorValue)

        self._preferences.darkModeGridLineColor = pyutColorEnum
