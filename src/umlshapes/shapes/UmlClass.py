
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

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
from pyutmodelv2.PyutMethod import PyutMethods
from pyutmodelv2.PyutField import PyutFields

from pyutmodelv2.enumerations.PyutStereotype import PyutStereotype
from pyutmodelv2.enumerations.PyutDisplayMethods import PyutDisplayMethods
from pyutmodelv2.enumerations.PyutDisplayParameters import PyutDisplayParameters

from umlshapes.UmlUtils import UmlUtils

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.links.UmlAssociation import UmlAssociation
from umlshapes.links.UmlLink import UmlLink

from umlshapes.types.Common import LeftCoordinate
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.mixins.IDMixin import IDMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin
from umlshapes.mixins.ControlPointMixin import ControlPointMixin

if TYPE_CHECKING:
    from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

DUNDER_METHOD_INDICATOR: str = '__'
CONSTRUCTOR_NAME:        str = '__init__'


class UmlClass(ControlPointMixin, RectangleShape, TopLeftMixin, IDMixin):
    """

    """

    def __init__(self, pyutClass: PyutClass = None, size: UmlDimensions = None):
        """]
        Args:
            pyutClass:   A PyutClass Object
            size:       An initial size that overrides the default
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
        TopLeftMixin.__init__(self, umlShape=self, width=classSize.width, height=classSize.height)
        IDMixin.__init__(self, umlShape=self)

        self.logger: Logger = getLogger(__name__)

        classBackgroundColor: UmlColor = self._preferences.classBackGroundColor
        backgroundColor:      Colour   = Colour(UmlColor.toWxColor(classBackgroundColor))

        self.SetBrush(Brush(backgroundColor))
        self.SetFont(UmlUtils.defaultFont())

        umlTextColor:       UmlColor = self._preferences.classTextColor
        self._textColor:    Colour   = Colour(UmlColor.toWxColor(umlTextColor))
        self._defaultFont:  Font     = UmlUtils.defaultFont()
        self._textHeight:   int      = cast(int, None)
        self._margin:       int      = self._preferences.classTextMargin

        self.SetDraggable(drag=True)
        self.SetCentreResize(False)

    @property
    def pyutClass(self) -> PyutClass:
        """

        Returns:  The associated model class
        """
        return self._pyutClass

    @pyutClass.setter
    def pyutClass(self, pyutClass: PyutClass):
        self._pyutClass = pyutClass

    @property
    def umlFrame(self) -> 'ClassDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'ClassDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def selected(self) -> bool:
        return self.Selected()

    @selected.setter
    def selected(self, select: bool):
        self.Select(select=select)

    def addLink(self, umlLink: UmlLink, destinationClass: 'UmlClass'):

        self.AddLine(line=umlLink, other=destinationClass)

        if isinstance(umlLink, UmlAssociation):
            umlLink.createAssociationLabels()

    def OnDraw(self, dc: MemoryDC):

        super().OnDraw(dc)

        w: int = self.size.width
        leftCoordinate: LeftCoordinate = self._computeTopLeft()
        x: int = leftCoordinate.x
        y: int = leftCoordinate.y

        dc.SetFont(self._defaultFont)
        dc.SetTextForeground(self._textColor)
        #
        # Define the margin between draw separator lines and individual text lines
        #
        if self._textHeight is None:
            self._textHeight = self._determineTextHeight(dc)  + self._preferences.lineHeightAdjustment

        # drawing is restricted in the specified region of the device
        self._startClipping(dc=dc, leftX=x, leftY=y)
        drawingYOffset = self._drawClassHeader(dc=dc, leftX=x, leftY=y, shapeWidth=w)

        # noinspection PySimplifyBooleanCheck
        if self.pyutClass.showFields is True:
            dc.DrawLine(x, y + drawingYOffset, x + w, y + drawingYOffset)
            drawingYOffset = self._drawClassFields(dc, leftX=x, leftY=y, startYOffset=drawingYOffset)

        dc.DrawLine(x, y + drawingYOffset, x + w, y + drawingYOffset)

        # noinspection PySimplifyBooleanCheck
        if self.pyutClass.showMethods is True:
            self._drawClassMethods(dc=dc, leftX=x, leftY=y, startYOffset=drawingYOffset)

        self._endClipping(dc=dc)

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

    def autoSize(self):
        """
        Adjust the shape to a width and height accommodates the widest displayable method
        and the height to accommodate all the displayable fields and methods
        """
        savePosition: UmlPosition = self.position

        umlFrame:    UmlFrame = self.GetCanvas()
        dc:          ClientDC = ClientDC(umlFrame)
        shapeHeight: int      = self._calculateMaxShapeHeight()
        shapeWidth:  int      = self._calculateMaxShapeWidth(dc)

        shapeSize:   UmlDimensions = UmlDimensions(
            width=shapeWidth,
            height=shapeHeight
        )
        self.size     = shapeSize
        self.position = savePosition
        self.Select(select=False)
        umlFrame.refresh()

    def textWidth(self, dc: DC, text: str):
        """

        Args:
            dc:   Current device context
            text: The string to measure

        Returns:
        """

        size: Size = dc.GetTextExtent(text)

        return size.width

    def _drawClassHeader(self, dc: MemoryDC | ClientDC, leftX: int, leftY: int, shapeWidth: int) -> int:
        """
        Draw the class name and the stereotype name if necessary

        Args:
            dc:
            leftX
            leftY
            shapeWidth:

        Returns:  The updated y drawing position
        """
        x: int = leftX
        y: int = leftY

        headerMargin:   int = self._textHeight
        drawingYOffset: int = headerMargin

        self._drawClassName(dc, drawingYOffset, shapeWidth, x, y)
        drawingYOffset += self._textHeight

        drawingYOffset = self._drawStereotypeValue(dc=dc, leftX=leftX,
                                                   leftY=leftY,
                                                   shapeWidth=shapeWidth,
                                                   headerMargin=headerMargin,
                                                   drawingYOffset=drawingYOffset
                                                   )

        return drawingYOffset

    def _drawClassName(self, dc: MemoryDC, heightOffset: int, w: int, x: int, y: int):
        """

        Args:
            dc:
            heightOffset:  offset from top of shape
            w:  Shape width
            x:  Shape top left X
            y:  Shape top left Y
        """
        className: str = self.pyutClass.name
        #
        # Draw the class name
        nameWidth: int = self.textWidth(dc, className)
        nameX:     int = x + (w - nameWidth) // 2
        nameY:     int = y + heightOffset

        dc.DrawText(className, nameX, nameY)

    def _drawStereotypeValue(self, dc: MemoryDC, leftX: int, leftY: int, shapeWidth: int, headerMargin: int, drawingYOffset: int) -> int:
        """
        Draw the stereotype value;  If class has no stereotype, just leave a blank space

        Args:
            dc:
            leftX
            leftY
            shapeWidth:
            headerMargin:
            drawingYOffset:

        Returns:    Updated Y offset
        """
        x: int = leftX
        y: int = leftY

        stereoTypeValue:      str = self._getStereoTypeValue()
        stereoTypeValueWidth: int = self.textWidth(dc, stereoTypeValue)

        if len(stereoTypeValue) != 0:
            dc.DrawText(stereoTypeValue, x + (shapeWidth - stereoTypeValueWidth) // 2, y + drawingYOffset)

            drawingYOffset += self._textHeight

        updatedYOffset = drawingYOffset + headerMargin

        return updatedYOffset

    def _drawClassFields(self, dc: MemoryDC, leftX: int, leftY: int, startYOffset: int):
        """

        Args:
            dc:
            leftX
            leftY
            startYOffset:  Where to start drawing

        Returns:  The updated y drawing position
        """
        x:       int = leftX
        y:       int = leftY
        yOffset: int = startYOffset

        textHeight: int       = self._textHeight
        pyutClass:  PyutClass = self.pyutClass

        # Add space above
        if len(pyutClass.fields) > 0:
            yOffset += textHeight

        # This code depends on excellent string representations of fields
        # Provided by the fields __str__() methods
        #
        # noinspection PySimplifyBooleanCheck
        if pyutClass.showFields is True:
            for field in pyutClass.fields:
                fieldStr: str = str(field)      # Must be good __str__()
                dc.DrawText(fieldStr, x + self._margin, y + yOffset)
                yOffset += textHeight

        # Add space below
        if len(pyutClass.fields) > 0:
            yOffset += textHeight

        return yOffset

    def _drawClassMethods(self, dc: MemoryDC, leftX: int, leftY: int, startYOffset: int):
        """
        Display methods

        Args:
            dc:
            leftX
            leftY
            startYOffset:
        """
        yOffset:    int = startYOffset
        textHeight: int = self._textHeight

        # Add space above
        pyutClass: PyutClass = self.pyutClass
        if len(pyutClass.methods) > 0:
            yOffset += textHeight

        for method in pyutClass.methods:
            # noinspection PySimplifyBooleanCheck
            if self._eligibleToDraw(pyutClass=pyutClass, pyutMethod=method) is True:

                displayParameters: PyutDisplayParameters = pyutClass.displayParameters
                self._drawMethod(dc, method, displayParameters, leftX=leftX, leftY=leftY, startYOffset=yOffset)

                yOffset += textHeight

    def _drawMethod(self, dc: MemoryDC, pyutMethod: PyutMethod, displayParameters: PyutDisplayParameters, leftX: int, leftY: int, startYOffset: int):
        """
        If the preference is not set at the individual class level, then defer to global preference; Otherwise,
        respect the class level preference

        Args:
            dc:
            pyutMethod:
            displayParameters:
            leftX
            leftY
            startYOffset:
        """
        x: int = leftX
        y: int = leftY

        methodStr: str = self._getMethodRepresentation(pyutMethod, displayParameters)

        dc.DrawText(methodStr, x + self._margin, y + startYOffset)

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
            # noinspection PySimplifyBooleanCheck
            if globalValue is False:
                ans = False
        else:
            if classProperty == PyutDisplayMethods.DO_NOT_DISPLAY:
                ans = False

        return ans

    def _isSameName(self, other) -> bool:

        ans: bool = False
        selfPyutClass:  PyutClass = self.pyutClass
        otherPyutClass: PyutClass = other.pyutClass

        if selfPyutClass.name == otherPyutClass.name:
            ans = True
        return ans

    def _isSameId(self, other):

        ans: bool = False
        if self.id == other.id:
            ans = True
        return ans

    def _startClipping(self, dc: DC, leftX: int, leftY: int):
        """
        Convenience method

        Args:
            dc:
        """

        w: int = self.GetWidth()
        h: int = self.GetHeight()
        x: int = leftX
        y: int = leftY

        dc.SetClippingRegion(x, y, w, h)

    def _endClipping(self, dc: DC):
        """
        Convenience method

        Args:
            dc:
        """
        dc.DestroyClippingRegion()

    def _determineTextHeight(self, dc: DC):
        """
        Convenience method

        Args:
            dc:   Current device context

        Returns:
        """

        size: Size = dc.GetTextExtent('*')
        return round(size.height)

    def _getStereoTypeValue(self):
        """
        Will return a blank value if the preferences let us

        Returns:  A proper string rendition of a stereotype
        """

        stereotype: PyutStereotype = self.pyutClass.stereotype

        if self.pyutClass.displayStereoType is True and stereotype is not None and stereotype != PyutStereotype.NO_STEREOTYPE:
            stereoTypeValue: str = f'<<{stereotype.value}>>'
        else:
            stereoTypeValue = ''

        return stereoTypeValue

    def _calculateMaxShapeHeight(self) -> int:
        """
        Account for
            Margin above class name
            Class Name
            Margin above Stereotype
            Stereotype Name or place holder
            Margin below Stereotype name

        Returns: The highest based on the font set in the DC
        """

        pyutClass:        PyutClass = self.pyutClass
        singleLineHeight: int       = self._textHeight

        currentHeight: int = singleLineHeight * 5

        if len(pyutClass.fields) > 0 and pyutClass.showFields is True:
            currentHeight += singleLineHeight * 2   # Above and below margins
            currentHeight += singleLineHeight * len(pyutClass.fields)

        if len(pyutClass.methods) > 0 and pyutClass.showMethods is True:
            currentHeight += singleLineHeight * len(pyutClass.methods)

        currentHeight += singleLineHeight   # Add space after last method
        adjustedHeight: int = currentHeight - round(currentHeight * self._preferences.autoSizeHeightAdjustment)
        return adjustedHeight

    def _calculateMaxShapeWidth(self, dc: DC) -> int:

        headerWidth:  int = self._calculateMaxHeaderWidth(dc)
        fieldsWidth:  int = self._calculateMaxFieldWidth(dc)
        methodsWidth: int = self._calculateMaxMethodWidth(dc)

        currentMaxWidth: int = headerWidth

        currentMaxWidth = max(currentMaxWidth, fieldsWidth)
        currentMaxWidth = max(currentMaxWidth, methodsWidth)

        adjustedMaxWidth: int = currentMaxWidth - round(currentMaxWidth * self._preferences.autoSizeWidthAdjustment)
        return adjustedMaxWidth

    def _calculateMaxHeaderWidth(self, dc: DC) -> int:
        """
        The widest of either the method name or the stereotype
        Args:
            dc:

        Returns: The widest based on the font set in the DC
        """

        pyutClass:       PyutClass = self.pyutClass
        stereoTypeValue: str       = self._getStereoTypeValue()

        maxWidth:        int       = 0
        classNameWidth: int = self.textWidth(dc, pyutClass.name)
        stereoTypeWidth: int = self.textWidth(dc, stereoTypeValue)

        maxWidth = max(maxWidth, classNameWidth)
        maxWidth = max(maxWidth, stereoTypeWidth)

        return maxWidth

    def _calculateMaxFieldWidth(self, dc: DC) -> int:
        """
        Determines the widest.   There may be no fields are the preference may say do not display
        Args:
            dc:

        Returns: The widest based on the font set in the DC
        """

        pyutClass:  PyutClass  = self.pyutClass
        pyutFields: PyutFields = pyutClass.fields

        maxWidth: int = 0
        if len(pyutFields) > 0 and pyutClass.showFields is True:
            for pyutField in pyutFields:
                fieldStr: str = str(pyutField)
                fieldWidth: int = self.textWidth(dc, fieldStr)
                maxWidth = max(maxWidth, fieldWidth)

        return maxWidth

    def _calculateMaxMethodWidth(self, dc: DC) -> int:
        """
        Determines the widest based on eligible methods based on preferences and the individual
        class value

        Args:
            dc:

        Returns: The widest based on the font set in the DC
        """

        pyutClass:   PyutClass   = self.pyutClass
        pyutMethods: PyutMethods = pyutClass.methods

        maxWidth: int = 0
        # noinspection PySimplifyBooleanCheck
        if pyutClass.showMethods is True:
            for pyutMethod in pyutMethods:
                # noinspection PySimplifyBooleanCheck
                if self._eligibleToDraw(pyutClass=pyutClass, pyutMethod=pyutMethod) is True:
                    methodStr:   str = self._getMethodRepresentation(pyutMethod=pyutMethod, displayParameters=pyutClass.displayParameters)
                    self.logger.debug(f'{methodStr=}')
                    methodWidth: int = self.textWidth(dc=dc, text=methodStr)
                    maxWidth = max(maxWidth, methodWidth)

        return maxWidth

    # noinspection PyTypeChecker
    def _getMethodRepresentation(self, pyutMethod: PyutMethod, displayParameters: PyutDisplayParameters) -> str:
        """

        Args:
            pyutMethod:         The one we want to transform
            displayParameters:  The PyutClass value

        Returns:  The appropriate string version of a method
        """

        self.logger.debug(f'{displayParameters=} - {self._preferences.showParameters=}')

        if displayParameters == PyutDisplayParameters.UNSPECIFIED:

            if self._preferences.showParameters is True:
                methodStr: str = pyutMethod.methodWithParameters()
            else:
                methodStr = pyutMethod.methodWithoutParameters()

        elif displayParameters == PyutDisplayParameters.WITH_PARAMETERS:
            methodStr = pyutMethod.methodWithParameters()

        elif displayParameters == PyutDisplayParameters.WITHOUT_PARAMETERS:
            methodStr = pyutMethod.methodWithoutParameters()
        else:
            assert False, 'Internal error unknown pyutMethod parameter display type'

        return methodStr

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        selfName: str = self.pyutClass.name
        modelId:  int = self.pyutClass.id
        return f'UmlClass.{selfName} umlId: `{self.id}` modelId: {modelId}'

    def __eq__(self, other) -> bool:

        if isinstance(other, UmlClass):
            if self._isSameName(other) is True and self._isSameId(other) is True:
                return True
            else:
                return False
        else:
            return False

    def __hash__(self):

        selfPyutClass: PyutClass = self.pyutClass

        return hash(selfPyutClass.name) + hash(self.id)
