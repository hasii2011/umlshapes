from typing import cast

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine


class PubSubMixin:
    """
    Exposes a write only mechanism to insert the UML publisher/subscribe
    engine into a component
    """
    def __init__(self):
        self._umlPubSubEngine: IUmlPubSubEngine = cast(IUmlPubSubEngine, None)

    def _setUmlPubSubEngine(self, umlPubSubEngine: IUmlPubSubEngine):
        self._umlPubSubEngine = umlPubSubEngine

    # noinspection PyTypeChecker
    umlPubSubEngine = property(fget=None, fset=_setUmlPubSubEngine)
