# 🔄 CONVERT Mode Guide

## What is CONVERT Mode?

**CONVERT mode** uses the `vietnamadminunits` library's CONVERT_2025 feature to:
- Convert OLD addresses (63-province system) → NEW addresses (34-province system)
- Handle province/district/ward mergers from 2025 administrative changes
- Track BOTH old and new addresses in output

---

## 🎯 When to Use CONVERT Mode

Use CONVERT mode when:
- ✅ Your addresses are from **before 2025** (old administrative system)
- ✅ You want to **update to the new 2025 system** (34 provinces after mergers)
- ✅ You need to **track what changed** (old vs new)
- ✅ You want **updated coordinates** for the new administrative structure

---

## 📊 Results Comparison

| Mode | Success Rate | What It Does |
|------|-------------|--------------|
| **STRICT** | 22.7% | Parse addresses, keep original system |
| **CONVERT** | 42.9% | ⭐ Convert old→new + handle mergers |
| **NORMAL** | ? | Parse with balanced validation |
| **LENIENT** | ? | Maximum coverage |

**CONVERT mode has HIGHER success rate** because it handles incomplete addresses better through the conversion process!

---

## 🔄 What Administrative Changes Happened in 2025?

### Province Mergers:
- **Bắc Giang** + parts → **Bắc Ninh**
- **Long An** + parts → **Tây Ninh**
- Many others... (63 provinces → 34 provinces)

### District Changes:
- Many districts merged into main cities
- Example: **Quận Hà Đông** → merged into **Thành phố Hà Nội**

### Ward Renamings:
- Ward names updated, especially in major cities
- Example: **Phường 3, Quận 4** → **Phường Vĩnh Hội**

---

## 📋 Example Conversions

### Example 1: Province Merger

**Original Address:**
```
Nguyễn Thế Chiến, Huyện Yên Thế, Tỉnh Bắc Giang
```

**OLD System (Before 2025):**
```
Province: Tỉnh Bắc Giang
District: Huyện Yên Thế
Coordinates: 21.512877, 106.134571
```

**NEW System (After 2025):**
```
Province: Tỉnh Bắc Ninh  ← Changed from Bắc Giang!
Coordinates: 21.2428, 106.167
```

---

### Example 2: District Removal

**Original Address:**
```
Phường Dương Nội, Quận Hà Đông, Thành phố Hà Nội
```

**OLD System:**
```
Province: Thành phố Hà Nội
District: Quận Hà Đông
Ward: Phường Dương Nội
Coordinates: 20.979868, 105.743919
```

**NEW System:**
```
Province: Thành phố Hà Nội
District: (removed - merged into city)
Ward: Phường Dương Nội
Coordinates: 20.975, 105.749
```

---

### Example 3: Ward Renaming

**Original Address:**
```
Số 3 Đường 48, Phường 3, Quận 4, Thành phố Hồ Chí Minh
```

**OLD System:**
```
Province: Thành phố Hồ Chí Minh
District: Quận 4
Ward: Phường 3
Coordinates: 10.754494, 106.69914
```

**NEW System:**
```
Province: Thành phố Hồ Chí Minh
Ward: Phường Vĩnh Hội  ← Ward renamed!
Coordinates: 10.7553, 106.696
```

---

## 🚀 How to Use CONVERT Mode

### Step 1: Edit `config.py`

Line 41:
```python
PROCESSING_MODE = ProcessingMode.CONVERT
```

### Step 2: Run Processing

```bash
python main.py
```

### Step 3: Check Results

Open `output/PROCESSED_addresses.xlsx`:

**Sheet: "Valid Addresses"**
- 217 addresses successfully converted
- Has BOTH old and new information

**Columns you'll see:**
```
Original Data:
- Địa chỉ giao hàng (original address)
- cleaned_address

NEW Data (2025 System):
- parsed_province       ← NEW province
- parsed_district       ← NEW district (if exists)
- parsed_ward           ← NEW ward
- parsed_full_address   ← NEW standardized address
- latitude              ← NEW coordinates
- longitude             ← NEW coordinates

OLD Data (Before 2025):
- old_province         ← OLD province
- old_district         ← OLD district
- old_ward            ← OLD ward
- old_full_address    ← OLD address
- old_latitude        ← OLD coordinates
- old_longitude       ← OLD coordinates
```

---

## 💡 Use Cases

### Use Case 1: Update Database to 2025 System
```
1. Process with CONVERT mode
2. Use "NEW" columns (parsed_*) for your database
3. Keep "OLD" columns (old_*) for reference/mapping
```

### Use Case 2: Track What Changed
```
Compare:
- old_province vs parsed_province
- old_district vs parsed_district
- old_ward vs parsed_ward

See which addresses were affected by mergers!
```

### Use Case 3: Update Coordinates
```
Use "NEW" latitude/longitude for:
- Updated GPS routing
- Delivery planning
- Mapping applications
```

---

## ⚙️ CONVERT Mode Settings

In `config.py`:

```python
# CONVERT mode uses these settings:
PROCESSING_MODE = ProcessingMode.CONVERT  # Enable CONVERT

# Validation is more lenient in CONVERT mode:
# - Province required: YES
# - District required: NO (districts changed in new system)
# - Ward required: NO
# - Min commas: 2 (ensures some structure)
```

---

## 📈 Success Rate Analysis

**HAFELE Case Results:**

| Metric | Count | % |
|--------|-------|---|
| Total addresses | 506 | 100% |
| Successfully converted | 217 | 42.9% |
| Skipped | 289 | 57.1% |
| With coordinates | 217 | 42.9% |

**Why 42.9% vs 22.7% in STRICT mode?**
- CONVERT mode is more flexible with district requirements
- Handles incomplete addresses better through conversion
- New system has simplified structure (34 provinces vs 63)

---

## 🔍 Troubleshooting

### "No province in converted address"
- Address too incomplete to convert
- Try cleaning the original address more
- Add more location information

### "Conversion error"
- Address format not recognized by converter
- Try LEGACY or FROM_2025 mode instead
- Check if address has minimum required info

### OLD columns are empty
- Address was parseable but not convertible
- This is OK - means address is already in new system
- Or address structure doesn't match old system

---

## 📚 More Information

- **Library:** `vietnamadminunits` (local module)
- **Conversion Logic:** `vietnamadminunits/converter/converter_2025.py`
- **Data:** `vietnamadminunits/data/converter_2025.json`

---

## 🎯 Recommendation

**Use CONVERT mode for:**
- ✅ Existing databases with old addresses
- ✅ Historical data that needs updating
- ✅ Systems transitioning to 2025 administrative structure
- ✅ When you need to track what changed

**Use STRICT mode for:**
- New addresses already in 2025 format
- When you don't need conversion
- When highest quality is more important than coverage

---

**Date Added:** October 16, 2025  
**Mode:** CONVERT (OPTION 3)  
**Success Rate:** 42.9% (217/506 addresses)

