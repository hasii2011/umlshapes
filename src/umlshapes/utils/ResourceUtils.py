
from typing import cast

from logging import Logger
from logging import getLogger

from wx import FONTFAMILY_MODERN
from wx import FONTFAMILY_ROMAN
from wx import FONTFAMILY_SCRIPT
from wx import FONTFAMILY_SWISS
from wx import FONTFAMILY_TELETYPE

from wx import Font
from wx import Pen
from wx import RED
from wx import BLACK
from wx import Brush
from wx import Bitmap
from wx import FontFamily
from wx import PENSTYLE_SOLID
from wx import FONTSTYLE_NORMAL
from wx import FONTWEIGHT_NORMAL
from wx import PENSTYLE_SHORT_DASH

from umlshapes.resources.images.Display import embeddedImage as displayImage
from umlshapes.resources.images.UnSpecified import embeddedImage as unSpecifiedImage
from umlshapes.resources.images.DoNotDisplay import embeddedImage as doNotDisplayImage

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlFontFamily import UmlFontFamily


class ResourceUtils:

    clsLogger: Logger = getLogger(__name__)

    BLACK_SOLID_PEN:  Pen  = cast(Pen, None)        # noqa
    RED_SOLID_PEN:    Pen  = cast(Pen, None)        # noqa
    RED_DASHED_PEN:   Pen  = cast(Pen, None)        # noqa
    BLACK_DASHED_PEN: Pen  = cast(Pen, None)        # noqa

    DEFAULT_FONT:     Font = cast(Font, None)       # noqa

    DEFAULT_BACKGROUND_BRUSH: Brush = cast(Brush, None) # noqa

    @classmethod
    def blackSolidPen(cls) -> Pen:

        if ResourceUtils.BLACK_SOLID_PEN is None:
            ResourceUtils.BLACK_SOLID_PEN = Pen(BLACK, 1, PENSTYLE_SOLID)

        return ResourceUtils.BLACK_SOLID_PEN

    @classmethod
    def redSolidPen(cls) -> Pen:

        if ResourceUtils.RED_SOLID_PEN is None:
            ResourceUtils.RED_SOLID_PEN = Pen(RED, 1, PENSTYLE_SOLID)

        return ResourceUtils.RED_SOLID_PEN

    @classmethod
    def redDashedPen(cls) -> Pen:
        if ResourceUtils.RED_DASHED_PEN is None:
            ResourceUtils.RED_DASHED_PEN = Pen(RED, 1, PENSTYLE_SHORT_DASH)

        return ResourceUtils.RED_DASHED_PEN

    @classmethod
    def blackDashedPen(cls) -> Pen:
        if ResourceUtils.BLACK_DASHED_PEN is None:
            ResourceUtils.BLACK_DASHED_PEN = Pen(BLACK, 1, PENSTYLE_SHORT_DASH)

        return ResourceUtils.BLACK_DASHED_PEN

    @classmethod
    def defaultFont(cls) -> Font:

        if ResourceUtils.DEFAULT_FONT is None:
            fontSize:      int           = UmlPreferences().textFontSize
            fontFamilyStr: UmlFontFamily = UmlPreferences().textFontFamily
            fontFamily:    int           = ResourceUtils.umlFontFamilyToWxFontFamily(fontFamilyStr)

            ResourceUtils.DEFAULT_FONT = Font(fontSize, fontFamily, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL)
            ResourceUtils.clsLogger.debug(f'{ResourceUtils.DEFAULT_FONT=}')

        return ResourceUtils.DEFAULT_FONT

    @classmethod
    def backGroundBrush(cls) -> Brush:

        if ResourceUtils.DEFAULT_BACKGROUND_BRUSH is None:
            backGroundColor: UmlColor = UmlPreferences().backGroundColor
            brush:           Brush    = Brush()
            brush.SetColour(UmlColor.toWxColor(backGroundColor))

            ResourceUtils.DEFAULT_BACKGROUND_BRUSH = brush

        return ResourceUtils.DEFAULT_BACKGROUND_BRUSH

    @classmethod
    def umlFontFamilyToWxFontFamily(cls, enumValue: UmlFontFamily) -> FontFamily:

        if enumValue == UmlFontFamily.SWISS:
            return FONTFAMILY_SWISS
        elif enumValue == UmlFontFamily.MODERN:
            return FONTFAMILY_MODERN
        elif enumValue == UmlFontFamily.ROMAN:
            return FONTFAMILY_ROMAN
        elif enumValue == UmlFontFamily.SCRIPT:
            return FONTFAMILY_SCRIPT
        elif enumValue == UmlFontFamily.TELETYPE:
            return FONTFAMILY_TELETYPE
        else:
            assert False, 'Developer error'

    @classmethod
    def displayIcon(cls) -> Bitmap:
        bmp: Bitmap = displayImage.GetBitmap()
        return bmp

    @classmethod
    def doNotDisplayIcon(cls) -> Bitmap:
        bmp: Bitmap = doNotDisplayImage.GetBitmap()
        return bmp

    @classmethod
    def unspecifiedDisplayIcon(cls) -> Bitmap:
        bmp: Bitmap = unSpecifiedImage.GetBitmap()
        return bmp
