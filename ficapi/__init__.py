"""Flexible InterConnect API Access Module

This module is a Python library that provides API access functions
for Flexible InterConnect, a network service of NTT Communications.

It has functions to automatically acquire a authentication token
(reuse it within the expiration date, and reacquire when expire),
API access with parameters from JSON files or DICT,
and the ability to specify resource IDs by resource name.
"""
from ficapi.ficapi import FicAPI
from ficapi.playbook import Playbook, PlaybookParameter, InvalidMethod
from ficapi.mycipher import MyCipher, PasswordNotSet, DecryptionError
