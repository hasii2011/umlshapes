#!/usr/bin/env python

from typing import List

from logging import Logger
from logging import getLogger

from wx import App
from wx import BLACK
from wx import BLACK_BRUSH
from wx import BLACK_PEN
from wx import BLUE
from wx import BLUE_BRUSH
from wx import BRUSHSTYLE_SOLID
from wx import Brush
from wx import CYAN_BRUSH
from wx import ClientDC
from wx import DEFAULT_FRAME_STYLE
from wx import FONTFAMILY_SWISS
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_NORMAL
from wx import FRAME_FLOAT_ON_PARENT
from wx import Font
from wx import GREEN_BRUSH
from wx import GREEN_PEN
from wx import HORIZONTAL
from wx import LIGHT_GREY_BRUSH
from wx import PENSTYLE_DOT
from wx import Pen
from wx import RED
from wx import RED_BRUSH
from wx import WHITE_BRUSH

from wx.lib.ogl import ARROW_ARROW
from wx.lib.ogl import CONSTRAINT_MIDALIGNED_BOTTOM
from wx.lib.ogl import CircleShape
from wx.lib.ogl import CompositeShape as OglCompositeShape
from wx.lib.ogl import Constraint
from wx.lib.ogl import Diagram
from wx.lib.ogl import FORMAT_CENTRE_HORIZ
from wx.lib.ogl import FORMAT_CENTRE_VERT
from wx.lib.ogl import FORMAT_NONE
from wx.lib.ogl import LineShape

from wx.lib.ogl import OGLInitialize
from wx.lib.ogl import DrawnShape as OglDrawnShape
from wx.lib.ogl import DividedShape as OglDividedShape
from wx.lib.ogl import PolygonShape
from wx.lib.ogl import RectangleShape
from wx.lib.ogl import Shape
from wx.lib.ogl import ShapeCanvas
from wx.lib.ogl import ShapeRegion
from wx.lib.ogl import TextShape

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from codeallybasic.UnitTestBase import UnitTestBase

from tests.ogldemonstration.MyEvtHandler import MyEvtHandler


# import images


class DrawnShape(OglDrawnShape):

    def __init__(self):

        super().__init__()
        self.SetDrawnBrush(WHITE_BRUSH)
        self.SetDrawnPen(BLACK_PEN)
        self.DrawArc((0, -10), (30, 0), (-30, 0))

        self.SetDrawnPen(Pen("#ff8030"))
        self.DrawLine((-30, 5), (30, 5))

        self.SetDrawnPen(Pen("#00ee10"))
        self.DrawRoundedRectangle((-20, 10, 40, 10), 5)

        self.SetDrawnPen(Pen("#9090f0"))
        self.DrawEllipse((-30, 25, 60, 20))

        self.SetDrawnTextColour(BLACK)
        self.SetDrawnFont(Font(8, FONTFAMILY_SWISS, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL))
        self.DrawText("DrawText", (-26, 28))

        self.SetDrawnBrush(GREEN_BRUSH)
        self.DrawPolygon([(-100, 5), (-45, 30), (-35, 20), (-30, 5)])

        self.SetDrawnPen(BLACK_PEN)
        self.DrawLines([(30, -45), (40, -45), (40, 45), (30, 45)])

        # Make sure to call CalculateSize when all drawing is done
        self.CalculateSize()


class DiamondShape(PolygonShape):
    def __init__(self, w=0.0, h=0.0):
        PolygonShape.__init__(self)
        if w == 0.0:
            w = 60.0
        if h == 0.0:
            h = 60.0

        points = [(0.0,    -h/2.0),
                  (w/2.0,  0.0),
                  (0.0,    h/2.0),
                  (-w/2.0, 0.0),
                  ]

        self.Create(points)


class RoundedRectangleShape(RectangleShape):
    def __init__(self, w=0.0, h=0.0):
        RectangleShape.__init__(self, w, h)
        self.SetCornerRadius(-0.3)


class CompositeDivisionShape(OglCompositeShape):
    def __init__(self, canvas):
        super().__init__()
        # CompositeShape.__init__(self)

        self.SetCanvas(canvas)

        # create a division in the composite
        self.MakeContainer()

        # add a shape to the original division
        shape2 = RectangleShape(40, 60)
        self.GetDivisions()[0].AddChild(shape2)

        # now divide the division so we get 2
        self.GetDivisions()[0].Divide(HORIZONTAL)

        # and add a shape to the second division (and move it to the
        # centre of the division)
        shape3 = CircleShape(40)
        shape3.SetBrush(CYAN_BRUSH)
        self.GetDivisions()[1].AddChild(shape3)
        shape3.SetX(self.GetDivisions()[1].GetX())

        for division in self.GetDivisions():
            division.SetSensitivityFilter(0)


class CompositeShape(OglCompositeShape):
    def __init__(self, canvas):
        super().__init__()
        # CompositeShape.__init__(self)

        self.SetCanvas(canvas)

        constraining_shape = RectangleShape(120, 100)
        constrained_shape1 = CircleShape(50)
        constrained_shape2 = RectangleShape(80, 20)

        constraining_shape.SetBrush(BLUE_BRUSH)
        constrained_shape2.SetBrush(RED_BRUSH)

        self.AddChild(constraining_shape)
        self.AddChild(constrained_shape1)
        self.AddChild(constrained_shape2)

        constraint = Constraint(CONSTRAINT_MIDALIGNED_BOTTOM, constraining_shape, [constrained_shape1, constrained_shape2])
        self.AddConstraint(constraint)
        self.Recompute()

        # If we don't do this, the shapes will be able to move on their
        # own, instead of moving the composite
        constraining_shape.SetDraggable(False)
        constrained_shape1.SetDraggable(False)
        constrained_shape2.SetDraggable(False)

        # If we don't do this the shape will take all left-clicks for itself
        constraining_shape.SetSensitivityFilter(0)


class DividedShape(OglDividedShape):
    def __init__(self, width, height, canvas):
        super().__init__(width, height)
        # DividedShape.__init__(self, width, height)

        region1 = ShapeRegion()
        region1.SetText('DividedShape')
        region1.SetProportions(0.0, 0.2)
        region1.SetFormatMode(FORMAT_CENTRE_HORIZ)
        self.AddRegion(region1)

        region2 = ShapeRegion()
        region2.SetText('This is Region number two.')
        region2.SetProportions(0.0, 0.3)
        region2.SetFormatMode(FORMAT_CENTRE_HORIZ | FORMAT_CENTRE_VERT)
        self.AddRegion(region2)

        region3 = ShapeRegion()
        region3.SetText('Region 3\nwith embedded\nline breaks')
        region3.SetProportions(0.0, 0.5)
        region3.SetFormatMode(FORMAT_NONE)
        self.AddRegion(region3)

        self.SetRegionSizes()
        self.ReformatRegions(canvas)

    def ReformatRegions(self, canvas=None):
        reformatNumber = 0

        if canvas is None:
            canvas = self.GetCanvas()

        dc = ClientDC(canvas)  # used for measuring

        for region in self.GetRegions():
            text = region.GetText()
            self.FormatText(dc, text, reformatNumber)
            reformatNumber += 1

    def OnSizingEndDragLeft(self, pt, x, y, keys=0, attachment=0):

        super().OnSizingEndDragLeft(pt, x, y, keys, attachment)
        self.SetRegionSizes()
        self.ReformatRegions()
        self.GetCanvas().Refresh()


class TestWindow(ShapeCanvas):
    def __init__(self, parent, log, frame):
        ShapeCanvas.__init__(self, parent)

        maxWidth  = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth//20, maxHeight//20)

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE")  # wx.WHITE)
        self.diagram = Diagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)

        self.shapes: List[Shape] = []
        self.save_gdi = []

        rRectBrush = Brush("MEDIUM TURQUOISE", BRUSHSTYLE_SOLID)

        self.MyAddShape(
            CompositeDivisionShape(self),
            270, 310, BLACK_PEN, BLUE_BRUSH, "Division"
            )

        self.MyAddShape(
            CompositeShape(self),
            100, 260, BLACK_PEN, RED_BRUSH, "Composite"
            )

        self.MyAddShape(
            CircleShape(80),
            75, 110, Pen(BLUE, 3), GREEN_BRUSH, "Circle"
            )

        self.MyAddShape(
            TextShape(120, 45),
            160, 35, GREEN_PEN, LIGHT_GREY_BRUSH, "OGL is now a\npure Python lib!"
            )

        self.MyAddShape(
            RectangleShape(85, 50),
            305, 60, BLACK_PEN, LIGHT_GREY_BRUSH, "Rectangle"
            )

        self.MyAddShape(
            DrawnShape(),
            500, 80, BLACK_PEN, BLACK_BRUSH, "DrawnShape"
            )

        # ds = self.MyAddShape(
        #     DividedShape(140, 150, self),
        #     520, 265, wx.BLACK_PEN, dsBrush, ''
        #     )

        self.MyAddShape(
            DiamondShape(90, 90),
            355, 260, Pen(BLUE, 3, PENSTYLE_DOT), RED_BRUSH, "Polygon"
            )

        self.MyAddShape(
            RoundedRectangleShape(95, 70),
            345, 145, Pen(RED, 2), rRectBrush, "Rounded Rect"
            )

        # bmp = images.Splash6.GetBitmap()
        # mask = wx.Mask(bmp, wx.BLUE)
        # bmp.SetMask(mask)
        #
        # s = ogl.BitmapShape()
        # s.SetBitmap(bmp)
        # self.MyAddShape(s, 225, 130, None, None, "Bitmap")

        # dc = wx.ClientDC(self)
        # self.PrepareDC(dc)

        for x in range(len(self.shapes)):
            fromShape = self.shapes[x]
            if x+1 == len(self.shapes):
                toShape = self.shapes[0]
            else:
                toShape = self.shapes[x+1]

            line = LineShape()
            line.SetCanvas(self)
            line.SetPen(BLACK_PEN)
            line.SetBrush(BLACK_BRUSH)
            line.AddArrow(ARROW_ARROW)
            line.MakeLineControlPoints(2)
            fromShape.AddLine(line, toShape)
            self.diagram.AddShape(line)
            line.Show(True)

    def MyAddShape(self, shape, x, y, pen, brush, text):
        # Composites have to be moved for all children to get in place
        if isinstance(shape, CompositeShape):
            dc = ClientDC(self)
            self.PrepareDC(dc)
            shape.Move(dc, x, y)
        else:
            shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        if pen:
            shape.SetPen(pen)
        if brush:
            shape.SetBrush(brush)
        if text:
            for line in text.split('\n'):
                shape.AddText(line)

        self.diagram.AddShape(shape)
        shape.Show(True)

        eventHandler: MyEvtHandler = MyEvtHandler(self.frame)
        eventHandler.SetShape(shape)
        eventHandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(eventHandler)

        self.shapes.append(shape)
        return shape

    def OnBeginDragLeft(self, x, y, keys=0):
        self.log.write("OnBeginDragLeft: %s, %s, %s\n" % (x, y, keys))

    def OnEndDragLeft(self, x, y, keys=0):
        self.log.write("OnEndDragLeft: %s, %s, %s\n" % (x, y, keys))


class OglApp(App):

    def __init__(self):

        super().__init__(redirect=False)
        self.logger: Logger = getLogger(__name__)

        # This creates some pens and brushes that the OGL library uses.
        # It should be called after the app object has been created,
        # but before OGL is used.
        OGLInitialize()
        self._frame: SizedFrame = SizedFrame(parent=None, title="Ogl Test", size=(800, 600), style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT)

        sizedPanel: SizedPanel = self._frame.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._diagramFrame = TestWindow(parent=sizedPanel, frame=self._frame, log=self.logger)
        # noinspection PyUnresolvedReferences
        self._diagramFrame.SetSizerProps(expand=True, proportion=1)

        self.SetTopWindow(self._frame)

        self._frame.CreateStatusBar()  # should always do this when there's a resize border
        self._frame.SetAutoLayout(True)
        self._frame.Show(True)

    # noinspection PyAttributeOutsideInit
    def OnInit(self):

        return True


if __name__ == '__main__':

    UnitTestBase.setUpLogging()

    testApp: OglApp = OglApp()

    testApp.MainLoop()
