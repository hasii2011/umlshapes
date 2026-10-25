from enum import Enum


class SDFragmentOperator(Enum):
    """
    UML 2.5.1 Section 17.6.3 interaction operators for Combined Fragments.
    """

    ALT      = 'alt'
    OPT      = 'opt'
    LOOP     = 'loop'
    PAR      = 'par'
    BREAK    = 'break'
    CRITICAL = 'critical'
