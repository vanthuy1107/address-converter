from .converter_2025 import convert_address_2025
from .converter_legacy import convert_address_legacy
from enum import Enum
from typing import Union


class ConvertMode(Enum):
    CONVERT_2025 = "CONVERT_2025"  # From LEGACY (63-province) → MERGER_2025 (34-province)
    CONVERT_LEGACY = "CONVERT_LEGACY"  # From MERGER_2025 (34-province) → LEGACY (63-province)

    @classmethod
    def available(cls, value=False):
        attrs = list(cls)
        if value:
            attrs = [a.value for a in attrs]
        return attrs


def convert_address(address: str, mode: Union[str, ConvertMode]=ConvertMode.CONVERT_2025):
    '''
    Converts an address between 63-province (legacy) and 34-province (post-2025) formats.

    :param address: Best format *"(street), ward, (district), province"*. Case is ignored, accents are usually ignored except in rare cases.
    :param mode: `'CONVERT_2025'` (old→new) or `'CONVERT_LEGACY'` (new→old).
    :return: AdminUnit object.
    '''

    if mode in [ConvertMode.CONVERT_2025, ConvertMode.CONVERT_2025.value]:
        return convert_address_2025(address)
    if mode in [ConvertMode.CONVERT_LEGACY, ConvertMode.CONVERT_LEGACY.value]:
        return convert_address_legacy(address)
    raise Exception(f"Invalid mode. Available modes are {ConvertMode.available(value=True)}.")