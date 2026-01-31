"""
Convert address from new (34-province, post-2025) format to old (63-province, legacy) format.
Uses reverse lookups built from converter_2025.json.
"""
from pathlib import Path

from ..parser import parse_address, ParseMode
from ..parser.objects import AdminUnit

MODULE_DIR = Path(__file__).parent.parent

# Reuse converter_2025 data; we build reverse lookups
import json
with open(MODULE_DIR / 'data/converter_2025.json', 'r', encoding='utf-8') as f:
    _converter_data = json.load(f)

DICT_PROVINCE = _converter_data['DICT_PROVINCE']
DICT_PROVINCE_WARD_NO_DIVIDED = _converter_data['DICT_PROVINCE_WARD_NO_DIVIDED']
DICT_PROVINCE_WARD_DIVIDED = _converter_data['DICT_PROVINCE_WARD_DIVIDED']


def _parse_old_key(old_province_district_ward_key: str, old_province_candidates: list) -> tuple:
    """
    Split old_province_district_ward_key into (old_province_key, old_district_key, old_ward_key).
    old_province_candidates is list of possible old province keys (e.g. from DICT_PROVINCE[new_province_key]).
    """
    for old_prov in old_province_candidates:
        prefix = old_prov + '_'
        if old_province_district_ward_key.startswith(prefix):
            remainder = old_province_district_ward_key[len(prefix):]
            # remainder is "district_ward" or "district_" (ward can be empty in special zones)
            parts = remainder.split('_', 1)
            old_district_key = parts[0] if parts else ''
            old_ward_key = parts[1] if len(parts) > 1 else ''
            return (old_prov, old_district_key, old_ward_key)
    return (None, None, None)


def _build_reverse_ward_divided():
    """
    Build reverse map: (new_province_key, new_ward_key) -> list of old_province_district_ward_key.
    When one old ward was split into multiple new wards, we map back from new_ward_key to that old key.
    """
    reverse = {}
    for new_prov_key, old_to_new_wards in DICT_PROVINCE_WARD_DIVIDED.items():
        for old_key, new_wards in old_to_new_wards.items():
            for w in new_wards:
                new_ward_key = w.get('newWardKey')
                if not new_ward_key:
                    continue
                k = (new_prov_key, new_ward_key)
                if k not in reverse:
                    reverse[k] = []
                reverse[k].append((old_key, w.get('isDefaultNewWard', False)))
    return reverse


# Build once at module load
_REVERSE_WARD_DIVIDED = _build_reverse_ward_divided()


def convert_address_legacy(address: str) -> AdminUnit:
    """
    Convert address from new (34-province, post-2025) format to old (63-province, legacy) format.

    :param address: str - The new address to convert (street, ward, province; no district).
    :return: AdminUnit object (legacy 63-province with district).
    """
    # Parse with FROM_2025 (34-province)
    new_unit = parse_address(address, mode=ParseMode.FROM_2025, keep_street=True, level=2)
    if not new_unit or not getattr(new_unit, 'province_key', None):
        return new_unit

    new_province_key = new_unit.province_key
    new_ward_key = new_unit.ward_key
    old_province_candidates = DICT_PROVINCE.get(new_province_key, [])

    if not old_province_candidates:
        # No mapping for this new province; return new_unit as-is (no legacy equivalent)
        return new_unit

    # Prefer first old province when multiple (e.g. Cần Thơ maps from Cần Thơ + Hậu Giang)
    old_province_key = old_province_candidates[0]
    old_district_key = None
    old_ward_key = None
    old_province_district_ward_key = None

    if new_ward_key:
        # 1st: WARD_NO_DIVIDED — new_ward_key -> list of old_province_district_ward_key
        ward_no_div = DICT_PROVINCE_WARD_NO_DIVIDED.get(new_province_key, {})
        old_key_list = ward_no_div.get(new_ward_key, [])

        for ok in old_key_list:
            prov, dist, ward = _parse_old_key(ok, old_province_candidates)
            if prov is not None:
                old_province_key = prov
                old_district_key = dist
                old_ward_key = ward
                old_province_district_ward_key = ok
                break

        # 2nd: WARD_DIVIDED — (new_prov, new_ward) -> list of (old_key, is_default)
        if old_province_district_ward_key is None:
            rev_list = _REVERSE_WARD_DIVIDED.get((new_province_key, new_ward_key), [])
            # Prefer default new ward when going back to old
            for ok, is_default in rev_list:
                prov, dist, ward = _parse_old_key(ok, old_province_candidates)
                if prov is not None:
                    old_province_key = prov
                    old_district_key = dist
                    old_ward_key = ward
                    if is_default:
                        break

    # Build old-format address string and parse with LEGACY
    parts = [p for p in (new_unit.street, old_ward_key, old_district_key, old_province_key) if p]
    old_address = ','.join(parts)
    level = 3 if (old_district_key and old_ward_key) else (2 if old_district_key else 1)
    old_unit = parse_address(old_address, mode=ParseMode.LEGACY, keep_street=True, level=level)
    if old_unit:
        old_unit.NewAdminUnit = new_unit
    return old_unit
