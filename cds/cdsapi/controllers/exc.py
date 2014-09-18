import json
import sys


class BaseException(Exception):
    """An error occurred."""
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message or self.__class__.__doc__


class OpenstackCommunicationError(BaseException):
    """openstack is Not Commnunication"""
