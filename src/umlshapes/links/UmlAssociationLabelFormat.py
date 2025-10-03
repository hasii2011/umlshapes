
from typing import List

from enum import Enum

from umlshapes.lib.ogl import FORMAT_CENTRE_HORIZ
from umlshapes.lib.ogl import FORMAT_CENTRE_VERT
from umlshapes.lib.ogl import FORMAT_NONE
from umlshapes.lib.ogl import FORMAT_SIZE_TO_CONTENTS


class UmlAssociationLabelFormat(Enum):
    # noinspection SpellCheckingInspection
    """
    Types of formatting: can be combined in a bit list

        FORMAT_NONE = 0               # Left justification
        FORMAT_CENTRE_HORIZ = 1       # Centre horizontally
        FORMAT_CENTRE_VERT = 2        # Centre vertically
        FORMAT_SIZE_TO_CONTENTS = 4   # Resize shape to contents
    """
    FORMAT_NONE              = 'No Format'
    FORMAT_CENTER_HORIZONTAL = 'Center Horizontal'
    FORMAT_CENTER_VERTICAL   = 'Center Vertical'
    FORMAT_SIZE_TO_CONTENTS  = 'Format Size To Contents'
    NOT_SET = 'Not Set'

    @classmethod
    def toWxFormat(cls, values: str) -> int:
        """

        Args:
            values:  Comma delimited string

        Returns:  The wxPython bit map to format ogl.Shape text
        """
        umlValues: List[str] = values.split(',')
        bitwiseValue: int = 0
        if  UmlAssociationLabelFormat.FORMAT_NONE.value in umlValues:
            bitwiseValue |= FORMAT_NONE
        if UmlAssociationLabelFormat.FORMAT_CENTER_HORIZONTAL.value in umlValues:
            bitwiseValue |= FORMAT_CENTRE_HORIZ
        if UmlAssociationLabelFormat.FORMAT_CENTER_VERTICAL.value in umlValues:
            bitwiseValue |= FORMAT_CENTRE_VERT
        if UmlAssociationLabelFormat.FORMAT_SIZE_TO_CONTENTS.value in umlValues:
            bitwiseValue |= FORMAT_SIZE_TO_CONTENTS

        return bitwiseValue

    @classmethod
    def toDelimitedString(cls, formatMode: int) -> str:
        """
        umllinks
        umlshapes
        Args:
            formatMode:

        Returns: A comma delimited string

        """
        umlValues: str = ''

        if formatMode == FORMAT_NONE:
            umlValues = f'{UmlAssociationLabelFormat.FORMAT_NONE.value}'
        else:
            if cls.isFormatModeSet(wxMode=formatMode, wxValue=FORMAT_CENTRE_HORIZ):
                umlValues = f'{umlValues},{UmlAssociationLabelFormat.FORMAT_CENTER_HORIZONTAL.value}'
            if cls.isFormatModeSet(wxMode=formatMode, wxValue=FORMAT_CENTRE_VERT):
                umlValues = f'{umlValues},{UmlAssociationLabelFormat.FORMAT_CENTER_VERTICAL.value}'
            if cls.isFormatModeSet(wxMode=formatMode, wxValue=FORMAT_SIZE_TO_CONTENTS):
                umlValues = f'{umlValues},{UmlAssociationLabelFormat.FORMAT_SIZE_TO_CONTENTS.value}'

        umlValues = umlValues.strip(',')
        return umlValues

    @classmethod
    def isFormatModeSet(cls, wxMode: int, wxValue: int) -> bool:
        if wxMode & wxValue:
            return True
        else:
            return False

    @classmethod
    def clearMode(cls, wxMode: int, wxValue: int ) -> int:
        updatedValue = wxValue ^ wxMode  # turn it off

        return updatedValue

    @classmethod
    def setMode(cls, wxMode: int, wxValue) -> int:
        updatedValue: int = wxValue | wxMode  # turn it on

        return updatedValue

    def __str__(self) -> str:
        return self.value
