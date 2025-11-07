
from typing import List
from typing import NewType

from dataclasses import dataclass

from umlshapes.types.UmlPosition import UmlPoint


@dataclass
class UmlLine:
    start: UmlPoint
    end:   UmlPoint


UmlLines = NewType('UmlLines', List[UmlLine])
