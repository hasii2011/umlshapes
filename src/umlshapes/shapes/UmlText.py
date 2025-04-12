
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Brush
from wx import ColourDatabase
from wx import FONTSTYLE_ITALIC
from wx import FONTWEIGHT_BOLD
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_NORMAL

from wx import Colour
from wx import Font
from wx import MemoryDC
from wx import Menu

from wx.lib.ogl import CONTROL_POINT_DIAGONAL
from wx.lib.ogl import CONTROL_POINT_HORIZONTAL
from wx.lib.ogl import CONTROL_POINT_VERTICAL

from wx.lib.ogl import TextShape

from pyutmodelv2.PyutText import PyutText

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.types.UmlColor import UmlColor

from umlshapes.types.UmlFontFamily import UmlFontFamily
from umlshapes.UmlUtils import UmlUtils

from umlshapes.shapes.UmlControlPoint import UmlControlPoint

DEFAULT_FONT_SIZE:  int = 10
CONTROL_POINT_SIZE: int = 4


class UmlText(TextShape):
    MARGIN: int = 5

    def __init__(self, pyutText: PyutText, width: int = 0, height: int = 0):    # TODO make default text size a preference):

        self.logger: Logger = getLogger(__name__)

        w: int = width
        h: int = height

        # Use preferences to get initial size if not specified
        preferences: UmlPreferences = UmlPreferences()

        if width == 0:
            w = preferences.textDimensions.width
        if height == 0:
            h = preferences.textDimensions.height

        self._pyutText: PyutText = pyutText

        super().__init__(width=w, height=h)

        self.shadowOffsetX = 0      #
        self.shadowOffsetY = 0      #

        self._textFontFamily: UmlFontFamily = preferences.textFontFamily
        self._textSize:       int  = preferences.textFontSize
        self._isBold:         bool = preferences.textBold
        self._isItalicized:   bool = preferences.textItalicize

        self._defaultFont: Font = Font(DEFAULT_FONT_SIZE, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL)
        self._textFont:    Font = self._defaultFont.GetBaseFont()

        self._redColor:   Colour = ColourDatabase().Find('Red')
        self._blackColor: Colour = ColourDatabase().Find('Black')

        self.AddText(pyutText.content)

        self._initializeTextFont()
        self._menu: Menu = cast(Menu, None)

        umlBackgroundColor: UmlColor = preferences.textBackGroundColor
        backgroundColor:    Colour   = Colour(UmlColor.toWxColor(umlBackgroundColor))

        self._brush: Brush = Brush(backgroundColor)
        self.SetDraggable(drag=True)

    def OnDraw(self, dc: MemoryDC):

        # debugText: str = (
        #     f'{self._pyutText.content} Pen Color: {self.GetPen().GetColour()} "'
        #     f'Brush Color: {self.GetBrush().GetColour()} '
        #     f'Background Brush: {self.GetBackgroundBrush().GetColour()} '
        #     f'Background Pen: {self.GetBackgroundPen().GetColour()} '
        # )
        dc.SetBrush(self._brush)
        # debugText: str = (
        #     f'{self._pyutText.content} '
        #     f'Brush Color: {dc.GetBrush().GetColour()}'
        # )
        # self.logger.info(debugText)
        if self.Selected() is True:
            dc.SetPen(UmlUtils.redDashedPen())
            sx = self.GetX()
            sy = self.GetY()

            width  = self.GetWidth() + 3
            height = self.GetHeight() + 3

            x1 = round(sx - width  // 2)
            y1 = round(sy - height // 2)

            dc.DrawRectangle(x1, y1, round(width), round(height))

    def OnDrawContents(self, dc):

        if self.Selected() is True:
            self.SetTextColour('Red')
        else:
            self.SetTextColour('Black')

        super().OnDrawContents(dc=dc)

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

    def MakeControlPoints(self):
        """
        Make a list of control points (draggable handles) appropriate to
        the shape.
        """
        maxX, maxY = self.GetBoundingBoxMax()
        minX, minY = self.GetBoundingBoxMin()

        widthMin = minX + CONTROL_POINT_SIZE + 2
        heightMin = minY + CONTROL_POINT_SIZE + 2

        # Offsets from main object
        top = -heightMin / 2.0
        bottom = heightMin / 2.0 + (maxY - minY)
        left = -widthMin / 2.0
        right = widthMin / 2.0 + (maxX - minX)

        control: UmlControlPoint = UmlControlPoint(self._canvas, self, CONTROL_POINT_SIZE, left, top, CONTROL_POINT_DIAGONAL)
        self._canvas.AddShape(control)
        self._controlPoints.append(control)

        control = UmlControlPoint(self._canvas, self, CONTROL_POINT_SIZE, 0, top, CONTROL_POINT_VERTICAL)
        self._canvas.AddShape(control)
        self._controlPoints.append(control)

        control = UmlControlPoint(self._canvas, self, CONTROL_POINT_SIZE, right, top, CONTROL_POINT_DIAGONAL)
        self._canvas.AddShape(control)
        self._controlPoints.append(control)

        control = UmlControlPoint(self._canvas, self, CONTROL_POINT_SIZE, right, 0, CONTROL_POINT_HORIZONTAL)
        self._canvas.AddShape(control)
        self._controlPoints.append(control)

        control = UmlControlPoint(self._canvas, self, CONTROL_POINT_SIZE, right, bottom, CONTROL_POINT_DIAGONAL)
        self._canvas.AddShape(control)
        self._controlPoints.append(control)

        control = UmlControlPoint(self._canvas, self, CONTROL_POINT_SIZE, 0, bottom, CONTROL_POINT_VERTICAL)
        self._canvas.AddShape(control)
        self._controlPoints.append(control)

        control = UmlControlPoint(self._canvas, self, CONTROL_POINT_SIZE, left, bottom, CONTROL_POINT_DIAGONAL)
        self._canvas.AddShape(control)
        self._controlPoints.append(control)

        control = UmlControlPoint(self._canvas, self, CONTROL_POINT_SIZE, left, 0, CONTROL_POINT_HORIZONTAL)
        self._canvas.AddShape(control)
        self._controlPoints.append(control)

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
        return f'UmlText - modelId: `{self._pyutText.id}`'

    def __repr__(self):

        strMe: str = f"[UmlText  modelId: '{self._pyutText.id}']"
        return strMe
