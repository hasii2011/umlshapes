
from logging import Logger
from logging import getLogger

from wx import MemoryDC

from wx.lib.ogl import EllipseShape

from pyutmodelv2.PyutUseCase import PyutUseCase

from umlshapes.UmlUtils import UmlUtils

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.IDMixin import IDMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame


class UmlUseCase(ControlPointMixin,  EllipseShape, TopLeftMixin, IDMixin):

    def __init__(self, pyutUseCase: PyutUseCase = None, size: UmlDimensions = None):

        self.logger:       Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()

        if pyutUseCase is None:
            self._pyutUseCase: PyutUseCase = PyutUseCase()
        else:
            self.pyutUseCase = pyutUseCase

        super().__init__(shape=self)
        if size is None:
            useCaseSize: UmlDimensions = self._preferences.useCaseSize
        else:
            useCaseSize = size

        EllipseShape.__init__(self, w=useCaseSize.width, h=useCaseSize.height)
        TopLeftMixin.__init__(self, umlShape=self, width=useCaseSize.width, height=useCaseSize.height)
        IDMixin.__init__(self, umlShape=self)

        self.SetDraggable(drag=True)

        self.SetFont(UmlUtils.defaultFont())
        self.AddText(self.pyutUseCase.name)

    @property
    def pyutUseCase(self) -> PyutUseCase:
        return self._pyutUseCase

    @pyutUseCase.setter
    def pyutUseCase(self, value: PyutUseCase):
        self._pyutUseCase = value

    @property
    def umlFrame(self) -> UseCaseDiagramFrame:
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: UseCaseDiagramFrame):
        self.SetCanvas(frame)

    def OnDraw(self, dc: MemoryDC):
        """
        Lots of work around code on retrieved values from Shape, since it
        keeps returning floats

        Args:
            dc:
        """
        self.ClearText()
        self.AddText(self.pyutUseCase.name)

        super().OnDraw(dc)

        if self.Selected() is True:
            if self.Selected() is True:
                UmlUtils.drawSelectedEllipse(dc=dc, shape=self)
        else:
            super().OnDraw(dc)

    # This is dangerous, accessing internal stuff
    # noinspection PyProtectedMember
    # noinspection SpellCheckingInspection
    def ResetControlPoints(self):
        """
        Reset the positions of the control points (for instance, when the
        shape's shape has changed).

        Circles only have 4 control points HORIZONTAL and VERTICAL
        Bad Code depends on indices

        REFERENCE:  The parent of this method that I am deeply overriding
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

        # self._controlPoints[0]._xoffset = left
        # self._controlPoints[0]._yoffset = top

        self._controlPoints[0]._xoffset = 0
        self._controlPoints[0]._yoffset = top

        # self._controlPoints[1]._xoffset = right
        # self._controlPoints[1]._yoffset = top

        self._controlPoints[1]._xoffset = right
        self._controlPoints[1]._yoffset = 0

        # self._controlPoints[2]._xoffset = right
        # self._controlPoints[2]._yoffset = bottom

        self._controlPoints[2]._xoffset = 0
        self._controlPoints[2]._yoffset = bottom

        # self._controlPoints[3]._xoffset = left
        # self._controlPoints[3]._yoffset = bottom

        self._controlPoints[3]._xoffset = left
        self._controlPoints[3]._yoffset = 0

    def __str__(self) -> str:
        return self.pyutUseCase.name

    def __repr__(self) -> str:
        return f"[UmlUseCase - umlId: `{self.id} `modelId: '{self.pyutUseCase.id}']"
