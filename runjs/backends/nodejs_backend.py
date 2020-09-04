# -*- coding: utf-8 -*-
import logging

from .abstract import AbstractBackend

logger = logging.getLogger(__name__)

__all__ = ['NodeJSBackend', ]


class NodeJSBackend(AbstractBackend):
    """ Backend class for Nodejs """
    logger = logging.getLogger(__name__)

    def run(self, func=None, fargs=[]):
        pass
