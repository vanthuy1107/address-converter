# -*- coding: utf-8 -*-
"""
Address Processing Configuration
This file contains all settings and rules for address processing.
You can modify these settings for different use cases.
"""
import os
from enum import Enum


class ProcessingMode(Enum):
    """Processing strictness levels"""
    STRICT = "strict"  # Only process complete, validated addresses
    NORMAL = "normal"  # Process all parseable addresses
    LENIENT = "lenient"  # Try to process everything
    CONVERT = "convert"  # Convert old addresses to new 2025 system (handles mergers)


# ============================================================================
# FILE SETTINGS
# ============================================================================

# Input file settings
INPUT_FILE = r"C:\Users\smartlogaipc\Downloads\DanhSachDiaDiem_3012250340282934_gfOC8YERESBv0CFx.xlsx"
ADDRESS_COLUMN = "Địa chỉ giao hàng"  # Column name with addresses to process
SHEET_NAME = None  # None = first sheet, or specify sheet name

# Output file settings
OUTPUT_PREFIX = "PROCESSED"  # Prefix for output files
OUTPUT_DIR = "output"  # Directory for output files (created if doesn't exist)

# ============================================================================
# PROCESSING SETTINGS
# ============================================================================

# Processing mode: STRICT (recommended), NORMAL, LENIENT, or CONVERT
# - STRICT: Only complete, validated addresses (keeps OLD system with districts)
# - NORMAL: Balanced approach
# - LENIENT: Maximum coverage
# - CONVERT: Convert old addresses to new 2025 system (handles mergers, tracks OLD+NEW)
# NOTE: CONVERT mode fails for addresses without diacritics because it uses LEGACY mode first
#       which may misinterpret districts as wards. Use STRICT with FROM_2025 for better results.
PROCESSING_MODE = ProcessingMode.STRICT  # Use STRICT mode with LEGACY parser to avoid wrong province matches

# Parser mode: 'LEGACY' (63-province), 'FROM_2025' (34-province), 'HYBRID' (try both), or None (try both)
# NOTE: If PROCESSING_MODE is CONVERT, this setting is ignored
# HYBRID mode intelligently combines LEGACY and FROM_2025, scoring results to pick the best
# POST-2025 MODEL: Use 'FROM_2025' for new 2025 system (only province and ward/commune, no district)
PARSER_MODE = 'FROM_2025'  # Post-2025 model: 34-province system with only province and ward/commune

# Use hybrid mode to combine LEGACY and FROM_2025 intelligently
# When enabled, tries both modes and selects the best result based on:
# - Province correctness (matches explicit province in address)
# - Ward presence (prefers results with wards)
# - Validation passing
USE_HYBRID_MODE = True  # Enable intelligent combination of both modes

# Keep street information in parsed result
KEEP_STREET = True

# Normalize "Thành phố" districts in old addresses for FROM_2025 parser
# When enabled, addresses like "Phường X, Thành phố Y, Tỉnh Y" will be
# normalized to "Phường X, Tỉnh Y" to help FROM_2025 parser find the ward
# Note: This is only used in non-CONVERT modes
NORMALIZE_THANH_PHO_DISTRICTS = True

# Validate province consistency in CONVERT mode
# When enabled, checks if province changes are expected (mergers) vs errors
VALIDATE_PROVINCE_CONSISTENCY = False  # Set to True to enable strict validation

# Use CONVERT mode as fallback when FROM_2025 parser finds province but not ward
# This helps with addresses from old system where wards might not be in FROM_2025 data
USE_CONVERT_AS_FALLBACK = True

# Prefer LEGACY mode when explicit province is found in address
# This prevents unique ward matching from overriding explicit province names
# Set to True to avoid wrong province matches (e.g., Bình Dương -> Đồng Tháp)
PREFER_LEGACY_FOR_EXPLICIT_PROVINCE = True

# ============================================================================
# ADDRESS CLEANING RULES
# ============================================================================

# Phone number patterns to remove
PHONE_PATTERNS = [
    r'\d{9,11}',  # 9-11 consecutive digits
    r'\d{3}[-.\s]?\d{3}[-.\s]?\d{3,4}',  # Formatted phone numbers
    r'0\d{2,3}[-.\s]?\d{3}[-.\s]?\d{3,4}',  # Vietnamese phone format
]

# Name/contact prefixes to remove (case insensitive)
NAME_PREFIXES = [
    r'[Mm][Rr]\.?\s+\w+\s*[-:]?\s*',  # Mr. Name
    r'[Mm][Ss]\.?\s+\w+\s*[-:]?\s*',  # Ms. Name
    r'[Aa]nh\s+\w+\s*[-:]?\s*',  # Anh Name
    r'[Cc]hị\s+\w+\s*[-:]?\s*',  # Chị Name
    r'[Ll]iên [Hh]ệ.*?[-:]',  # Liên hệ
    r'[Ll][Hh]:?\s*.*?[-:]',  # LH:
    r'[Nn]gười nhận.*?[-:]',  # Người nhận
]

# Metadata patterns to remove
METADATA_PATTERNS = [
    r'CCCD\s*\d+',  # ID card numbers
    r'SDT:?\s*',  # Phone label
    r'#HAF\d+',  # Reference numbers
    r'VN\d+\s+TTBH.*',  # VN codes
    r'Sales\s+bs\s+.*',  # Sales notes
    r'Thông tin người nhận.*',  # Recipient info notes
]

# Warehouse/pickup keywords (if found, address is skipped)
# Format: (pattern, context_pattern)
# If pattern is found AND context_pattern is found nearby, skip the address
WAREHOUSE_PATTERNS = [
    (r'kho|KHO|warehouse', r'(qua|đến|tại|nhận|lấy|lay|nhan)\s+(kho|KHO)'),
    (r'khách.*?kho', None),  # "khách đến kho"
    (r'kho.*?lấy|lay', None),  # "kho lấy hàng"
]

# Minimum address length after cleaning
MIN_ADDRESS_LENGTH = 5

# ============================================================================
# VALIDATION RULES (STRICT MODE)
# ============================================================================

# Minimum required administrative levels
REQUIRE_PROVINCE = True
REQUIRE_DISTRICT = False  # Set to True if district is mandatory
REQUIRE_WARD = False  # Require ward for more specific locations (set to False to include addresses without wards)

# Minimum comma count (indicates address structure)
# 0 = no requirement
# 1 = at least street, ward
# 2 = street, ward, district, province (recommended)
# 3 = very strict
MIN_COMMA_COUNT = 2

# Coordinate validation
REQUIRE_COORDINATES = True
ALLOW_ZERO_COORDINATES = False  # Reject 0.0, 0.0

# Reject addresses that are just building names (no proper location)
REJECT_BUILDING_ONLY = True

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================

# Columns to include in output
OUTPUT_COLUMNS = [
    'STT',
    'Mã địa chỉ',
    'Tên địa chỉ',
    'Địa chỉ giao hàng',  # Original (will be different if you set ADDRESS_COLUMN)
    'parsed_full_address',  # Will be renamed to "New Address"
    'parsed_province',  # Will be renamed to "Province/City"
    'parsed_district',  # Will be renamed to "District"
    'parsed_ward',  # Will be renamed to "Ward/Commune"
    'latitude',
    'longitude',
    # OLD address fields (populated in CONVERT mode)
    'old_full_address',
    'old_province',
    'old_district',
    'old_ward',
    'old_latitude',
    'old_longitude',
]

# Additional original columns from the input file to keep in outputs
# Example: customer metadata columns such as codes or names
PASSTHROUGH_COLUMNS = [
    'Customer Code',
    'Customer Name',
]

# Column name mapping for output
COLUMN_RENAME_MAP = {
    'parsed_full_address': 'New Address',
    'parsed_province': 'Province/City',
    'parsed_district': 'District',
    'parsed_ward': 'Ward/Commune',
    # OLD address rename mapping
    'old_full_address': 'Old Address (Before 2025)',
    'old_province': 'Old Province/City',
    'old_district': 'Old District',
    'old_ward': 'Old Ward/Commune',
    'old_latitude': 'Old Latitude',
    'old_longitude': 'Old Longitude',
}

# Create separate sheets in Excel output
CREATE_SEPARATE_SHEETS = True
SHEET_VALID_NAME = "Valid Addresses"
SHEET_SKIPPED_NAME = "Skipped Addresses"

# AUTO FILTERING MODE (deprecated - now automatic based on REQUIRE_WARD)
# The system now automatically filters based on REQUIRE_WARD setting:
# - If REQUIRE_WARD=True: Only addresses with BOTH province AND ward are included
# - If REQUIRE_WARD=False: All addresses with province are included (ward optional)
# 
# This setting is kept for backward compatibility but is no longer used.
# The filtering is now fully automatic based on REQUIRE_WARD.
FILTER_VALID_BY_WARD = True  # Deprecated - filtering is now automatic

# Create CSV output
CREATE_CSV = True
CSV_ENCODING = 'utf-8-sig'  # utf-8-sig for Excel compatibility

# Create summary text file
CREATE_SUMMARY = True
SUMMARY_SAMPLE_COUNT = 15  # Number of samples to show in summary

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Enable progress display
SHOW_PROGRESS = True
PROGRESS_INTERVAL = 50  # Show progress every N addresses

# Log file
CREATE_LOG = True
LOG_FILE = "processing_log.txt"

# ============================================================================
# CUSTOM RULES (ADD YOUR OWN)
# ============================================================================

# Additional cleaning rules (will be applied in order)
# Format: (pattern, replacement)
CUSTOM_CLEANING_RULES = [
    # Add your custom rules here
    # Example: (r'specific_pattern', ''),
]

# Additional validation rules (will be checked after standard validation)
# Format: (check_function_name, error_message)
CUSTOM_VALIDATION_RULES = [
    # Add your custom validation functions here
    # Example: ('check_special_case', 'Failed special validation'),
]

# Skip patterns (addresses matching these will be skipped)
# These are in addition to warehouse patterns
CUSTOM_SKIP_PATTERNS = [
    # Add patterns for addresses you want to skip
    # Example: r'pattern_to_skip',
]

# ============================================================================
# LEARNING / IMPROVEMENT TRACKING
# ============================================================================

# Track problematic addresses for learning
TRACK_FAILURES = True
FAILURE_LOG_FILE = "failed_addresses_log.txt"

# Track successful patterns for learning
TRACK_SUCCESSES = True
SUCCESS_LOG_FILE = "successful_patterns_log.txt"

# Save processing statistics
SAVE_STATISTICS = True
STATISTICS_FILE = "processing_statistics.json"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_output_filepath(base_name, extension):
    """Generate output file path"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    timestamp = ""
    # Uncomment to add timestamp to filenames
    # from datetime import datetime
    # timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
    
    filename = f"{OUTPUT_PREFIX}_{base_name}{timestamp}.{extension}"
    return os.path.join(OUTPUT_DIR, filename)


def get_mode_description():
    """Get description of current processing mode"""
    descriptions = {
        ProcessingMode.STRICT: "Only complete, validated addresses",
        ProcessingMode.NORMAL: "All parseable addresses",
        ProcessingMode.LENIENT: "Maximum coverage, minimal validation",
        ProcessingMode.CONVERT: "Convert old addresses to new 2025 system (handles mergers)"
    }
    return descriptions.get(PROCESSING_MODE, "Unknown mode")


# ============================================================================
# MODE-SPECIFIC OVERRIDES
# ============================================================================

if PROCESSING_MODE == ProcessingMode.LENIENT:
    # Lenient mode: process as much as possible
    REQUIRE_DISTRICT = False
    MIN_COMMA_COUNT = 0
    REJECT_BUILDING_ONLY = False
    
elif PROCESSING_MODE == ProcessingMode.NORMAL:
    # Normal mode: balanced approach
    REQUIRE_DISTRICT = True
    MIN_COMMA_COUNT = 1
    REJECT_BUILDING_ONLY = True
    
elif PROCESSING_MODE == ProcessingMode.STRICT:
    # Strict mode: highest quality - require province + ward
    REQUIRE_DISTRICT = False
    REQUIRE_WARD = False  # Set to False to include addresses with province but no ward
    MIN_COMMA_COUNT = 2
    REJECT_BUILDING_ONLY = True

elif PROCESSING_MODE == ProcessingMode.CONVERT:
    # Convert mode: require BOTH province and ward in result
    REQUIRE_DISTRICT = False
    REQUIRE_WARD = True  # Must have ward in final result
    MIN_COMMA_COUNT = 2
    REJECT_BUILDING_ONLY = True

