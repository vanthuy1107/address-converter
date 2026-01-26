# Province Mismatch Fix Summary

## Problem
Address: `Feliz En Vista ( Đi cổng 4, cột G8, để kệ hàng) 1 Lê Hiến Mai, Phường Thạnh Mỹ Lợi, Quận 2, Bình Dương`

**Wrong Result**: Converted to `Tỉnh Đồng Tháp, Xã Mỹ Lợi`  
**Expected**: Should stay in `Tỉnh Bình Dương`

## Root Cause
The FROM_2025 parser is matching "Mỹ Lợi" (from "Thạnh Mỹ Lợi") as a unique ward that belongs to Đồng Tháp province, overriding the explicit "Bình Dương" province in the address.

## Fixes Applied

1. **Province Validation**: Added validation to check if parsed province matches explicit province in address
2. **Mode Preference**: When explicit province found, prefer LEGACY mode first to avoid unique ward mismatches
3. **Configuration Option**: Added `PREFER_LEGACY_FOR_EXPLICIT_PROVINCE = True` to enable this behavior

## Current Status
The validation code is in place but may not be fully effective. The FROM_2025 parser's unique ward matching happens before province validation can catch it.

## Recommended Solution

**For addresses with explicit provinces, use LEGACY mode or CONVERT mode:**

```python
# Option 1: Use LEGACY mode (recommended for old addresses)
PARSER_MODE = 'LEGACY'

# Option 2: Use CONVERT mode (for addresses before 2025)
PROCESSING_MODE = ProcessingMode.CONVERT
```

The FROM_2025 parser's unique ward feature is causing conflicts when ward names are ambiguous across provinces.

