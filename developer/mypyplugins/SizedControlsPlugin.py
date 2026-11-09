"""
Mypy plugin for wx.lib.sized_controls dynamic extensions.

NOTE: This plugin is temporarily hosted here in the developer directory.
Future plan: Move this plugin into the shared `buildlackey` toolkit
(e.g., buildlackey.mypy.sized_controls) so it can be shared across all
wxPython repositories via a single `.mypi.ini` plugin reference without
duplicating files across projects.

Adds dynamically monkey-patched methods (such as SetSizerProps and GetSizerProps)
to wx.core.Window and wx.core.SizerItem.
"""
from typing import Callable
from typing import Optional
from mypy.plugin import Plugin
from mypy.plugin import ClassDefContext
from mypy.plugins.common import add_method_to_class
from mypy.nodes import Argument
from mypy.nodes import Var
from mypy.nodes import ARG_STAR
from mypy.nodes import ARG_STAR2
from mypy.types import AnyType
from mypy.types import TypeOfAny
from mypy.types import NoneType
from mypy.types import Instance

TARGET_WINDOW_CLASS: str = 'wx.core.Window'
TARGET_SIZER_ITEM_CLASS: str = 'wx.core.SizerItem'


class SizedControlsPlugin(Plugin):
    """
    Plugin to teach mypy about monkey-patched methods from wx.lib.sized_controls.
    """

    def get_customize_class_mro_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        """
        Hook called before class bodies are analyzed to customize class definitions.
        """
        if fullname == TARGET_WINDOW_CLASS:
            return self._customizeWindowClass
        if fullname == TARGET_SIZER_ITEM_CLASS:
            return self._customizeSizerItemClass
        return None

    def _customizeWindowClass(self, ctx: ClassDefContext):
        """
        Injects sized_controls methods onto wx.core.Window.
        """
        anyType: AnyType = AnyType(TypeOfAny.special_form)
        starArgs: Argument = Argument(
            variable=Var('args', anyType),
            type_annotation=anyType,
            initializer=None,
            kind=ARG_STAR,
        )
        starKwargs: Argument = Argument(
            variable=Var('kwargs', anyType),
            type_annotation=anyType,
            initializer=None,
            kind=ARG_STAR2,
        )
        intType: Instance = ctx.api.named_type('builtins.int')

        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='SetSizerProps',
            args=[starArgs, starKwargs],
            return_type=NoneType(),
        )
        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='GetSizerProps',
            args=[],
            return_type=anyType,
        )
        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='SetSizerProp',
            args=[starArgs, starKwargs],
            return_type=NoneType(),
        )
        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='SetDefaultSizerProps',
            args=[],
            return_type=NoneType(),
        )
        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='GetDefaultHIGBorder',
            args=[],
            return_type=intType,
        )
        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='GetDialogBorder',
            args=[],
            return_type=intType,
        )

    def _customizeSizerItemClass(self, ctx: ClassDefContext):
        """
        Injects sized_controls methods onto wx.core.SizerItem.
        """
        anyType: AnyType = AnyType(TypeOfAny.special_form)
        starArgs: Argument = Argument(
            variable=Var('args', anyType),
            type_annotation=anyType,
            initializer=None,
            kind=ARG_STAR,
        )
        starKwargs: Argument = Argument(
            variable=Var('kwargs', anyType),
            type_annotation=anyType,
            initializer=None,
            kind=ARG_STAR2,
        )
        intType: Instance = ctx.api.named_type('builtins.int')

        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='SetHGrow',
            args=[starArgs, starKwargs],
            return_type=NoneType(),
        )
        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='GetHGrow',
            args=[],
            return_type=intType,
        )
        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='SetVGrow',
            args=[starArgs, starKwargs],
            return_type=NoneType(),
        )
        add_method_to_class(
            api=ctx.api,
            cls=ctx.cls,
            name='GetVGrow',
            args=[],
            return_type=intType,
        )


def plugin(version: str) -> type[Plugin]:
    """
    Entry point for the mypy plugin.
    """
    return SizedControlsPlugin
