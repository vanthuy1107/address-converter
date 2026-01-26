# -*- coding: utf-8 -*-
"""
Custom Rules Module
Add your own custom cleaning, validation, and processing rules here.
These rules will be learned and refined over time based on different use cases.
"""
import re
import pandas as pd


# ============================================================================
# CUSTOM CLEANING RULES
# ============================================================================

def clean_special_case_1(address: str) -> str:
    """
    Example: Remove specific patterns for your use case
    """
    # Example: Remove specific company codes
    address = re.sub(r'PROJECT\s+\d+_VN\d+_', '', address, flags=re.IGNORECASE)
    return address


def clean_special_case_2(address: str) -> str:
    """
    Add more custom cleaning logic here
    """
    return address


# List all custom cleaning functions to apply
CUSTOM_CLEANERS = [
    clean_special_case_1,
    # clean_special_case_2,
    # Add more as needed
]


# ============================================================================
# CUSTOM VALIDATION RULES
# ============================================================================

def validate_special_format(admin_unit, cleaned_address: str) -> tuple:
    """
    Example: Validate address follows specific format requirements
    Returns: (is_valid, error_message)
    """
    # Example: Reject if street name too short
    if admin_unit.street and len(admin_unit.street) < 5:
        return False, "Street name too short"
    
    return True, None


def validate_business_hours_address(admin_unit, cleaned_address: str) -> tuple:
    """
    Example: Special validation for business addresses
    """
    # Add your logic here
    return True, None


# List all custom validation functions
CUSTOM_VALIDATORS = [
    validate_special_format,
    # validate_business_hours_address,
    # Add more as needed
]


# ============================================================================
# CUSTOM SKIP PATTERNS
# ============================================================================

# Patterns that should cause address to be skipped
# Based on your specific use cases
CUSTOM_SKIP_PATTERNS = [
    # Example: Skip test addresses
    r'test\s+address',
    r'địa\s+chỉ\s+test',
    
    # Add more patterns based on what you learn
]


# ============================================================================
# POST-PROCESSING RULES
# ============================================================================

def post_process_result(result: dict, original_address: str) -> dict:
    """
    Apply custom logic after parsing
    Modify the result dictionary as needed
    
    Args:
        result: Dictionary with parsing results
        original_address: Original address string
    
    Returns:
        Modified result dictionary
    """
    
    # Example: Add custom flags or metadata
    if 'URGENT' in original_address.upper():
        result['priority'] = 'high'
    
    # Example: Adjust coordinates based on known patterns
    # if some_condition:
    #     result['latitude'] = adjusted_lat
    #     result['longitude'] = adjusted_lon
    
    return result


# ============================================================================
# LEARNING / PATTERN RECOGNITION
# ============================================================================

class AddressPatternLearner:
    """
    Learn common patterns from processing history
    This can be used to improve processing over time
    """
    
    def __init__(self):
        self.successful_patterns = []
        self.failed_patterns = []
    
    def learn_from_success(self, original: str, parsed: str):
        """
        Learn from successful parse
        """
        # Extract patterns that worked
        pattern = {
            'original': original,
            'parsed': parsed,
            'comma_count': original.count(','),
            'length': len(original),
        }
        self.successful_patterns.append(pattern)
    
    def learn_from_failure(self, original: str, reason: str):
        """
        Learn from failed parse
        """
        pattern = {
            'original': original,
            'reason': reason,
        }
        self.failed_patterns.append(pattern)
    
    def suggest_rules(self):
        """
        Suggest new rules based on learned patterns
        """
        suggestions = []
        
        # Analyze failures to suggest skip patterns
        common_failures = {}
        for pattern in self.failed_patterns:
            reason = pattern['reason']
            common_failures[reason] = common_failures.get(reason, 0) + 1
        
        # Add more analysis logic here
        
        return suggestions


# ============================================================================
# DOMAIN-SPECIFIC RULES
# ============================================================================

def is_residential_address(admin_unit) -> bool:
    """
    Determine if address is residential vs commercial
    """
    if not admin_unit.street:
        return False
    
    residential_keywords = ['căn hộ', 'chung cư', 'apartment', 'phòng']
    street_lower = admin_unit.street.lower()
    
    return any(keyword in street_lower for keyword in residential_keywords)


def is_commercial_address(admin_unit) -> bool:
    """
    Determine if address is commercial
    """
    if not admin_unit.street:
        return False
    
    commercial_keywords = ['văn phòng', 'office', 'tòa nhà', 'building', 'tầng']
    street_lower = admin_unit.street.lower()
    
    return any(keyword in street_lower for keyword in commercial_keywords)


def get_address_type(admin_unit) -> str:
    """
    Classify address type
    """
    if is_residential_address(admin_unit):
        return 'residential'
    elif is_commercial_address(admin_unit):
        return 'commercial'
    else:
        return 'unknown'


# ============================================================================
# EXAMPLE: COMPANY-SPECIFIC RULES
# ============================================================================

def clean_hafele_specific(address: str) -> str:
    """
    Example: HAFELE-specific cleaning rules learned from processing
    """
    # Remove HAFELE reference codes
    address = re.sub(r'#HAF\d+', '', address)
    
    # Remove specific notes format
    address = re.sub(r'VN\d+\s+TTBH.*', '', address)
    
    return address


def validate_hafele_delivery(admin_unit, cleaned_address: str) -> tuple:
    """
    Example: HAFELE-specific validation
    """
    # Must not be warehouse pickup
    if 'kho' in cleaned_address.lower() and 'lấy' in cleaned_address.lower():
        return False, "Warehouse pickup not allowed"
    
    return True, None


# Add company-specific rules to the lists above as you learn them
# CUSTOM_CLEANERS.append(clean_hafele_specific)
# CUSTOM_VALIDATORS.append(validate_hafele_delivery)

