# Address Conversion Issues Analysis

## Problem Summary

Three addresses from **Thành phố Thanh Hóa, Tỉnh Thanh Hóa** are being incorrectly converted:

1. `Phường Đông Thọ,Thành phố Thanh Hóa,Tỉnh Thanh Hóa` → `P, Xã Hương Đô, Tỉnh Hà Tĩnh` ❌
2. `Phường Trường Thi,Thành phố Thanh Hóa,Tỉnh Thanh Hóa` → `Phường Trường Thi, Tỉnh Ninh Bình` ❌
3. `Phường Phú Sơn,Thành phố Thanh Hóa,Tỉnh Thanh Hóa` → `Phường, Xã Phú Sơn, Tỉnh Ninh Bình` ❌

## Root Causes Identified

### Issue 1: CONVERT Mode - Ward Merging
When using **CONVERT mode**, the converter correctly parses the old address but maps multiple old wards to the same new ward:

- **Old wards**: Phường Đông Thọ, Phường Trường Thi, Phường Phú Sơn
- **New ward**: Phường Hạc Thành (all three map to this)

This is likely **correct** according to the 2025 administrative changes where multiple wards were merged. However, the converter data shows all these wards mapping to "Phường Hạc Thành" in the new system.

**Test Results:**
```
LEGACY PARSED: Province: Tỉnh Thanh Hóa ✓
CONVERTED: Province: Tỉnh Thanh Hóa ✓, Ward: Phường Hạc Thành (merged)
```

### Issue 2: FROM_2025 Parser - Ward Recognition
When using **STRICT mode** (which uses FROM_2025 parser), the parser:
- ✅ Correctly identifies province: `Tỉnh Thanh Hóa`
- ❌ Cannot find the ward (returns `None`)

This happens because in the 34-province system, the district structure changed and "Thành phố Thanh Hóa" may not exist as a district anymore, so the wards need to be looked up differently.

**Test Results:**
```
FROM_2025 PARSED: Province: Tỉnh Thanh Hóa ✓, Ward: None ❌
```

### Issue 3: Wrong Province Conversion (User's Output)
The user's output shows addresses being converted to **Hà Tĩnh** and **Ninh Bình** provinces, which is completely wrong. This suggests:

1. The addresses in the actual Excel file might be different from what was shown
2. There might be address cleaning/processing that's corrupting the addresses
3. The FROM_2025 parser might be misinterpreting parts of the address when the ward is missing

## Solutions

### Solution 1: Use CONVERT Mode (Recommended for Old Addresses)
If you have addresses from **before 2025** and want to convert them to the new system:

1. Set `PROCESSING_MODE = ProcessingMode.CONVERT` in `config.py`
2. The converter will correctly map wards according to 2025 administrative changes
3. Note: Multiple old wards may map to the same new ward (this is expected)

### Solution 2: Fix FROM_2025 Parser for Missing Wards
If using STRICT mode, the FROM_2025 parser needs to handle cases where:
- The old district ("Thành phố Thanh Hóa") doesn't exist in the new system
- Wards need to be looked up by name directly in the province

**Potential Fix**: Modify the parser to search for wards by name within the province when district is not found.

### Solution 3: Pre-process Addresses
Before parsing, normalize the address format:
- Ensure proper spacing: `Phường Đông Thọ, Thành phố Thanh Hóa, Tỉnh Thanh Hóa`
- Handle cases where "Thành phố" is used as both district and part of province name

## Recommendations

1. **For addresses from before 2025**: Use **CONVERT mode** - it handles the administrative changes correctly
2. **For addresses from 2025+**: Use **STRICT mode with FROM_2025** - but ensure wards are properly recognized
3. **Verify the actual addresses in your Excel file** - the wrong province conversion suggests the addresses might be different from what was shown

## Next Steps

1. Check the actual addresses in the Excel file to see if they match what was reported
2. Verify if CONVERT mode was used when generating the output (check the output file for "Old Address" columns)
3. If using STRICT mode, consider adding custom logic to handle "Thành phố Thanh Hóa" addresses

