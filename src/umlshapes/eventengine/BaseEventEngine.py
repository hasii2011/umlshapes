
from typing import Callable
from typing import NewType

from pubsub import pub


Topic = NewType('Topic', str)


class BaseEventEngine:
    """
    Wrapper class to hide underlying implementation
    """
    def _subscribe(self, topic: Topic, callback: Callable):
        """

        Args:
            topic:
            callback:
        """
        pub.subscribe(callback, topic)

    def _sendMessage(self, topic: Topic, **kwargs):

        pub.sendMessage(topic, **kwargs)
