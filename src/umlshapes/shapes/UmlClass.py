
from typing import ClassVar
from typing import Generator
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutObject import PyutObject
from wx import Brush
from wx import ClientDC
from wx import Colour
from wx import DC
from wx import Font
from wx import MemoryDC
from wx import Size

from wx.lib.ogl import RectangleShape

from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutMethod import PyutMethod
from pyutmodelv2.enumerations.PyutStereotype import PyutStereotype
from pyutmodelv2.enumerations.PyutDisplayParameters import PyutDisplayParameters
from pyutmodelv2.enumerations.PyutDisplayMethods import PyutDisplayMethods

from umlshapes.UmlUtils import UmlUtils

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.ControlPointMixin import ControlPointMixin
from umlshapes.types.Common import LeftCoordinate

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition

DUNDER_METHOD_INDICATOR: str = '__'
CONSTRUCTOR_NAME:        str = '__init__'

MARGIN: int = 10


def infiniteSequence() -> Generator[int, None, None]:
    num = 0
    while True:
        yield num
        num += 1


class UmlClass(ControlPointMixin, RectangleShape):
    """

    """
    idGenerator: ClassVar = infiniteSequence()

    def __init__(self, pyutClass: PyutClass = None, size: UmlDimensions = None):
        """]
        Args:
            pyutClass:   A PyutClass Object
            size:
        """
        self._preferences: UmlPreferences = UmlPreferences()

        if pyutClass is None:
            self._pyutClass: PyutClass = PyutClass()
        else:
            self._pyutClass = pyutClass

        if size is None:
            classSize: UmlDimensions = self._preferences.classDimensions
        else:
            classSize = size

        super().__init__(shape=self)
        RectangleShape.__init__(self, w=classSize.width, h=classSize.height)

        self.logger: Logger = getLogger(__name__)

        classBackgroundColor: UmlColor = self._preferences.classBackGroundColor
        backgroundColor:      Colour   = Colour(UmlColor.toWxColor(classBackgroundColor))

        self.SetBrush(Brush(backgroundColor))
        self.SetFont(UmlUtils.defaultFont())

        umlTextColor:      UmlColor = self._preferences.classTextColor
        self._textColor:   Colour   = Colour(UmlColor.toWxColor(umlTextColor))
        self._defaultFont: Font     = UmlUtils.defaultFont()
        self._id:          int       = next(UmlClass.idGenerator)     # unique ID number

        self.SetDraggable(drag=True)
        self.SetCentreResize(False)

    @property
    def pyutClass(self) -> PyutClass:
        return self._pyutClass

    @pyutClass.setter
    def pyutClass(self, pyutClass: PyutClass):
        self._pyutClass = pyutClass

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, newValue: int):
        self._id = newValue

    @property
    def size(self) -> UmlDimensions:
        return UmlDimensions(
            width=round(self.GetWidth()),
            height=round(self.GetHeight())
        )

    @size.setter
    def size(self, newSize: UmlDimensions):

        self.SetWidth(round(newSize.width))
        self.SetHeight(round(newSize.height))

    @property
    def position(self) -> UmlPosition:
        return UmlPosition(x=round(self.GetX()), y=round(self.GetY()))

    @position.setter
    def position(self, position: UmlPosition):

        self.SetX(round(position.x))
        self.SetY(round(position.y))

    @property
    def topLeft(self) -> LeftCoordinate:
        """
        This method necessary because ogl reports positions from the center of the shape
        Calculates the left top coordinate

        Returns:  An adjusted coordinate
        """

        x = self.GetX()                 # This points to the center of the rectangle
        y = self.GetY()                 # This points to the center of the rectangle

        width:  int = self.size.width
        height: int = self.size.height

        left: int = x - (width // 2)
        top:  int = y - (height // 2)

        return LeftCoordinate(x=round(left), y=round(top))

    def OnDraw(self, dc: MemoryDC):

        try:
            super().OnDraw(dc)
        except (ValueError, Exception) as e:
            # Work around a bug where width and height sometimes become a float
            self.logger.warning(f'Bug workaround !!! {e}')

            self.SetWidth(round(self.GetWidth()))
            self.SetHeight(round(self.GetHeight()))
            super().OnDraw(dc)

        # drawing is restricted in the specified region of the device
        w: int = round(self.GetWidth())
        h: int = round(self.GetHeight())
        x: int = self.topLeft.x
        y: int = self.topLeft.y

        dc.SetClippingRegion(x, y, w, h)
        drawingYOffset, maxWidth = self._drawClassHeader(dc=dc, drawText=True)

        if self.pyutClass.showFields is True:
            dc.DrawLine(x, y + drawingYOffset, x + w, y + drawingYOffset)
            fieldsX, fieldsY, fieldsW, fieldsH = self._drawClassFields(dc, True, initialY=y+drawingYOffset)
            y = fieldsY + fieldsH
        dc.DrawLine(x, y, x + w, y)
        #
        # Method needs to be called even though returned values not used  -- TODO look at refactoring
        #
        if self.pyutClass.showMethods is True:
            (methodsX, methodsY, methodsW, methodsH) = self._drawClassMethods(dc=dc, initialY=y)
            # noinspection PyUnusedLocal
            y = methodsY + methodsH
            if methodsW > self._width:
                # self._width = methodsW
                self.SetWidth(methodsW)

        dc.DestroyClippingRegion()

    def OnRightClick(self, x: int, y: int, keys: int = 0, attachment: int = 0):
        super().OnRightClick(x=x, y=y, keys=keys, attachment=attachment)

        self.logger.info(f'You clicked on class: {str(self)}')

    # This is dangerous, accessing internal stuff
    # noinspection PyProtectedMember
    # noinspection SpellCheckingInspection
    def ResetControlPoints(self):
        """
        Reset the positions of the control points (for instance, when the
        shape's shape has changed).
        Override because of widthMin & heightMin does not put the control point right
        on the border
        """
        self.ResetMandatoryControlPoints()

        if len(self._controlPoints) == 0:
            return

        maxX, maxY = self.GetBoundingBoxMax()
        minX, minY = self.GetBoundingBoxMin()

        # widthMin  = minX + UML_CONTROL_POINT_SIZE + 2
        # heightMin = minY + UML_CONTROL_POINT_SIZE + 2
        widthMin  = minX
        heightMin = minY

        # Offsets from the main object
        top = -heightMin / 2.0
        bottom = heightMin / 2.0 + (maxY - minY)
        left = -widthMin / 2.0
        right = widthMin / 2.0 + (maxX - minX)

        self._controlPoints[0]._xoffset = left
        self._controlPoints[0]._yoffset = top

        self._controlPoints[1]._xoffset = 0
        self._controlPoints[1]._yoffset = top

        self._controlPoints[2]._xoffset = right
        self._controlPoints[2]._yoffset = top

        self._controlPoints[3]._xoffset = right
        self._controlPoints[3]._yoffset = 0

        self._controlPoints[4]._xoffset = right
        self._controlPoints[4]._yoffset = bottom

        self._controlPoints[5]._xoffset = 0
        self._controlPoints[5]._yoffset = bottom

        self._controlPoints[6]._xoffset = left
        self._controlPoints[6]._yoffset = bottom

        self._controlPoints[7]._xoffset = left
        self._controlPoints[7]._yoffset = 0

    def autoResize(self):
        """
        Auto-resize the class

        WARNING: Every change here must be reported in the OnDraw method
        """
        pyutObject: PyutClass = self.pyutClass
        umlFrame = self.GetCanvas()
        dc: ClientDC = ClientDC(umlFrame)

        self._startClipping(dc)

        y: int = self.position.y
        # Get header size
        # (headerX, headerY, headerW, headerH) = self._drawClassHeader(dc, False, calcWidth=True)
        headerY, headerW, = self._drawClassHeader(dc, False, calculateWidth=True)
        y += headerY

        # Get the size of the field's portion of the display
        if pyutObject.showFields is True:
            (fieldsX, fieldsY, fieldsW, fieldsH) = self._drawClassFields(dc, False, initialY=y)
            y = fieldsY + fieldsH
        else:
            fieldsW, fieldsH = 0, 0

        # Get method's size
        if pyutObject.showMethods is True:
            (methodX, methodY, methodW, methodH) = self._drawClassMethods(dc=dc, initialY=y)
            y = methodY + methodH
        else:
            methodW, methodH = 0, 0

        w = max(headerW, fieldsW, methodW)
        h = y - headerY
        w += 2 * MARGIN

        minDimensions: UmlDimensions = self._preferences.classDimensions
        if w < minDimensions.width:
            w = minDimensions.width
        if h < minDimensions.height:
            h = minDimensions.height

        # if HACK_FIX_AUTO_RESIZE is True:
        #     w = w - 20      # Hack keeps growing
        self.SetSize(w, h)

        # to automatically replace the sizer objects at a correct place
        if self.Selected() is True:
            self.Select(False)
        self.Select(True)

        self._endClipping(dc)
        # self.eventEngine.sendEvent(OglEventType.DiagramFrameModified)

    def textWidth(self, dc: MemoryDC, text: str):
        """

        Args:
            dc:   Current device context
            text: The string to measure

        Returns:
        """

        size: Size = dc.GetTextExtent(text)
        return round(size.width)

    def textHeight(self, dc: MemoryDC, text: str):
        """

        Args:
            dc:   Current device context
            text: The string to measure

        Returns:

        """

        size: Size = dc.GetTextExtent(text)
        return round(size.height)

    def _drawClassHeader(self, dc: MemoryDC | ClientDC, drawText: bool = False, initialX=None, initialY=None, calculateWidth: bool = False):
        """
        Calculate the class header position and size and display it if
        a draw is True

        Args:
            dc:
            drawText:       Set to False if you only want the returned calculations,  Ugh ...
            initialX:
            initialY:
            calculateWidth:

        Returns: tuple (x, y, w, h) = position and size of the header
        """
        dc.SetTextForeground(self._textColor)

        # x, y = self.GetPosition()
        x: int = self.topLeft.x
        y: int = self.topLeft.y

        if initialX is not None:
            x = initialX
        if initialY is not None:
            y = initialY

        w: int = self.size.width
        if calculateWidth is True:
            w = 0
        #
        # The margin we want above and below the text in the class header
        #
        headerMargin: int = cast(Size, dc.GetTextExtent("*")).height // 2
        #
        drawingYOffset: int = 0
        drawingYOffset += headerMargin

        nameWidth: int = self._drawClassName(dc, drawText, drawingYOffset, w, x, y)

        if calculateWidth is True:
            w = max(nameWidth, w)
        drawingYOffset += self.textHeight(dc, self.pyutClass.name)
        drawingYOffset += headerMargin
        #
        # Draw the stereotype value
        #
        stereotype: PyutStereotype = self.pyutClass.stereotype

        if self.pyutClass.displayStereoType is True and stereotype is not None and stereotype != PyutStereotype.NO_STEREOTYPE:
            stereoTypeValue: str = f'<<{stereotype.value}>>'
        else:
            stereoTypeValue = ''
        # Draw the stereotype
        stereoTypeValueWidth = self.textWidth(dc, stereoTypeValue)
        if drawText is True:
            dc.DrawText(stereoTypeValue, x + (w - stereoTypeValueWidth) // 2, y + drawingYOffset)

        if calculateWidth is True:
            w = max(stereoTypeValueWidth, w)
        drawingYOffset += self.textHeight(dc, str(stereoTypeValue))
        drawingYOffset += headerMargin

        # Return sizes
        # return x, y, w, heightOffset

        return drawingYOffset, w

    def _drawClassName(self, dc: MemoryDC, draw: bool, heightOffset: int, w: int, x: int, y: int):
        """

        Args:
            dc:
            draw:
            heightOffset:  offset from top of shape
            w:  Shape width
            x:  Shape top left X
            y:  Shape top left Y

        Returns:

        """
        # draw a pyutClass name
        # dc.SetFont(self._nameFont)
        dc.SetFont(self._defaultFont)
        className: str = self.pyutClass.name

        #
        # Draw the class name
        nameWidth: int = self.textWidth(dc, className)
        if draw:
            nameX: int = x + (w - nameWidth) // 2
            nameY: int = y + heightOffset

            dc.DrawText(className, nameX, nameY)
        return nameWidth

    def _drawClassFields(self, dc, draw: bool = False, initialX=None, initialY=None, calculateWidth: bool = False):
        """
        Calculate the class fields position and size and display it if
        a draw is True

        Args:
            dc:
            draw:
            initialX:
            initialY:
            calculateWidth:

        Returns: A tuple (x, y, w, h) = position and size of the field
        """
        # dc.SetFont(self._defaultFont)
        # dc.SetTextForeground(self._textColor)

        # x, y = self.GetPosition()
        x: int = self.topLeft.x
        y: int = self.topLeft.y

        if initialX is not None:
            x = initialX
        if initialY is not None:
            y = initialY
        w = self._width
        h = 0
        if calculateWidth:
            w = 0

        # Define the space between the text and the line
        # textHeightMargin: int = dc.GetTextExtent("*")[1] // 2
        textHeightMargin: int = cast(Size, dc.GetTextExtent("*")).height // 2

        pyutClass: PyutClass = self.pyutClass

        # Add space
        if len(pyutClass.fields) > 0:
            h += textHeightMargin

        # Draw pyutClass fields
        # This code depends on excellent string representations of fields
        # Provided by the fields __str__() methods
        #
        if pyutClass.showFields is True:
            for field in pyutClass.fields:
                if draw is True:
                    dc.DrawText(str(field), x + MARGIN, y + h)
                if calculateWidth is True:
                    w = max(w, self.textWidth(dc, str(field)))      # Must be good __str__()

                h += self.textHeight(dc, str(field))                # Must be good __str__()

        # Add space
        if len(pyutClass.fields) > 0:
            h += textHeightMargin

        # Return sizes
        return x, y, w, h

    def _drawClassMethods(self, dc, initialY=None) -> Tuple[int, int, int, int]:
        """
        Calculate the class methods position and size and display it if
        a showMethods is True

        Args:
            dc:
            initialY:

        Returns: tuple (x, y, w, h) which is position and size of the method's portion of the OglClass
        """

        # dc.SetFont(self._defaultFont)
        # dc.SetTextForeground(self._textColor)

        # x, y = self.GetPosition()
        x: int = self.topLeft.x
        y: int = self.topLeft.y

        if initialY is not None:
            y = initialY
        w: int = 0
        h: int = 0

        # Define the space between the text and the line
        # lth = dc.GetTextExtent("*")[1] // 2
        lth: int = cast(Size, dc.GetTextExtent("*")).height // 2
        # Add space
        pyutClass: PyutClass = self.pyutClass
        if len(pyutClass.methods) > 0:
            h += lth

        # draw pyutClass methods
        self.logger.debug(f"showMethods => {pyutClass.showMethods}")
        if pyutClass.showMethods is True:
            for method in pyutClass.methods:
                if self._eligibleToDraw(pyutClass=pyutClass, pyutMethod=method) is True:

                    self._drawMethod(dc, method, pyutClass, x, y, h)

                    pyutMethod: PyutMethod = cast(PyutMethod, method)
                    if pyutClass.displayParameters == PyutDisplayParameters.WITH_PARAMETERS or self._preferences.showParameters is True:
                        w = max(w, self.textWidth(dc, str(pyutMethod.methodWithParameters())))
                    else:
                        w = max(w, self.textWidth(dc, str(pyutMethod.methodWithoutParameters())))
                    h += self.textHeight(dc, str(method))

        # Add space
        if len(pyutClass.methods) > 0:
            h += lth

        # Return sizes
        return x, y, w, h

    def _drawMethod(self, dc: MemoryDC, pyutMethod: PyutMethod, pyutClass: PyutClass, x: int, y: int, h: int):
        """
        If the preference is not set at the individual class level, then defer to global preference; Otherwise,
        respect the class level preference

        Args:
            dc:
            pyutMethod:
            pyutClass:
            x:
            y:
            h:
        """
        self.logger.debug(f'{pyutClass.displayParameters=} - {self._preferences.showParameters=}')
        dc.SetTextForeground(self._textColor)
        if pyutClass.displayParameters == PyutDisplayParameters.UNSPECIFIED:
            if self._preferences.showParameters is True:
                dc.DrawText(pyutMethod.methodWithParameters(), x + MARGIN, y + h)
            else:
                dc.DrawText(pyutMethod.methodWithoutParameters(), x + MARGIN, y + h)
        elif pyutClass.displayParameters == PyutDisplayParameters.WITH_PARAMETERS:
            self.logger.info(f'{x=} {y=} {h=}')
            try:
                dc.DrawText(pyutMethod.methodWithParameters(), x + MARGIN, y + h)
            except TypeError as te:
                self.logger.error(f'[te=')

        elif pyutClass.displayParameters == PyutDisplayParameters.WITHOUT_PARAMETERS:
            try:
                dc.DrawText(pyutMethod.methodWithoutParameters(), x + MARGIN, y + h)
            except TypeError as te:
                self.logger.error(f'[te=')
        else:
            assert False, 'Internal error unknown pyutMethod parameter display type'

    def _eligibleToDraw(self, pyutClass: PyutClass, pyutMethod: PyutMethod):
        """
        Is it one of those 'special' dunder methods?

        Args:
            pyutClass: The class we need to check
            pyutMethod: The particular method we are asked about

        Returns: `True` if we can draw it, `False` if we should not
        """

        ans: bool = True

        methodName: str = pyutMethod.name
        if methodName == CONSTRUCTOR_NAME:
            ans = self._checkConstructor(pyutClass=pyutClass)
        elif methodName.startswith(DUNDER_METHOD_INDICATOR) and methodName.endswith(DUNDER_METHOD_INDICATOR):
            ans = self._checkDunderMethod(pyutClass=pyutClass)

        return ans

    def _checkConstructor(self, pyutClass: PyutClass) -> bool:
        """
        If class property is UNSPECIFIED, defer to the global value; otherwise check the local value

        Args:
            pyutClass: The specified class to check

        Returns: Always `True` unless the specific class says `False` or class does not care then returns
        `False` if the global value says so
        """
        ans: bool = self._allowDraw(classProperty=pyutClass.displayConstructor, globalValue=self._preferences.displayConstructor)

        return ans

    def _checkDunderMethod(self, pyutClass: PyutClass):
        """
        If class property is UNSPECIFIED, defer to the global value; otherwise check the local value

        Args:
            pyutClass: The specified class to check

        Returns: Always `True` unless the specific class says `False` or class does not care then returns
        `False` if the global value says so
        """
        ans: bool = self._allowDraw(classProperty=pyutClass.displayDunderMethods, globalValue=self._preferences.displayDunderMethods)

        return ans

    def _allowDraw(self, classProperty: PyutDisplayMethods, globalValue: bool) -> bool:
        ans: bool = True

        if classProperty == PyutDisplayMethods.UNSPECIFIED:
            if globalValue is False:
                ans = False
        else:
            if classProperty == PyutDisplayMethods.DO_NOT_DISPLAY:
                ans = False

        return ans

    def _isSameName(self, other) -> bool:

        ans: bool = False
        selfPyutObj:  PyutObject = self.pyutClass
        otherPyutObj: PyutObject = other.pyutClass

        if selfPyutObj.name == otherPyutObj.name:
            ans = True
        return ans

    def _isSameId(self, other):

        ans: bool = False
        if self.id == other.id:
            ans = True
        return ans

    def _startClipping(self, dc: DC):
        """
        Convenience method

        Args:
            dc:
        """

        w: int = round(self.GetWidth())
        h: int = round(self.GetHeight())
        x: int = self.topLeft.x
        y: int = self.topLeft.y

        dc.SetClippingRegion(x, y, w, h)

    def _endClipping(self, dc: DC):
        """
        Convenience method

        Args:
            dc:
        """
        dc.DestroyClippingRegion()

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        selfName: str = self.pyutClass.name
        modelId:  int = self.pyutClass.id
        return f'OglClass.{selfName} modelId: {modelId}'

    def __eq__(self, other) -> bool:

        if isinstance(other, UmlClass):
            if self._isSameName(other) is True and self._isSameId(other) is True:
                return True
            else:
                return False
        else:
            return False

    def __hash__(self):

        selfPyutObj:  PyutObject = self.pyutClass

        return hash(selfPyutObj.name) + hash(self.id)
