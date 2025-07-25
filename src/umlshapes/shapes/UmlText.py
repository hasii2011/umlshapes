
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Brush
from wx import ColourDatabase
from wx import FONTSTYLE_ITALIC
from wx import FONTWEIGHT_BOLD
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_NORMAL

from wx import Colour
from wx import Font
from wx import MemoryDC
from wx import Menu

from wx.lib.ogl import Shape
from wx.lib.ogl import TextShape

from pyutmodelv2.PyutText import PyutText

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.IDMixin import IDMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlFontFamily import UmlFontFamily

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.UmlUtils import UmlUtils

CONTROL_POINT_SIZE: int = 4         # Make this a preference


class UmlText(ControlPointMixin, TextShape, TopLeftMixin, IDMixin):
    MARGIN: int = 5

    def __init__(self, pyutText: PyutText, size: UmlDimensions = None):
        """

        Args:
            pyutText:
            size:       An initial size that overrides the default
        """

        self.logger: Logger = getLogger(__name__)

        # Use preferences to get initial size if not specified
        self._preferences: UmlPreferences = UmlPreferences()

        if size is None:
            textSize: UmlDimensions = self._preferences.useCaseSize
        else:
            textSize = size

        self._pyutText: PyutText = pyutText

        super().__init__(shape=self)

        TextShape.__init__(self, width=textSize.width, height=textSize.height)
        TopLeftMixin.__init__(self, umlShape=self, width=textSize.width, height=textSize.height)
        IDMixin.__init__(self, umlShape=self)

        self.shadowOffsetX = 0      #
        self.shadowOffsetY = 0      #

        self._textFontFamily: UmlFontFamily = self._preferences.textFontFamily
        self._textSize:       int  = self._preferences.textFontSize
        self._isBold:         bool = self._preferences.textBold
        self._isItalicized:   bool = self._preferences.textItalicize

        self._defaultFont: Font = UmlUtils.defaultFont()
        self._textFont:    Font = self._defaultFont.GetBaseFont()

        self._redColor:   Colour = ColourDatabase().Find('Red')
        self._blackColor: Colour = ColourDatabase().Find('Black')

        self.AddText(pyutText.content)

        self._initializeTextFont()
        self._menu: Menu = cast(Menu, None)

        umlBackgroundColor: UmlColor = self._preferences.textBackGroundColor
        backgroundColor:    Colour   = Colour(UmlColor.toWxColor(umlBackgroundColor))

        self._brush: Brush = Brush(backgroundColor)
        self.SetDraggable(drag=True)
        self.SetCentreResize(False)

    @property
    def umlFrame(self) -> ClassDiagramFrame | UseCaseDiagramFrame | SequenceDiagramFrame:
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: ClassDiagramFrame | UseCaseDiagramFrame | SequenceDiagramFrame):
        self.SetCanvas(frame)

    @property
    def selected(self) -> bool:
        return self.Selected()

    @selected.setter
    def selected(self, select: bool):
        self.Select(select=select)

    @property
    def shadowOffsetX(self):
        return self._shadowOffsetX

    @shadowOffsetX.setter
    def shadowOffsetX(self, value):
        self._shadowOffsetX = value

    @property
    def shadowOffsetY(self):
        return self._shadowOffsetY

    @shadowOffsetY.setter
    def shadowOffsetY(self, value):
        self._shadowOffsetY = value

    @property
    def moveColor(self) -> Colour:
        return self._redColor

    @property
    def pyutText(self):
        return self._pyutText

    @pyutText.setter
    def pyutText(self, pyutText: PyutText):
        self._pyutText = pyutText

    @property
    def textSize(self) -> int:
        return self._textSize

    @textSize.setter
    def textSize(self, newSize: int):
        self._textSize = newSize

    @property
    def isBold(self) -> bool:
        return self._isBold

    @isBold.setter
    def isBold(self, newValue: bool):
        self._isBold = newValue

    @property
    def isItalicized(self) -> bool:
        return self._isItalicized

    @isItalicized.setter
    def isItalicized(self, newValue: bool):
        self._isItalicized = newValue

    @property
    def textFontFamily(self) -> UmlFontFamily:
        return self._textFontFamily

    @textFontFamily.setter
    def textFontFamily(self, newValue: UmlFontFamily):
        self._textFontFamily = newValue

    @property
    def textFont(self) -> Font:
        return self._textFont

    @textFont.setter
    def textFont(self, newFont: Font):
        self._textFont = newFont

    def OnDraw(self, dc: MemoryDC):

        self.ClearText()
        self.AddText(self.pyutText.content)

        dc.SetBrush(self._brush)

        if self.Selected() is True:
            UmlUtils.drawSelectedRectangle(dc=dc, shape=self)

    def OnDrawContents(self, dc):

        if self.Selected() is True:
            self.SetTextColour('Red')
        else:
            self.SetTextColour('Black')

        super().OnDrawContents(dc=dc)

    def addChild(self, shape: Shape):
        """
        The event handler for UML Control Points wants to know who its` parent is
        Args:
            shape:
        """
        self._children.append(shape)

    def _initializeTextFont(self):
        """
        Use the model to get other text attributes; We'll
        get what was specified or defaults
        """

        self._textFont.SetPointSize(self.textSize)

        if self.isBold is True:
            self._textFont.SetWeight(FONTWEIGHT_BOLD)
        if self.isItalicized is True:
            self._textFont.SetWeight(FONTWEIGHT_NORMAL)

        if self.isItalicized is True:
            self._textFont.SetStyle(FONTSTYLE_ITALIC)
        else:
            self._textFont.SetStyle(FONTSTYLE_NORMAL)

        self._textFont.SetPointSize(self.textSize)
        self._textFont.SetFamily(UmlUtils.umlFontFamilyToWxFontFamily(self.textFontFamily))

        self.SetFont(self._textFont)

    def __str__(self) -> str:
        return self.pyutText.content

    def __repr__(self):

        strMe: str = f"[UmlText - umlId: `{self.id} `modelId: '{self.pyutText.id}']"
        return strMe
