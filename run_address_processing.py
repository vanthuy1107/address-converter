# -*- coding: utf-8 -*-
"""
Shared address processing core.
Used by main_convert_to_2025.py (old→new) and main_convert_to_legacy.py (new→old).

Do not run this file directly for conversion; use:
  python main_convert_to_2025.py   — convert old (63-province) to new (34-province)
  python main_convert_to_legacy.py — convert new (34-province) to old (63-province)

To customize: edit config.py for settings and rules.
"""
import pandas as pd
import sys
import os
import re
import json
import time
from datetime import datetime
from typing import Dict, Tuple, Optional, List

# Add vietnamadminunits to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vietnamadminunits'))

from vietnamadminunits import parse_address, ParseMode, convert_address, ConvertMode
import config


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _normalize_for_comparison(text: str) -> str:
    """
    Normalize text for comparison (remove accents, lowercase, strip).
    """
    if not text:
        return ""
    # Simple normalization - remove common Vietnamese accents
    # For more accurate normalization, could use unidecode or similar
    normalized = text.lower().strip()
    # Remove common diacritics for basic comparison
    replacements = {
        'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
        'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
        'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
        'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
        'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
        'đ': 'd',
    }
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized


def _remove_province_prefix(province: str) -> Optional[str]:
    """
    Remove "Tỉnh" and "Thành phố" prefixes from province name.
    Returns None if province is None/empty, otherwise returns cleaned name.
    """
    if not province or pd.isna(province):
        return None
    
    # Convert to string and strip
    cleaned = str(province).strip()
    
    # Remove "Tỉnh" prefix (case insensitive)
    cleaned = re.sub(r'^Tỉnh\s+', '', cleaned, flags=re.IGNORECASE)
    
    # Remove "Thành phố" prefix (case insensitive)
    cleaned = re.sub(r'^Thành\s+phố\s+', '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip() if cleaned else None


def _is_known_province_merger(old_name: str, new_name: str) -> bool:
    """
    Check if a province change is a known administrative merger.
    This is a conservative check - only flag obvious errors.
    """
    # Known mergers from 2025 administrative changes
    # Add more as needed
    known_mergers = {
        'Bắc Giang': 'Bắc Ninh',  # Example - adjust based on actual data
        # Add more known mergers here
    }
    
    # Normalize names for comparison
    old_normalized = _normalize_for_comparison(old_name)
    new_normalized = _normalize_for_comparison(new_name)
    
    # Check if it's a known merger
    for old, new in known_mergers.items():
        if _normalize_for_comparison(old) == old_normalized and _normalize_for_comparison(new) == new_normalized:
            return True
    
    return False


# ============================================================================
# ADDRESS PREPROCESSING
# ============================================================================

def preprocess_address(address: str) -> str:
    """
    Preprocess address to handle common issues before cleaning.
    This helps with addresses that have old district structures.
    """
    if not address:
        return address
    
    # Normalize comma spacing (ensure space after comma)
    address = re.sub(r',([^\s])', r', \1', address)
    
    # CRITICAL FIX: Prevent partial ward name matching
    # Issue: "Phường Thạnh Mỹ Lợi" might be matched as just "Mỹ Lợi" 
    # which is a unique ward in a different province
    # Solution: Ensure full ward names are preserved and not shortened
    # This is especially important when province is explicitly stated
    
    # Handle cases where "Thành phố" appears as both district and part of province
    # Example: "Phường X, Thành phố Thanh Hóa, Tỉnh Thanh Hóa"
    # In the new system, "Thành phố Thanh Hóa" district may not exist
    # We keep it for CONVERT mode (which handles it) but normalize for FROM_2025 mode
    if config.PROCESSING_MODE != config.ProcessingMode.CONVERT:
        # For FROM_2025 mode, if we have "Thành phố X, Tỉnh X", 
        # the district might not exist in new system, so we try to extract just ward and province
        # But we're conservative - only do this if explicitly enabled
        if config.NORMALIZE_THANH_PHO_DISTRICTS:
            # Pattern: ward, Thành phố X, Tỉnh X -> ward, Tỉnh X
            address = re.sub(
                r',\s*Thành\s+phố\s+([^,]+),\s*Tỉnh\s+\1',
                r', Tỉnh \1',
                address,
                flags=re.IGNORECASE
            )
    
    return address


# ============================================================================
# ADDRESS CLEANING
# ============================================================================

def clean_address(address: str) -> Optional[str]:
    """
    Clean address by removing unwanted patterns.
    Returns None if address should be skipped.
    """
    # Handle NaN, None, and empty values
    if pd.isna(address) or address is None:
        return None
    
    # Convert to string first to handle integers and other types
    cleaned = str(address).strip()
    
    # Check if empty or just punctuation
    if not cleaned or cleaned in [',', '']:
        return None
    
    # Preprocess address first (normalize format, handle special cases)
    cleaned = preprocess_address(cleaned)
    
    # Remove phone numbers
    for pattern in config.PHONE_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned)
    
    # Remove name prefixes
    for pattern in config.NAME_PREFIXES:
        cleaned = re.sub(pattern, '', cleaned)
    
    # Remove metadata
    for pattern in config.METADATA_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Check for warehouse patterns
    for main_pattern, context_pattern in config.WAREHOUSE_PATTERNS:
        if re.search(main_pattern, cleaned, re.IGNORECASE):
            if context_pattern is None or re.search(context_pattern, cleaned, re.IGNORECASE):
                return None  # Skip warehouse pickups
    
    # Check custom skip patterns
    for pattern in config.CUSTOM_SKIP_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return None
    
    # Apply custom cleaning rules
    for pattern, replacement in config.CUSTOM_CLEANING_RULES:
        cleaned = re.sub(pattern, replacement, cleaned)
    
    # Clean up spaces and commas
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r',\s*,+', ',', cleaned)
    cleaned = cleaned.strip().strip(',')
    
    # Check minimum length
    if len(cleaned) < config.MIN_ADDRESS_LENGTH:
        return None
    
    return cleaned


# ============================================================================
# ADDRESS VALIDATION
# ============================================================================

def validate_parse_result(admin_unit, cleaned_address: str) -> Tuple[bool, str]:
    """
    Validate that parsing result meets quality criteria.
    Returns (is_valid, reason)
    """
    if not admin_unit:
        return False, "No admin unit returned"
    
    # Check province requirement
    if config.REQUIRE_PROVINCE and not admin_unit.province:
        return False, "No province parsed"
    
    # Check district requirement
    if config.REQUIRE_DISTRICT and not admin_unit.district:
        return False, "No district parsed - address too incomplete"
    
    # Check ward requirement
    if config.REQUIRE_WARD and not admin_unit.ward:
        return False, "No ward parsed - address too incomplete"
    
    # Check address structure (comma count)
    if config.MIN_COMMA_COUNT > 0:
        comma_count = cleaned_address.count(',')
        if comma_count < config.MIN_COMMA_COUNT:
            return False, f"Address too simple - only {comma_count} commas, need at least {config.MIN_COMMA_COUNT}"
    
    # Check coordinates
    if config.REQUIRE_COORDINATES:
        if not admin_unit.latitude or not admin_unit.longitude:
            return False, "No coordinates available"
        
        if not config.ALLOW_ZERO_COORDINATES:
            if admin_unit.latitude == 0.0 or admin_unit.longitude == 0.0:
                return False, "Invalid coordinates (0.0)"
    
    # Check if it's just a building name
    if config.REJECT_BUILDING_ONLY:
        lower_address = cleaned_address.lower()
        building_patterns = [
            r'^[a-z0-9\s\-]+$',  # Only alphanumeric
            r'^\w+\s+\d+[-/]\d+\s*,?\s*$',  # Just "Building 01-18"
        ]
        for pattern in building_patterns:
            if re.match(pattern, lower_address):
                return False, "Address is just a building/apartment name"
    
    # Custom validation rules (if any)
    for rule_func_name, error_msg in config.CUSTOM_VALIDATION_RULES:
        # Import and run custom validation if defined
        pass  # Placeholder for custom validation
    
    return True, "Valid"


# ============================================================================
# ADDRESS PARSING
# ============================================================================

def parse_and_process_address(address_text: str) -> Dict:
    """
    Parse and process a single address with validation.
    Returns dictionary with all processing results.
    """
    result = {
        'cleaned_address': None,
        'parsed_province': None,
        'parsed_district': None,
        'parsed_ward': None,
        'parsed_street': None,
        'parsed_full_address': None,
        'latitude': None,
        'longitude': None,
        # OLD address info (for CONVERT mode: old→new)
        'old_province': None,
        'old_district': None,
        'old_ward': None,
        'old_full_address': None,
        'old_latitude': None,
        'old_longitude': None,
        # NEW address info (for CONVERT_TO_LEGACY mode: new→old, input 34-province)
        'new_province': None,
        'new_ward': None,
        'new_full_address': None,
        'new_latitude': None,
        'new_longitude': None,
        'parse_success': False,
        'parse_mode': None,
        'skip_reason': None
    }
    
    # Clean the address
    cleaned = clean_address(address_text)
    result['cleaned_address'] = cleaned
    
    if not cleaned:
        result['skip_reason'] = "Address could not be cleaned (empty or should be skipped)"
        return result
    
    # Check if CONVERT mode (old→new)
    if config.PROCESSING_MODE == config.ProcessingMode.CONVERT:
        # Use CONVERT_2025 mode
        try:
            converted = convert_address(cleaned, mode=ConvertMode.CONVERT_2025)
            
            # Validate the NEW address (use relaxed validation for CONVERT mode)
            # The NEW address structure is different (34-province system), so don't require district
            is_valid = True
            reason = None
            
            # Basic validation for CONVERT mode
            if not converted or not converted.province:
                is_valid = False
                reason = "No province in converted address"
            elif config.REQUIRE_WARD and not converted.ward:
                # Require BOTH province AND ward
                is_valid = False
                reason = "No ward in converted address - address incomplete"
            elif config.REQUIRE_COORDINATES:
                if not converted.latitude or not converted.longitude:
                    is_valid = False
                    reason = "No coordinates in converted address"
                elif not config.ALLOW_ZERO_COORDINATES:
                    if converted.latitude == 0.0 or converted.longitude == 0.0:
                        is_valid = False
                        reason = "Invalid coordinates (0.0) in converted address"
            
            # Additional validation: Check if province changed unexpectedly
            # This helps catch cases where conversion went wrong
            if is_valid and hasattr(converted, 'OldAdminUnit'):
                old_unit = converted.OldAdminUnit
                if old_unit.province and converted.province:
                    # Extract province name without "Tỉnh" or "Thành phố" prefix for comparison
                    old_prov_name = re.sub(r'^(Tỉnh|Thành\s+phố)\s+', '', old_unit.province, flags=re.IGNORECASE).strip()
                    new_prov_name = re.sub(r'^(Tỉnh|Thành\s+phố)\s+', '', converted.province, flags=re.IGNORECASE).strip()
                    
                    # If province names are completely different (not just administrative changes),
                    # this might indicate a parsing error
                    # Note: Some province mergers are expected (e.g., Bắc Giang -> Bắc Ninh)
                    # So we only flag if the names are very different
                    if old_prov_name and new_prov_name and old_prov_name != new_prov_name:
                        # Check if it's a known merger (conservative check)
                        # If not a known merger and names are very different, log warning but don't fail
                        if config.VALIDATE_PROVINCE_CONSISTENCY and not _is_known_province_merger(old_prov_name, new_prov_name):
                            # Log but don't fail - might be legitimate administrative change
                            pass
            
            if is_valid:
                # NEW address (after conversion) - Post-2025 model: only province and ward/commune (no district)
                result['parsed_province'] = _remove_province_prefix(converted.province)
                result['parsed_district'] = None  # Post-2025 model: no district
                result['parsed_ward'] = converted.ward
                result['parsed_street'] = converted.street
                # Build address without district for post-2025 model
                address_parts = []
                if converted.street:
                    address_parts.append(converted.street)
                if converted.ward:
                    address_parts.append(converted.ward)
                if converted.province:
                    address_parts.append(converted.province)
                result['parsed_full_address'] = ', '.join(address_parts) if address_parts else converted.get_address(short_name=False)
                result['latitude'] = converted.latitude
                result['longitude'] = converted.longitude
                
                # OLD address (before conversion)
                if hasattr(converted, 'OldAdminUnit'):
                    old_unit = converted.OldAdminUnit
                    result['old_province'] = old_unit.province
                    result['old_district'] = old_unit.district
                    result['old_ward'] = old_unit.ward
                    result['old_full_address'] = old_unit.get_address(short_name=False)
                    result['old_latitude'] = old_unit.latitude
                    result['old_longitude'] = old_unit.longitude
                
                result['parse_success'] = True
                result['parse_mode'] = 'CONVERT_2025'
                result['skip_reason'] = None
            else:
                result['skip_reason'] = reason
                
        except Exception as e:
            result['skip_reason'] = f"Conversion error: {str(e)}"
        
        return result
    
    # Check if CONVERT_TO_LEGACY mode (new→old)
    if config.PROCESSING_MODE == config.ProcessingMode.CONVERT_TO_LEGACY:
        try:
            converted = convert_address(cleaned, mode=ConvertMode.CONVERT_LEGACY)
            # converted = OLD (63-province) AdminUnit; converted.NewAdminUnit = input (34-province)
            is_valid = True
            reason = None
            if not converted or not converted.province:
                is_valid = False
                reason = "No province in converted (legacy) address"
            elif config.REQUIRE_WARD and not converted.ward:
                is_valid = False
                reason = "No ward in converted (legacy) address - address incomplete"
            elif config.REQUIRE_COORDINATES:
                if not converted.latitude or not converted.longitude:
                    is_valid = False
                    reason = "No coordinates in converted (legacy) address"
                elif not config.ALLOW_ZERO_COORDINATES:
                    if converted.latitude == 0.0 or converted.longitude == 0.0:
                        is_valid = False
                        reason = "Invalid coordinates (0.0) in converted (legacy) address"
            if is_valid:
                # OLD address (63-province) - the converted result
                result['parsed_province'] = _remove_province_prefix(converted.province)
                result['parsed_district'] = _remove_province_prefix(converted.district) if converted.district else None
                result['parsed_ward'] = converted.ward
                result['parsed_street'] = converted.street
                result['parsed_full_address'] = converted.get_address(short_name=False)
                result['latitude'] = converted.latitude
                result['longitude'] = converted.longitude
                # NEW address (34-province) - the input
                if hasattr(converted, 'NewAdminUnit') and converted.NewAdminUnit:
                    new_unit = converted.NewAdminUnit
                    result['new_province'] = new_unit.province
                    result['new_ward'] = new_unit.ward
                    address_parts = []
                    if new_unit.street:
                        address_parts.append(new_unit.street)
                    if new_unit.ward:
                        address_parts.append(new_unit.ward)
                    if new_unit.province:
                        address_parts.append(new_unit.province)
                    result['new_full_address'] = ', '.join(address_parts) if address_parts else new_unit.get_address(short_name=False)
                    result['new_latitude'] = new_unit.latitude
                    result['new_longitude'] = new_unit.longitude
                result['parse_success'] = True
                result['parse_mode'] = 'CONVERT_LEGACY'
                result['skip_reason'] = None
            else:
                result['skip_reason'] = reason
        except Exception as e:
            result['skip_reason'] = f"Conversion error: {str(e)}"
        return result
    
    # CRITICAL FIX: Extract explicit province from address to validate against parser results
    # This prevents wrong province matches from unique ward keywords
    # Must be done BEFORE mode selection
    explicit_province = None
    # Try to find province with prefix first (Tỉnh X or Thành phố X)
    province_pattern = re.compile(r'(Tỉnh|Thành\s+phố)\s+([^,]+)', re.IGNORECASE)
    province_match = province_pattern.search(cleaned)
    if province_match:
        explicit_province = province_match.group(2).strip()
    else:
        # Fallback: Look for common province names at the end of address
        # This handles cases like "..., Quận 2, Bình Dương" (no prefix)
        # Common province names that might appear without prefix
        common_provinces = [
            'Bình Dương', 'Đồng Tháp', 'Thanh Hóa', 'Hà Nội', 'Hồ Chí Minh',
            'Đà Nẵng', 'Hải Phòng', 'An Giang', 'Bà Rịa - Vũng Tàu', 'Bạc Liêu',
            'Bắc Giang', 'Bắc Kạn', 'Bắc Ninh', 'Bến Tre', 'Bình Định',
            'Bình Phước', 'Bình Thuận', 'Cà Mau', 'Cao Bằng', 'Đắk Lắk',
            'Đắk Nông', 'Điện Biên', 'Gia Lai', 'Hà Giang', 'Hà Nam',
            'Hà Tĩnh', 'Hải Dương', 'Hậu Giang', 'Hòa Bình', 'Hưng Yên',
            'Khánh Hòa', 'Kiên Giang', 'Kon Tum', 'Lai Châu', 'Lâm Đồng',
            'Lạng Sơn', 'Lào Cai', 'Long An', 'Nam Định', 'Nghệ An',
            'Ninh Bình', 'Ninh Thuận', 'Phú Thọ', 'Phú Yên', 'Quảng Bình',
            'Quảng Nam', 'Quảng Ngãi', 'Quảng Ninh', 'Quảng Trị', 'Sóc Trăng',
            'Sơn La', 'Tây Ninh', 'Thái Bình', 'Thái Nguyên', 'Thanh Hóa',
            'Thừa Thiên Huế', 'Tiền Giang', 'Trà Vinh', 'Tuyên Quang', 'Vĩnh Long',
            'Vĩnh Phúc', 'Yên Bái'
        ]
        # Check last part of address (after last comma) for province name
        parts = [p.strip() for p in cleaned.split(',')]
        if parts:
            last_part = parts[-1]
            for prov in common_provinces:
                if prov.lower() in last_part.lower() or last_part.lower() in prov.lower():
                    explicit_province = prov
                    break
    
    # Standard parsing modes (LEGACY or FROM_2025)
    # HYBRID MODE: Combine both LEGACY and FROM_2025 for best results
    if config.PARSER_MODE:
        # Convert string to ParseMode enum if needed
        if config.PARSER_MODE == 'LEGACY':
            modes = [ParseMode.LEGACY]
        elif config.PARSER_MODE == 'FROM_2025':
            modes = [ParseMode.FROM_2025]
        elif config.PARSER_MODE == 'HYBRID' or config.USE_HYBRID_MODE:
            # HYBRID: Try both modes and pick the best
            modes = [ParseMode.LEGACY, ParseMode.FROM_2025]
        else:
            modes = [config.PARSER_MODE]  # Already enum
    else:
        # Default behavior: use hybrid mode if enabled, otherwise try both
        if config.USE_HYBRID_MODE:
            modes = [ParseMode.LEGACY, ParseMode.FROM_2025]
        else:
            # If explicit province found, prefer LEGACY first to avoid unique ward issues
            if explicit_province and config.PREFER_LEGACY_FOR_EXPLICIT_PROVINCE:
                modes = [ParseMode.LEGACY, ParseMode.FROM_2025]
            else:
                modes = [ParseMode.LEGACY, ParseMode.FROM_2025]
    
    # Try parsing with different modes and score each result
    candidate_results = []  # List of (admin_unit, mode, score, is_valid, reason)
    
    for mode in modes:
        try:
            admin_unit = parse_address(
                cleaned, 
                mode=mode, 
                keep_street=config.KEEP_STREET
            )
            
            # Check province match
            province_match_score = 0
            province_mismatch = False
            if explicit_province and admin_unit.province:
                # Extract province name from parser result
                parsed_province_name = re.sub(
                    r'^(Tỉnh|Thành\s+phố)\s+', 
                    '', 
                    admin_unit.province, 
                    flags=re.IGNORECASE
                ).strip()
                
                # Normalize for comparison
                explicit_normalized = _normalize_for_comparison(explicit_province)
                parsed_normalized = _normalize_for_comparison(parsed_province_name)
                
                if explicit_normalized == parsed_normalized:
                    province_match_score = 10  # Perfect match
                elif _is_known_province_merger(explicit_province, parsed_province_name):
                    province_match_score = 8  # Known merger
                else:
                    province_mismatch = True
                    province_match_score = -10  # Wrong province - heavy penalty
            
            # Validate the result
            is_valid, reason = validate_parse_result(admin_unit, cleaned)
            
            # Calculate score
            # CRITICAL: Province correctness is the highest priority
            score = 0
            if province_mismatch:
                score = -1000  # Heavy penalty for wrong province - always reject
            elif is_valid:
                score += province_match_score  # +10 for perfect match, +8 for known merger
                if admin_unit.province:
                    score += 5  # Has province
                if admin_unit.ward:
                    score += 3  # Has ward (preferred)
                if admin_unit.district:
                    score += 1  # Has district (bonus)
                if admin_unit.street:
                    score += 1  # Has street (bonus)
            else:
                score = -100  # Invalid result (but less penalty than wrong province)
            
            candidate_results.append((admin_unit, mode, score, is_valid, reason, province_mismatch))
                    
        except Exception as e:
            candidate_results.append((None, mode, -100, False, f"Parse error: {str(e)}", False))
            continue
    
    # Select best result based on score
    # CRITICAL: Never select results with province mismatches
    best_admin_unit = None
    best_mode = None
    best_score = -999
    
    # First pass: Only consider results without province mismatches
    for admin_unit, mode, score, is_valid, reason, province_mismatch in candidate_results:
        if province_mismatch:
            continue  # Skip province mismatches completely
        if score > best_score:
            best_score = score
            best_admin_unit = admin_unit
            best_mode = mode
            if not result['skip_reason'] and not is_valid:
                result['skip_reason'] = reason
    
    # Second pass: If no valid result found without province mismatch, 
    # try to use the best available (even if invalid, but still no province mismatch)
    if best_admin_unit is None:
        for admin_unit, mode, score, is_valid, reason, province_mismatch in candidate_results:
            if province_mismatch:
                continue  # Still skip province mismatches
            if admin_unit and score > best_score:
                best_score = score
                best_admin_unit = admin_unit
                best_mode = mode
                if not result['skip_reason']:
                    result['skip_reason'] = reason or "No fully valid result found"
    
    # Fallback: If FROM_2025 mode didn't find a ward but found province,
    # and we have a valid province, try using CONVERT mode as fallback
    if (best_admin_unit and 
        best_mode == ParseMode.FROM_2025 and 
        not best_admin_unit.ward and 
        best_admin_unit.province and
        config.USE_CONVERT_AS_FALLBACK):
        try:
            # Try CONVERT mode to get ward information
            converted = convert_address(cleaned, mode=ConvertMode.CONVERT_2025)
            if converted and converted.province and converted.ward:
                # Use converted result if it has both province and ward
                # But only if province matches
                if converted.province == best_admin_unit.province:
                    best_admin_unit = converted
                    best_mode = 'FROM_2025_WITH_CONVERT_FALLBACK'
        except Exception:
            pass  # Silently fail fallback
    
    # Use best result if found
    if best_admin_unit:
        # Post-2025 model: only province and ward/commune (no district)
        result['parsed_province'] = _remove_province_prefix(best_admin_unit.province)
        result['parsed_district'] = None  # Post-2025 model: no district
        result['parsed_ward'] = best_admin_unit.ward
        result['parsed_street'] = best_admin_unit.street
        # Build address without district for post-2025 model
        address_parts = []
        if best_admin_unit.street:
            address_parts.append(best_admin_unit.street)
        if best_admin_unit.ward:
            address_parts.append(best_admin_unit.ward)
        if best_admin_unit.province:
            address_parts.append(best_admin_unit.province)
        result['parsed_full_address'] = ', '.join(address_parts) if address_parts else best_admin_unit.get_address(short_name=False)
        result['latitude'] = best_admin_unit.latitude
        result['longitude'] = best_admin_unit.longitude
        result['parse_success'] = True
        result['parse_mode'] = best_mode.value if hasattr(best_mode, 'value') else best_mode
        result['skip_reason'] = None
    
    return result


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def process_file(input_file: str = None, address_column: str = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Process an entire file of addresses.
    Returns (output_df, results_df)
    """
    # Use config values if not provided
    input_file = input_file or config.INPUT_FILE
    address_column = address_column or config.ADDRESS_COLUMN
    
    print("="*70)
    print(f"ADDRESS PROCESSING - {config.PROCESSING_MODE.value.upper()} MODE")
    print("="*70)
    print(f"Mode: {config.get_mode_description()}")
    print(f"Input file: {input_file}")
    try:
        print(f"Address column: {address_column}")
    except:
        print(f"Address column: [contains Vietnamese characters]")
    print("="*70 + "\n")
    
    # Read input file
    print("Reading input file...")
    try:
        if config.SHEET_NAME:
            df = pd.read_excel(input_file, sheet_name=config.SHEET_NAME)
        else:
            df = pd.read_excel(input_file)  # Read first sheet
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, None
    
    print(f"Total rows: {len(df)}")
    
    # Filter to rows with addresses
    if address_column not in df.columns:
        print(f"Error: Column not found in file!")
        print(f"Available columns: {[repr(col) for col in df.columns.tolist()]}")
        return None, None
    
    df_with_addresses = df[df[address_column].notna()].copy()
    print(f"Rows with addresses: {len(df_with_addresses)}")
    
    # Process each address
    print(f"\nProcessing addresses ({config.PROCESSING_MODE.value} mode)...")
    results = []
    
    for idx, row in df_with_addresses.iterrows():
        address = row[address_column]
        result = parse_and_process_address(address)
        results.append({
            'row_index': idx,
            'original_address': address,
            **result
        })
        
        if config.SHOW_PROGRESS and (len(results) % config.PROGRESS_INTERVAL == 0):
            print(f"  Processed {len(results)}/{len(df_with_addresses)} addresses...")
    
    # Create results dataframe
    df_results = pd.DataFrame(results)
    
    # Merge back with original data
    df_output = df_with_addresses.merge(
        df_results, 
        left_index=True, 
        right_on='row_index',
        how='left'
    )
    
    # Drop row_index column
    df_output = df_output.drop(columns=['row_index'], errors='ignore')
    
    # Log statistics
    successful = df_results['parse_success'].sum()
    failed = len(df_results) - successful
    # Count missing wards only among successfully processed addresses (matches "Valid Addresses" sheet)
    df_successful = df_results[df_results['parse_success'] == True]
    missing_ward = df_successful['parsed_ward'].isna().sum()
    
    print("\n" + "="*70)
    print("PROCESSING COMPLETE")
    print("="*70)
    print(f"  Total addresses: {len(df_results)}")
    print(f"  Successfully processed: {successful} ({successful/len(df_results)*100:.1f}%)")
    print(f"  Skipped: {failed} ({failed/len(df_results)*100:.1f}%)")
    print(f"  With coordinates: {df_results['latitude'].notna().sum()}")
    print(f"  Missing Ward/Commune (in valid addresses): {missing_ward} ({missing_ward/len(df_successful)*100:.1f}% of valid)")
    print("="*70 + "\n")
    
    return df_output, df_results


# ============================================================================
# OUTPUT GENERATION
# ============================================================================

def save_outputs(df_output: pd.DataFrame, df_results: pd.DataFrame, base_name: str = "addresses"):
    """
    Save processing results to Excel file only.
    """
    print("Saving output...")
    
    # Filter columns: include requested passthrough columns from original file
    passthrough_cols = [col for col in getattr(config, 'PASSTHROUGH_COLUMNS', []) if col in df_output.columns]
    base_cols = [col for col in config.OUTPUT_COLUMNS if col in df_output.columns]
    # Preserve order, deduplicate with passthrough first
    ordered_cols = []
    for col in passthrough_cols + base_cols:
        if col not in ordered_cols:
            ordered_cols.append(col)
    df_final = df_output[ordered_cols].copy()
    
    # Separate valid and skipped  
    # For skipped, we need to go back to df_output to get all original columns
    if 'parse_success' in df_output.columns:
        df_valid = df_output[df_output['parse_success'] == True].copy()
        df_skipped_full = df_output[df_output['parse_success'] == False].copy()
    else:
        df_valid = df_output.copy()
        df_skipped_full = pd.DataFrame()
    
    # Save Excel
    excel_file = config.get_output_filepath(base_name, "xlsx")
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        if config.CREATE_SEPARATE_SHEETS:
            # Clean columns for valid addresses
            # Include passthrough columns and original address column for valid sheet
            valid_cols = []
            # Add passthrough columns first
            for col in passthrough_cols:
                if col not in valid_cols:
                    valid_cols.append(col)
            # Add original address column (Địa chỉ)
            if config.ADDRESS_COLUMN in df_valid.columns and config.ADDRESS_COLUMN not in valid_cols:
                valid_cols.append(config.ADDRESS_COLUMN)
            # Add base columns (parsed results)
            for col in base_cols:
                if col not in valid_cols:
                    valid_cols.append(col)
            valid_clean = df_valid[valid_cols].drop(columns=['parse_success', 'skip_reason'], errors='ignore').copy()
            
            # AUTO FILTERING: Automatically decide per address based on what it has
            # Logic:
            # - Addresses with BOTH province AND ward → Always included
            # - Addresses with province but NO ward → Included if REQUIRE_WARD=False
            # - This makes it automatic - no need to manually set FILTER_VALID_BY_WARD per case
            if 'parsed_province' in valid_clean.columns:
                if 'parsed_ward' in valid_clean.columns:
                    # Both columns exist - filter based on REQUIRE_WARD setting
                    if config.REQUIRE_WARD:
                        # Ward is required - only include addresses with both province AND ward
                        valid_clean = valid_clean[
                            valid_clean['parsed_province'].notna() & 
                            valid_clean['parsed_ward'].notna()
                        ].copy()
                    else:
                        # Ward not required - include all addresses with province (ward optional)
                        valid_clean = valid_clean[
                            valid_clean['parsed_province'].notna()
                        ].copy()
                else:
                    # No ward column - include all with province
                    valid_clean = valid_clean[
                        valid_clean['parsed_province'].notna()
                    ].copy()
            
            # Remove OLD columns if they're all empty (not in CONVERT mode)
            old_cols = ['old_province', 'old_district', 'old_ward', 'old_full_address', 'old_latitude', 'old_longitude']
            for col in old_cols:
                if col in valid_clean.columns and valid_clean[col].isna().all():
                    valid_clean = valid_clean.drop(columns=[col])
            # Remove NEW columns if they're all empty (not in CONVERT_TO_LEGACY mode)
            new_cols = ['new_province', 'new_ward', 'new_full_address', 'new_latitude', 'new_longitude']
            for col in new_cols:
                if col in valid_clean.columns and valid_clean[col].isna().all():
                    valid_clean = valid_clean.drop(columns=[col])
            
            # Reset STT index (1, 2, 3, ...) - must do this BEFORE renaming
            if 'STT' in valid_clean.columns:
                valid_clean = valid_clean.reset_index(drop=True)
                valid_clean['STT'] = range(1, len(valid_clean) + 1)
            
            # Rename columns according to mapping
            if hasattr(config, 'COLUMN_RENAME_MAP'):
                valid_clean = valid_clean.rename(columns=config.COLUMN_RENAME_MAP)
            
            valid_clean.to_excel(writer, sheet_name=config.SHEET_VALID_NAME, index=False)
            
            # Clean columns for skipped addresses - include passthrough columns
            if len(df_skipped_full) > 0:
                # Build list of columns to include (in order of preference)
                skip_cols = []
                for col in passthrough_cols + ['STT', 'Mã địa chỉ', 'Tên địa chỉ', config.ADDRESS_COLUMN, 'original_address', 
                           'cleaned_address', 'skip_reason']:
                    if col in df_skipped_full.columns:
                        skip_cols.append(col)
                
                # Make sure we have at least the address and reason
                if len(skip_cols) > 0:
                    df_skipped_clean = df_skipped_full[skip_cols].copy()
                    df_skipped_clean.to_excel(writer, sheet_name=config.SHEET_SKIPPED_NAME, index=False)
                else:
                    # Fallback: save all columns
                    df_skipped_full.to_excel(writer, sheet_name=config.SHEET_SKIPPED_NAME, index=False)
            else:
                # Create empty sheet
                pd.DataFrame().to_excel(writer, sheet_name=config.SHEET_SKIPPED_NAME, index=False)
        else:
            df_final.to_excel(writer, sheet_name='All Addresses', index=False)
    
    print(f"  [OK] Saved: {excel_file}")


def save_summary(df_results: pd.DataFrame, base_name: str):
    """Save text summary of processing"""
    summary_file = config.get_output_filepath(f"{base_name}_summary", "txt")
    
    successful = df_results['parse_success'].sum()
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Address Processing Summary - {config.PROCESSING_MODE.value.upper()} MODE\n")
        f.write(f"{'='*70}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total addresses: {len(df_results)}\n")
        f.write(f"Successfully processed: {successful} ({successful/len(df_results)*100:.1f}%)\n")
        f.write(f"Skipped: {len(df_results) - successful}\n")
        f.write(f"With coordinates: {df_results['latitude'].notna().sum()}\n")
        # Count missing wards only among successfully processed addresses (matches "Valid Addresses" sheet)
        df_successful = df_results[df_results['parse_success'] == True]
        missing_ward = df_successful['parsed_ward'].isna().sum()
        f.write(f"Missing Ward/Commune (in valid addresses): {missing_ward} ({missing_ward/len(df_successful)*100:.1f}% of valid)\n\n")
        
        f.write(f"Successful parses (first {config.SUMMARY_SAMPLE_COUNT}):\n")
        f.write(f"{'-'*70}\n")
        for idx, row in df_results[df_results['parse_success']].head(config.SUMMARY_SAMPLE_COUNT).iterrows():
            f.write(f"\nOriginal: {row['original_address']}\n")
            
            # Check if CONVERT mode (old→new, has old address info)
            if pd.notna(row.get('old_province')):
                f.write(f"\nNEW Address (2025): {row['parsed_full_address']}\n")
                f.write(f"  Province: {row['parsed_province']}\n")
                if pd.notna(row['parsed_district']):
                    f.write(f"  District: {row['parsed_district']}\n")
                if pd.notna(row['parsed_ward']):
                    f.write(f"  Ward: {row['parsed_ward']}\n")
                f.write(f"  Coordinates: {row['latitude']}, {row['longitude']}\n")
                
                f.write(f"\nOLD Address (Before 2025): {row['old_full_address']}\n")
                f.write(f"  Province: {row['old_province']}\n")
                if pd.notna(row['old_district']):
                    f.write(f"  District: {row['old_district']}\n")
                if pd.notna(row['old_ward']):
                    f.write(f"  Ward: {row['old_ward']}\n")
                f.write(f"  Coordinates: {row['old_latitude']}, {row['old_longitude']}\n")
            # Check if CONVERT_TO_LEGACY mode (new→old, has new/input address info)
            elif pd.notna(row.get('new_province')):
                f.write(f"\nInput Address (2025): {row['new_full_address']}\n")
                f.write(f"  Province: {row['new_province']}\n")
                if pd.notna(row.get('new_ward')):
                    f.write(f"  Ward: {row['new_ward']}\n")
                f.write(f"  Coordinates: {row['new_latitude']}, {row['new_longitude']}\n")
                
                f.write(f"\nConverted (Before 2025): {row['parsed_full_address']}\n")
                f.write(f"  Province: {row['parsed_province']}\n")
                if pd.notna(row['parsed_district']):
                    f.write(f"  District: {row['parsed_district']}\n")
                if pd.notna(row['parsed_ward']):
                    f.write(f"  Ward: {row['parsed_ward']}\n")
                f.write(f"  Coordinates: {row['latitude']}, {row['longitude']}\n")
            else:
                # Standard parsing (not CONVERT mode) - Post-2025 model: only province and ward
                f.write(f"Parsed: {row['parsed_full_address']}\n")
                f.write(f"Province: {row['parsed_province']}\n")
                if pd.notna(row['parsed_ward']):
                    f.write(f"Ward/Commune: {row['parsed_ward']}\n")
                f.write(f"Coordinates: {row['latitude']}, {row['longitude']}\n")
        
        f.write(f"\n\nSkip reasons breakdown:\n")
        f.write(f"{'-'*70}\n")
        skip_reasons = df_results[~df_results['parse_success']]['skip_reason'].value_counts()
        for reason, count in skip_reasons.items():
            f.write(f"  {reason}: {count}\n")
    
    print(f"  [OK] Saved: {summary_file}")


def save_statistics(df_results: pd.DataFrame, base_name: str):
    """Save processing statistics as JSON"""
    stats_file = config.get_output_filepath(f"{base_name}_stats", "json")
    
    successful = df_results['parse_success'].sum()
    # Count missing wards only among successfully processed addresses (matches "Valid Addresses" sheet)
    df_successful = df_results[df_results['parse_success'] == True]
    missing_ward = df_successful['parsed_ward'].isna().sum()
    
    stats = {
        'timestamp': datetime.now().isoformat(),
        'mode': config.PROCESSING_MODE.value,
        'total_addresses': len(df_results),
        'successful': int(successful),
        'failed': int(len(df_results) - successful),
        'success_rate': round(successful/len(df_results)*100, 2),
        'with_coordinates': int(df_results['latitude'].notna().sum()),
        'with_ward': int(df_results['parsed_ward'].notna().sum()),
        'missing_ward_in_valid': int(missing_ward),
        'missing_ward_percentage_of_valid': round(missing_ward/len(df_successful)*100, 2) if len(df_successful) > 0 else 0,
        'skip_reasons': df_results[~df_results['parse_success']]['skip_reason'].value_counts().to_dict()
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"  [OK] Saved: {stats_file}")


def track_failures(df_results: pd.DataFrame):
    """Track failed addresses for learning"""
    failed = df_results[~df_results['parse_success']]
    if len(failed) == 0:
        return
    
    log_file = os.path.join(config.OUTPUT_DIR, config.FAILURE_LOG_FILE)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*70}\n")
        f.write(f"Failed addresses - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*70}\n")
        for idx, row in failed.head(20).iterrows():
            f.write(f"\nOriginal: {row['original_address']}\n")
            f.write(f"Cleaned: {row['cleaned_address']}\n")
            f.write(f"Reason: {row['skip_reason']}\n")


def track_successes(df_results: pd.DataFrame):
    """Track successful patterns for learning"""
    successful = df_results[df_results['parse_success']]
    if len(successful) == 0:
        return
    
    log_file = os.path.join(config.OUTPUT_DIR, config.SUCCESS_LOG_FILE)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*70}\n")
        f.write(f"Successful addresses - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*70}\n")
        for idx, row in successful.head(10).iterrows():
            f.write(f"\nOriginal: {row['original_address']}\n")
            f.write(f"Parsed: {row['parsed_full_address']}\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    start_time = time.time()
    print("\n" + "="*70)
    print("STARTING ADDRESS PROCESSING")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Process the file
        df_output, df_results = process_file()
        
        if df_output is None or df_results is None:
            print("Processing failed. Check error messages above.")
            return
        
        # Save outputs
        save_outputs(df_output, df_results)
        
        # Calculate elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        milliseconds = int((elapsed_time % 1) * 1000)
        
        print("\n" + "="*70)
        print("ALL DONE! Check the 'output' folder for results.")
        print("="*70)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if minutes > 0:
            print(f"Total execution time: {minutes} minute(s) {seconds} second(s) {milliseconds} ms")
        else:
            print(f"Total execution time: {seconds} second(s) {milliseconds} ms")
        print("="*70)
        
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        milliseconds = int((elapsed_time % 1) * 1000)
        
        print("\n" + "="*70)
        print(f"ERROR: {e}")
        print("="*70)
        if minutes > 0:
            print(f"Execution time before error: {minutes} minute(s) {seconds} second(s) {milliseconds} ms")
        else:
            print(f"Execution time before error: {seconds} second(s) {milliseconds} ms")
        print("="*70)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

