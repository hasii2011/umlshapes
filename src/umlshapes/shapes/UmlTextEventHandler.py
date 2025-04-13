
from typing import cast
from typing import NewType
from typing import List

from logging import Logger
from logging import getLogger

from wx import Bitmap
from wx import ClientDC
from wx import CommandEvent

from wx import EVT_MENU
from wx import FONTSTYLE_ITALIC
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_BOLD
from wx import FONTWEIGHT_NORMAL
from wx import MOD_CMD
from wx import PENSTYLE_SOLID

from wx import DC
from wx import Menu
from wx import MenuItem
from wx import Colour
from wx import Pen

from wx import NewIdRef as wxNewIdRef

from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeEvtHandler

from umlshapes.frames.UmlFrame import UmlFrame
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


class UmlTextEventHandler(ShapeEvtHandler):

    def __init__(self, moveColor: Colour):

        self.logger: Logger = getLogger(__name__)
        super().__init__(self)

        self._moveColor: Colour = moveColor
        self._outlinePen: Pen    = Pen(colour=self._moveColor, width=2, style=PENSTYLE_SOLID)

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
        Use this to pop up menu

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

    def OnLeftClick(self, x: int, y: int, keys=0, attachment=0):

        self.logger.info(f'({x},{y}), {keys=} {attachment=}')
        shape:  Shape       = self.GetShape()
        canvas: ShapeCanvas = shape.GetCanvas()
        dc:     ClientDC    = ClientDC(canvas)

        canvas.PrepareDC(dc)

        if keys == MOD_CMD:
            pass
        else:
            self._unSelectAllShapesOnCanvas(shape, canvas, dc)
        shape.Select(True, dc)

    def OnDrawOutline(self, dc: ClientDC, x: float, y: float, w: int, h: int):
        """
        Called when shape is moving or is resized
        Args:
            dc:  This is a client DC; It won't draw on OS X
            x:
            y:
            w:
            h:
        """
        self.logger.debug(f'Position: ({x},{y}) Size: ({w},{h})')

        shape: Shape  = self.GetShape()
        shape.Move(dc=dc, x=x, y=y, display=True)
        # Hmm, weird how SetSize namex width and height
        shape.SetSize(x=w, y=h)

    def _unSelectAllShapesOnCanvas(self, shape: Shape, canvas: ShapeCanvas, dc: ClientDC):

        # Unselect if already selected
        if shape.Selected() is True:
            shape.Select(False, dc)
            canvas.Refresh(False)
        else:
            shapeList: ShapeList = canvas.GetDiagram().GetShapeList()
            toUnselect: ShapeList = ShapeList([])

            for s in shapeList:
                if s.Selected() is True:
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            if len(toUnselect) > 0:
                for s in toUnselect:
                    s.Select(False, dc)

                # #canvas.Redraw(dc)
                canvas.Refresh(False)

    def _createMenu(self) -> Menu:

        menu: Menu = Menu()

        increaseItem: MenuItem = menu.Append(ID_MENU_INCREASE_SIZE, 'Increase Size', 'Increase Text Size by 2 points')
        decreaseItem: MenuItem = menu.Append(ID_MENU_DECREASE_SIZE, 'Decrease Size', 'Decrease Text Size by 2 points')

        incBmp: Bitmap = IncreaseTextSize.GetBitmap()
        decBmp: Bitmap = DecreaseTextSize.GetBitmap()

        increaseItem.SetBitmap(incBmp)
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
        Callback for popup menu on UmlText object

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
