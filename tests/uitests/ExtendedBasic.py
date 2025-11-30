
from typing import Dict
from typing import NewType

from enum import Enum

from pathlib import Path

from json import loads as jsonLoads

from codeallybasic.Basic import Basic
from codeallybasic.Basic import RunResult


class VerifyStatus(Enum):
    SUCCESS       = 'Success'
    FAIL          = 'Fail'
    CANNOT_VERIFY = 'Cannot Verify'


EXIFTOOL:         str = 'exiftool'
META_IMAGE_SIZE:  str = 'ImageSize'
META_MEGA_PIXELS: str = 'Megapixels'
JSON_OPTION:      str = 'json'

JsonDict  = NewType('JsonDict', Dict[str, str])


class ExtendedBasic:
    """
    Placeholder so I can move these methods to codeallybasic
    """

    @classmethod
    def verifySameImage(cls, goldenImage: Path, generatedImage: Path) -> VerifyStatus:
        status: VerifyStatus = VerifyStatus.CANNOT_VERIFY

        if ExtendedBasic.cliExists(EXIFTOOL) is True:
            goldenMeta:    JsonDict = ExtendedBasic.generatedVerificationMetaData(imagePath=goldenImage)
            generatedMeta: JsonDict = ExtendedBasic.generatedVerificationMetaData(imagePath=generatedImage)
            if goldenMeta[META_IMAGE_SIZE] == generatedMeta[META_IMAGE_SIZE] and goldenMeta[META_MEGA_PIXELS] == generatedMeta[META_MEGA_PIXELS]:
                status = VerifyStatus.SUCCESS

        return status

    @classmethod
    def cliExists(cls, cliName: str) -> bool:
        """
        Runs the command with the --help option.  If the shell returns a non-zero status
        we assume the CLI is not installed

        Args:
            cliName:  The external command name

        Returns:  `True` if it does, else `False`
        """
        answer: bool = False

        result: RunResult = Basic.runCommand(programToRun=f'{cliName} --help')
        if result.returnCode == 0:
            answer = True

        return answer

    @classmethod
    def generatedVerificationMetaData(cls, imagePath: Path) -> JsonDict:
        """
        exiftool -ImageSize -Megapixels -json goldenImages/testShapes.png
        """
        cmd: str = (
            f'{EXIFTOOL} '
            f'-{META_IMAGE_SIZE} '
            f'-{META_MEGA_PIXELS} '
            f'-{JSON_OPTION} '
            f'{imagePath}'
        )
        result: RunResult = Basic.runCommand(programToRun=cmd)

        js = jsonLoads(result.stdout)[0]

        return JsonDict(js)
