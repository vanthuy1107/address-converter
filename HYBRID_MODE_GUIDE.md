# Hybrid Mode Guide

## Overview

Hybrid mode intelligently combines **LEGACY** (63-province) and **FROM_2025** (34-province) parsers to handle both old and new address formats. It tries both modes and selects the best result based on a scoring system.

## How It Works

1. **Tries Both Modes**: Parses the address with both LEGACY and FROM_2025 parsers
2. **Scores Each Result**: Assigns a score based on:
   - **Province Correctness** (highest priority): +10 for perfect match with explicit province, +8 for known mergers
   - **Province Presence**: +5 if province is found
   - **Ward Presence**: +3 if ward is found (preferred)
   - **District Presence**: +1 bonus
   - **Street Presence**: +1 bonus
   - **Wrong Province**: -1000 penalty (always rejected)
3. **Selects Best Result**: Chooses the result with the highest score

## Configuration

Enable hybrid mode in `config.py`:

```python
# Option 1: Set PARSER_MODE to None or 'HYBRID'
PARSER_MODE = None  # or 'HYBRID'

# Option 2: Enable USE_HYBRID_MODE flag
USE_HYBRID_MODE = True
```

## Benefits

✅ **Handles Old Addresses**: LEGACY mode correctly parses addresses from the 63-province system  
✅ **Handles New Addresses**: FROM_2025 mode parses addresses from the 34-province system  
✅ **Prevents Wrong Provinces**: Heavily penalizes province mismatches  
✅ **Prefers Complete Results**: Favors results with both province and ward  

## Example Results

### Old Address (63-province system)
**Input**: `Phường Thạnh Mỹ Lợi, Quận 2, Bình Dương`  
**Result**: Uses LEGACY mode, correctly identifies `Tỉnh Bình Dương`

### New Address (34-province system)
**Input**: `Phường X, Tỉnh Y` (new format)  
**Result**: Uses FROM_2025 mode, correctly identifies province and ward

### Address with Explicit Province
**Input**: `..., Bình Dương` (no "Tỉnh" prefix)  
**Result**: Extracts province name, validates against parser results, prevents wrong matches

## Province Validation

Hybrid mode includes enhanced province extraction that:
- Finds provinces with "Tỉnh" or "Thành phố" prefix
- Falls back to checking common province names at the end of address
- Validates parser results against explicit provinces
- Rejects results with province mismatches

## Scoring Priority

1. **Province Correctness** (most important)
2. **Validation Passing**
3. **Ward Presence**
4. **District/Street Presence**

This ensures that a result with the correct province but no ward is preferred over a result with a ward but wrong province.

