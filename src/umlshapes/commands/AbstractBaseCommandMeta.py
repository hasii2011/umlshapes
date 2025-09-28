
from abc import ABCMeta

from umlshapes.commands.BaseCommand import BaseCommand
"""
I have no idea why this works:

https://stackoverflow.com/questions/50085658/inheriting-from-both-abc-and-django-db-models-model-raises-metaclass-exception
"""

class AbstractBaseCommandMeta(ABCMeta, type(BaseCommand)):      # type: ignore
    pass
