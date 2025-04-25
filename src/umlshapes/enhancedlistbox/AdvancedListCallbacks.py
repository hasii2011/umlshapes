
from typing import cast

from dataclasses import dataclass

from umlshapes.enhancedlistbox.Callbacks import AddCallback
from umlshapes.enhancedlistbox.Callbacks import DownCallback
from umlshapes.enhancedlistbox.Callbacks import EditCallback
from umlshapes.enhancedlistbox.Callbacks import RemoveCallback
from umlshapes.enhancedlistbox.Callbacks import UpCallback


@dataclass
class AdvancedListCallbacks:
    addCallback:    AddCallback    = cast(AddCallback, None)
    editCallback:   EditCallback   = cast(EditCallback, None)
    removeCallback: RemoveCallback = cast(RemoveCallback, None)
    upCallback:     UpCallback     = cast(UpCallback, None)
    downCallback:   DownCallback   = cast(DownCallback, None)
