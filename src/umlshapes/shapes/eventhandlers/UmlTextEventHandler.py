
from typing import cast
from typing import NewType
from typing import List

from logging import Logger
from logging import getLogger

from wx import RED
from wx import EVT_MENU
from wx import FONTSTYLE_ITALIC
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import FONTWEIGHT_NORMAL
from wx import OK
from wx import PENSTYLE_SOLID

from wx import DC
from wx import Bitmap
from wx import CommandEvent
from wx import Menu
from wx import MenuItem
from wx import Colour
from wx import Pen

from wx import NewIdRef as wxNewIdRef

from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas

from pyutmodelv2.PyutText import PyutText

from umlshapes.dialogs.DlgEditText import DlgEditText
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.shapes.UmlText import UmlText

from umlshapes.resources.images.textdetails.DecreaseTextSize import embeddedImage as DecreaseTextSize
from umlshapes.resources.images.textdetails.IncreaseTextSize import embeddedImage as IncreaseTextSize

ShapeList = NewType('ShapeList', List[Shape])

ID_MENU_INCREASE_SIZE:  int = wxNewIdRef()
ID_MENU_DECREASE_SIZE:  int = wxNewIdRef()
ID_MENU_BOLD_TEXT:      int = wxNewIdRef()
ID_MENU_ITALIC_TEXT:    int = wxNewIdRef()

TEXT_SIZE_INCREMENT: int = 2
TEXT_SIZE_DECREMENT: int = 2


class UmlTextEventHandler(UmlBaseEventHandler):

    def __init__(self):

        self.logger: Logger = getLogger(__name__)
        super().__init__()

        self._moveColor: Colour = RED
        self._outlinePen: Pen   = Pen(colour=self._moveColor, width=2, style=PENSTYLE_SOLID)

        self._menu: Menu = cast(Menu, None)

    @property
    def umlText(self) -> UmlText:
        return self.GetShape()

    def OnHighlight(self, dc: DC):
        super().OnHighlight(dc)

    def OnDragRight(self, draw, x, y, keys=0, attachment=0):
        super().OnDragRight(draw=draw, x=x, y=y, attachment=attachment)

        self.logger.info(f'{draw=}')

    def OnRightClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        """
        Use this to pop up a menu

        Args:
            x:
            y:
            keys:
            attachment:
        """
        if self._previousHandler:
            self._previousHandler.OnRightClick(x, y, keys, attachment)

        self.logger.info(f'{self.umlText}')

        if self._menu is None:
            self._menu = self._createMenu()

        canvas: ShapeCanvas = self.umlText.GetCanvas()

        canvas.PopupMenu(self._menu, x, y)

    def OnLeftDoubleClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):

        super().OnLeftDoubleClick(x=x, y=y, keys=keys, attachment=attachment)

        umlText:  UmlText  = self.GetShape()
        pyutText: PyutText = umlText.pyutText

        umlFrame:  ClassDiagramFrame  = umlText.GetCanvas()

        with DlgEditText(parent=umlFrame, pyutText=pyutText,) as dlg:
            if dlg.ShowModal() == OK:
                umlFrame.refresh()

        umlText.selected = False

    def _createMenu(self) -> Menu:

        menu: Menu = Menu()

        increaseItem: MenuItem = menu.Append(ID_MENU_INCREASE_SIZE, 'Increase Size', 'Increase Text Size by 2 points')
        decreaseItem: MenuItem = menu.Append(ID_MENU_DECREASE_SIZE, 'Decrease Size', 'Decrease Text Size by 2 points')

        incBmp: Bitmap = IncreaseTextSize.GetBitmap()
        decBmp: Bitmap = DecreaseTextSize.GetBitmap()

        # noinspection PyTypeChecker
        increaseItem.SetBitmap(incBmp)
        # noinspection PyTypeChecker
        decreaseItem.SetBitmap(decBmp)

        boldItem:       MenuItem = menu.AppendCheckItem(ID_MENU_BOLD_TEXT,   item='Bold Text',      help='Set text to bold')
        italicizedItem: MenuItem = menu.AppendCheckItem(ID_MENU_ITALIC_TEXT, item='Italicize Text', help='Set text to italics')

        if self.umlText.isBold is True:
            boldItem.Check(check=True)
        if self.umlText.isItalicized is True:
            italicizedItem.Check(check=True)

        menu.Bind(EVT_MENU, self._onChangeTextSize, id=ID_MENU_INCREASE_SIZE)
        menu.Bind(EVT_MENU, self._onChangeTextSize, id=ID_MENU_DECREASE_SIZE)
        menu.Bind(EVT_MENU, self._onToggleBold,     id=ID_MENU_BOLD_TEXT)
        menu.Bind(EVT_MENU, self._onToggleItalicize, id=ID_MENU_ITALIC_TEXT)

        return menu

    def _onChangeTextSize(self, event: CommandEvent):
        """
        Callback for the popup menu on UmlText object

        Args:
            event:
        """
        eventId: int     = event.GetId()
        umlText: UmlText = self.umlText

        if eventId == ID_MENU_INCREASE_SIZE:
            umlText.textSize += TEXT_SIZE_INCREMENT
        elif eventId == ID_MENU_DECREASE_SIZE:
            umlText.textSize -= TEXT_SIZE_DECREMENT
        else:
            assert False, f'Unhandled text size event: {eventId}'

        umlText.textFont.SetPointSize(umlText.textSize)
        self.__updateDisplay()

    # noinspection PyUnusedLocal
    def _onToggleBold(self, event: CommandEvent):

        umlText: UmlText = self.umlText

        if umlText.isBold is True:
            umlText.isBold = False
            umlText.textFont.SetWeight(FONTWEIGHT_NORMAL)
        else:
            umlText.isBold = True
            umlText.textFont.SetWeight(FONTWEIGHT_BOLD)

        self.__updateDisplay()

    # noinspection PyUnusedLocal
    def _onToggleItalicize(self, event: CommandEvent):

        umlText: UmlText = self.umlText

        if umlText.isItalicized is True:
            umlText.isItalicized = False
            umlText.textFont.SetStyle(FONTSTYLE_NORMAL)
        else:
            umlText.isItalicized = True
            umlText.textFont.SetStyle(FONTSTYLE_ITALIC)

        self.__updateDisplay()

    def __updateDisplay(self):

        # self.umlText.autoResize()     TODO implement this

        canvas: UmlFrame = self.umlText.GetCanvas()
        canvas.refresh()
