
from abc import ABC
from abc import abstractmethod


class IApplicationAdapter(ABC):
    """
    This interface must be implemented by the wrapper application
    """
    def __init__(self):
        pass

    @abstractmethod
    def updateApplicationStatus(self, message: str):
        """
        This method should update the wrapper application status bar

        Args:
            message:   The message a frame wants displayed on the application status bar
        """
        pass
