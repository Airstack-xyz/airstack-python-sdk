"""
Module: constant.py
Description: This module contains the constant used in airstack sdk.
"""

from enum import Enum


class SocialsDappName(Enum):
    LENS = "lens"
    FARCASTER = "farcaster"


class TransferType(Enum):
    SEND = "send"
    RECEIVED = "received"


class ChainType(Enum):
    ETH = "ethereum"
    POLYGON = "polygon"
    BASE = "base"


class AirstackConstants:
    """Class for keeping constants
    """
    API_ENDPOINT_PROD = 'https://api.airstack.xyz/gql'
    API_TIMEOUT = 60
    SUCCESS_STATUS_CODE = 200
    UNPROCESSABLE_STATUS_CODE = 422
