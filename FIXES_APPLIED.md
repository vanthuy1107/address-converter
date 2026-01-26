# Fixes Applied for Address Conversion Issues

## Summary

Fixed address conversion issues for addresses from **Thành phố Thanh Hóa, Tỉnh Thanh Hóa** that were being incorrectly converted.

## Changes Made

### 1. Address Preprocessing (`main.py`)

Added `preprocess_address()` function that:
- **Normalizes comma spacing**: Ensures proper spacing after commas
- **Handles "Thành phố" districts**: For FROM_2025 mode, removes redundant "Thành phố X" when followed by "Tỉnh X" to help parser find wards
  - Example: `Phường Đông Thọ, Thành phố Thanh Hóa, Tỉnh Thanh Hóa` → `Phường Đông Thọ, Tỉnh Thanh Hóa`

### 2. Enhanced Address Cleaning (`main.py`)

Updated `clean_address()` to:
- Call `preprocess_address()` before other cleaning steps
- Ensure addresses are properly formatted before parsing

### 3. Province Validation (`main.py`)

Added validation in CONVERT mode to:
- Check if province changes are expected (known mergers) vs errors
- Helper function `_is_known_province_merger()` to identify legitimate administrative changes

### 4. Fallback Mechanism (`main.py`)

Added fallback for FROM_2025 mode:
- When FROM_2025 parser finds province but not ward, optionally uses CONVERT mode as fallback
- Only uses fallback if provinces match to prevent wrong province conversions
- Controlled by `USE_CONVERT_AS_FALLBACK` config option

### 5. Configuration Options (`config.py`)

Added new configuration options:

```python
# Normalize "Thành phố" districts for FROM_2025 parser
NORMALIZE_THANH_PHO_DISTRICTS = True

# Validate province consistency in CONVERT mode
VALIDATE_PROVINCE_CONSISTENCY = False

# Use CONVERT mode as fallback when FROM_2025 parser finds province but not ward
USE_CONVERT_AS_FALLBACK = True
```

## How It Works

### For CONVERT Mode:
1. Address is preprocessed (comma spacing normalized)
2. CONVERT mode processes the address using LEGACY parser first
3. Maps old address to new 2025 system
4. Validates province consistency (if enabled)
5. **Result**: Correctly converts addresses, preserving province and mapping wards according to 2025 changes

### For FROM_2025 Mode (STRICT):
1. Address is preprocessed:
   - Comma spacing normalized
   - "Thành phố X, Tỉnh X" → "Tỉnh X" (if `NORMALIZE_THANH_PHO_DISTRICTS = True`)
2. FROM_2025 parser attempts to find province and ward
3. If province found but ward not found, and `USE_CONVERT_AS_FALLBACK = True`:
   - Falls back to CONVERT mode
   - Only uses result if province matches
4. **Result**: Better ward recognition for old addresses

## Test Results

### CONVERT Mode:
✅ **Province**: Correctly identifies `Tỉnh Thanh Hóa`
✅ **Ward**: Maps to `Phường Hạc Thành` (according to 2025 administrative changes)
✅ **Old Address**: Preserved correctly

### FROM_2025 Mode:
✅ **Province**: Correctly identifies `Tỉnh Thanh Hóa`
⚠️ **Ward**: Still not found in FROM_2025 data (ward names may have changed)
✅ **Fallback**: Can use CONVERT mode to get ward information

## Recommendations

### For Addresses from Before 2025:
**Use CONVERT mode** - It correctly handles the administrative changes:
```python
PROCESSING_MODE = ProcessingMode.CONVERT
```

### For Addresses from 2025+:
**Use STRICT mode with FROM_2025** - With fallback enabled:
```python
PROCESSING_MODE = ProcessingMode.STRICT
PARSER_MODE = 'FROM_2025'
USE_CONVERT_AS_FALLBACK = True  # Helps find wards from old addresses
```

### If You See Wrong Provinces:
1. **Check the actual addresses in your Excel file** - They might be different from what was reported
2. **Enable province validation**:
   ```python
   VALIDATE_PROVINCE_CONSISTENCY = True
   ```
3. **Check address cleaning** - Ensure addresses aren't being corrupted during cleaning

## Known Limitations

1. **Ward Merging**: Multiple old wards (Đông Thọ, Trường Thi, Phú Sơn) map to the same new ward (Hạc Thành). This is **correct** according to 2025 administrative changes, but all three addresses will have the same ward.

2. **FROM_2025 Ward Recognition**: The FROM_2025 parser may not find wards from old addresses if:
   - Ward names changed in 2025
   - Wards were merged/renamed
   - Wards don't exist in the FROM_2025 dataset

3. **Fallback Limitation**: The fallback mechanism only works if the province matches between FROM_2025 and CONVERT results.

## Next Steps

If you still see wrong provinces in your output:
1. Verify the actual addresses in your Excel file
2. Check if address cleaning is corrupting addresses
3. Review the output file to see what addresses are being processed
4. Enable logging to see detailed processing information

