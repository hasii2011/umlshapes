from typing import cast

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine


class PubSubMixin:
    """
    Exposes a write only mechanism to insert the UML publisher/subscribe
    engine into a component
    """
    def __init__(self):
        self._umlPubSubEngine: UmlPubSubEngine = cast(UmlPubSubEngine, None)

    def _setUmlPubSubEngine(self, umlPubSubEngine: UmlPubSubEngine):
        self._umlPubSubEngine = umlPubSubEngine

    # noinspection PyTypeChecker
    umlPubSubEngine = property(fget=None, fset=_setUmlPubSubEngine)
