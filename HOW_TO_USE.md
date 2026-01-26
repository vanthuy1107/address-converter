# 📘 How to Use the Address Processing System

## 🎯 Overview

This is a **reusable, learning address processing system** that can be adapted for different use cases. It learns and improves over time as you process different files.

---

## 🚀 Quick Start

### 1. Basic Usage (First Time)

```bash
# Just run it with default settings
python main.py
```

This will:
- Process `HAFELE DanhSachDiaDiem_thieutinhthanhphuongxa.xlsx`
- Use STRICT mode (only valid addresses)
- Save results to `output/` folder

### 2. Customize Settings

Edit `config.py` to change:
- Input file name
- Processing mode (STRICT/NORMAL/LENIENT)
- Validation rules
- Output format

### 3. Add Custom Rules

Edit `custom_rules.py` to add:
- Company-specific cleaning patterns
- Custom validation logic
- Domain-specific rules

---

## 📁 File Structure

```
├── main.py                 # Main processing script (don't modify often)
├── config.py              # All settings and rules (modify this!)
├── custom_rules.py        # Your custom rules (add new rules here)
├── vietnamadminunits/     # Address parser library
├── output/                # All outputs go here
│   ├── PROCESSED_addresses.xlsx
│   ├── PROCESSED_addresses_valid.csv
│   ├── PROCESSED_addresses_summary.txt
│   └── PROCESSED_addresses_stats.json
└── HOW_TO_USE.md         # This file
```

---

## ⚙️ Configuration Guide

### Processing Modes

Edit `config.py` line 33:

```python
PROCESSING_MODE = ProcessingMode.STRICT  # Change this line
```

**Options:**
- `ProcessingMode.STRICT` - ✅ **Recommended for production**
  - Only complete addresses (province + district + coordinates)
  - Highest quality, lower quantity
  
- `ProcessingMode.NORMAL` - For general use
  - Balanced approach
  - Good quality, moderate quantity
  
- `ProcessingMode.LENIENT` - For maximum coverage
  - Process everything possible
  - Lower quality, maximum quantity

### Input File Settings

Edit these in `config.py`:

```python
INPUT_FILE = "your_file.xlsx"           # Your Excel file
ADDRESS_COLUMN = "Địa chỉ giao hàng"    # Column with addresses
SHEET_NAME = None                       # None = first sheet
```

### Validation Rules

Control what makes an address "valid" (in `config.py`):

```python
REQUIRE_PROVINCE = True     # Must have province
REQUIRE_DISTRICT = True     # Must have district
REQUIRE_WARD = False        # Must have ward (set True if needed)
MIN_COMMA_COUNT = 2         # Minimum address structure
```

---

## 🔧 Adding Custom Rules (Learning Over Time)

### Step 1: Identify Patterns

After each processing run, check:
1. `output/PROCESSED_addresses_summary.txt` - See what failed
2. `output/failed_addresses_log.txt` - Failed patterns
3. Excel output "Skipped Addresses" sheet

### Step 2: Add Cleaning Rules

If you find patterns that need cleaning, add to `config.py`:

```python
# In config.py, find CUSTOM_CLEANING_RULES section
CUSTOM_CLEANING_RULES = [
    (r'pattern_to_remove', ''),  # Add your patterns here
    (r'another_pattern', 'replacement'),
]
```

**Example - Remove company codes:**
```python
CUSTOM_CLEANING_RULES = [
    (r'COMPANY_CODE_\d+', ''),  # Remove company codes
    (r'\[Internal\]', ''),      # Remove internal markers
]
```

### Step 3: Add Skip Patterns

If certain addresses should always be skipped:

```python
# In config.py, find CUSTOM_SKIP_PATTERNS section
CUSTOM_SKIP_PATTERNS = [
    r'test.*address',      # Skip test addresses
    r'địa\s+chỉ\s+thử',   # Skip test addresses (Vietnamese)
]
```

### Step 4: Add Company-Specific Rules

For recurring clients/use cases, add to `custom_rules.py`:

```python
def clean_acme_company(address: str) -> str:
    """Clean ACME company addresses"""
    address = re.sub(r'ACME-\d+', '', address)
    return address

# Add to the list at bottom of file
CUSTOM_CLEANERS.append(clean_acme_company)
```

---

## 📊 Understanding Output Files

### 1. Main Excel File: `PROCESSED_addresses.xlsx`

**Sheet: "Valid Addresses"**
- ✅ Addresses that passed validation
- Has coordinates and standardized format
- **Use this for your system**

**Sheet: "Skipped Addresses"**
- ❌ Addresses that failed validation
- Shows `skip_reason` for each
- Review these to improve rules

### 2. CSV File: `PROCESSED_addresses_valid.csv`
- Same as "Valid Addresses" sheet
- Easy to import to databases
- UTF-8 encoding

### 3. Summary File: `PROCESSED_addresses_summary.txt`
- Human-readable summary
- Sample successful and failed addresses
- Skip reasons breakdown

### 4. Statistics File: `PROCESSED_addresses_stats.json`
- Machine-readable statistics
- Track improvement over time
- Compare different runs

---

## 🎓 Learning & Improving Over Time

### Workflow for Continuous Improvement

```
1. Process File
   ↓
2. Check Results
   - How many succeeded?
   - What failed and why?
   ↓
3. Identify Patterns
   - Common failure reasons
   - Similar address structures
   ↓
4. Add Rules
   - Update config.py
   - Add to custom_rules.py
   ↓
5. Re-process
   - Run main.py again
   - Compare statistics
   ↓
6. Iterate
   - Keep refining
   - Document learnings
```

### Tracking Improvement

Check `output/processing_statistics.json` after each run:

```json
{
  "timestamp": "2025-10-16T15:30:00",
  "success_rate": 23.1,    // Track this over time
  "total_addresses": 506,
  "successful": 117,
  "skip_reasons": {         // See what's failing
    "No province parsed": 196,
    "Warehouse pickup": 85
  }
}
```

**Goal:** Increase `success_rate` with each iteration!

---

## 💡 Common Use Cases

### Use Case 1: Process Different File

```python
# Edit config.py
INPUT_FILE = "new_client_addresses.xlsx"
ADDRESS_COLUMN = "delivery_address"
```

Then run: `python main.py`

### Use Case 2: More Lenient Processing

```python
# Edit config.py
PROCESSING_MODE = ProcessingMode.NORMAL  # or LENIENT
MIN_COMMA_COUNT = 1  # Less strict
REQUIRE_DISTRICT = False  # Don't require district
```

### Use Case 3: Company-Specific Processing

Create a new config file: `config_company.py`

```python
# Copy config.py to config_company.py
# Modify for that company

# Then run with:
# import config_company as config
```

### Use Case 4: Add New Cleaning Pattern

Found a new pattern to remove? Add it:

```python
# In config.py
PHONE_PATTERNS = [
    r'\d{9,11}',
    r'NEW_PATTERN_HERE',  # Add your new pattern
]
```

---

## 🔍 Debugging & Troubleshooting

### Problem: Low Success Rate

**Check:**
1. Is `PROCESSING_MODE` too strict?
2. Are addresses missing province/district?
3. Check `skip_reasons` in summary file

**Solution:**
- Use `ProcessingMode.NORMAL` instead of `STRICT`
- Lower `MIN_COMMA_COUNT`
- Set `REQUIRE_DISTRICT = False`

### Problem: Wrong Parses

**Check:**
- Look at "Valid Addresses" sheet
- Find incorrect addresses
- What pattern do they share?

**Solution:**
- Add validation rules in `config.py`
- Add custom validators in `custom_rules.py`

### Problem: Addresses Not Cleaning Properly

**Check:**
- Look at `cleaned_address` column
- What remains that shouldn't?

**Solution:**
- Add cleaning patterns to `config.py`
- Add custom cleaners to `custom_rules.py`

---

## 📈 Example: Improving From 23% to 50%

**Run 1: Initial (23% success)**
```
Skip reasons:
- No province parsed: 196
- Warehouse pickup: 85
```

**Add rules to config.py:**
```python
# Found pattern: addresses ending with province name
CUSTOM_CLEANING_RULES = [
    # Addresses like "Building X Thanh pho Ha Noi"
    # The city name is there but parser misses it
]
```

**Run 2: After improvements (35% success)**
```
Skip reasons:
- No province parsed: 150  # Improved!
- Warehouse pickup: 85
```

**Add more patterns, iterate...**

**Run 5: Optimized (50% success)**
```
Success rate doubled through learning!
```

---

## 🎯 Best Practices

### 1. Always Keep Backups
- Don't overwrite original files
- Keep history of config changes
- Save each run's statistics

### 2. Document What You Learn
```python
# In custom_rules.py, add comments
def clean_pattern_x(address):
    """
    Learned 2025-10-16: Client XYZ uses this format
    Example: "ABC-123 Street Name"
    Remove the "ABC-123" prefix
    """
    return re.sub(r'^[A-Z]{3}-\d{3}\s+', '', address)
```

### 3. Test Changes Incrementally
- Add one rule at a time
- Check if it helps or hurts
- Keep statistics to compare

### 4. Use Version Control
```bash
git add config.py custom_rules.py
git commit -m "Added rules for Client XYZ addresses"
```

---

## 📞 Quick Reference

### Essential Files to Edit:
- ✏️ `config.py` - Settings and rules
- ✏️ `custom_rules.py` - Custom logic

### Don't Usually Edit:
- 👀 `main.py` - Core logic (only modify for major changes)
- 👀 `vietnamadminunits/` - Library code

### Always Check:
- 📊 `output/PROCESSED_addresses.xlsx` - Results
- 📊 `output/PROCESSED_addresses_summary.txt` - Summary
- 📊 `output/PROCESSED_addresses_stats.json` - Statistics

---

## 🚀 Next Steps

1. **Run first processing**: `python main.py`
2. **Review results**: Check output folder
3. **Identify improvements**: Look at skipped addresses
4. **Add rules**: Update config.py
5. **Re-run**: `python main.py` again
6. **Repeat**: Keep improving!

---

**Remember:** This system learns with you. The more you use it and refine the rules, the better it becomes! 🎯

