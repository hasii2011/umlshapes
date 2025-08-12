
from typing import Dict
from typing import NewType

from logging import Logger
from logging import getLogger

from platform import platform as osPlatform

from sys import version as pythonVersion

from wx import __version__ as wxVersion

from codeallybasic.SingletonV3 import SingletonV3

from pyutmodelv2 import __version__ as dataModelVersion
from umlshapes import __version__ as __umlShapesVersion__

# noinspection PyPackageRequirements


PackageName    = NewType('PackageName', str)
PackageVersion = NewType('PackageVersion', str)

PackageVersionsMap = NewType('PackageVersionsMap', Dict[PackageName, PackageVersion])


class Versions(metaclass=SingletonV3):

    __appName__: str = 'Pyut'

    __longVersion__: str = "Python UML Diagrammer"
    __website__:     str = 'https://github.com/hasii2011/umldiagramer'

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

    @property
    def platform(self) -> str:
        return osPlatform(terse=True)

    @property
    def applicationName(self) -> str:
        return Versions.__appName__

    @property
    def applicationLongVersion(self) -> str:
        return self.__longVersion__

    @property
    def applicationWebSite(self) -> str:
        return self.__website__

    @property
    def pythonVersion(self) -> str:
        return pythonVersion.split(" ")[0]

    @property
    def wxPythonVersion(self) -> str:
        return wxVersion

    @property
    def pyutModelVersion(self) -> str:
        return dataModelVersion

    @property
    def umlShapesVersion(self) -> str:
        return __umlShapesVersion__
