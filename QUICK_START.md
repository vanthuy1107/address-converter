# ⚡ Quick Start - Address Processing System

## 🎯 Use It Right Now

```bash
python main.py
```

That's it! Results will be in the `output/` folder.

---

## 📝 For Next Time (Different File)

### Step 1: Edit `config.py`

Change lines 22-24:

```python
INPUT_FILE = "your_new_file.xlsx"           # ← Your file here
ADDRESS_COLUMN = "your_address_column"      # ← Your column name
SHEET_NAME = None                           # ← Or specify sheet name
```

### Step 2: Run

```bash
python main.py
```

Done!

---

## ⚙️ Change Processing Mode

In `config.py`, line 41:

```python
# For OLD→NEW conversion (handles 2025 mergers): ⭐ BEST!
PROCESSING_MODE = ProcessingMode.CONVERT

# For highest quality (no conversion):
PROCESSING_MODE = ProcessingMode.STRICT

# For balanced:
PROCESSING_MODE = ProcessingMode.NORMAL

# For maximum coverage:
PROCESSING_MODE = ProcessingMode.LENIENT
```

---

## 📊 Check Results

All outputs are in the `output/` folder:

1. **`PROCESSED_addresses.xlsx`** ← Main file
   - Sheet 1: Valid addresses with coordinates
   - Sheet 2: Skipped addresses with reasons

2. **`PROCESSED_addresses_valid.csv`** ← CSV format

3. **`PROCESSED_addresses_summary.txt`** ← Human-readable summary

4. **`PROCESSED_addresses_stats.json`** ← Statistics

---

## 🔧 Add New Cleaning Rules

### If you find patterns that need to be removed:

Edit `config.py`, find line ~70:

```python
CUSTOM_CLEANING_RULES = [
    (r'your_pattern_here', ''),      # ← Add patterns to remove
    (r'another_pattern', 'replace'), # ← Or replacements
]
```

### Examples:

```python
CUSTOM_CLEANING_RULES = [
    (r'#REF\d+', ''),           # Remove reference numbers
    (r'INTERNAL:', ''),         # Remove internal labels
    (r'\[.*?\]', ''),           # Remove [...] brackets
]
```

---

## 🚫 Skip Certain Addresses

Edit `config.py`, find line ~210:

```python
CUSTOM_SKIP_PATTERNS = [
    r'test',                    # Skip test addresses
    r'warehouse.*pickup',       # Skip warehouse pickups
    # Add your patterns here
]
```

---

## 📈 Track Improvement

After each run, check `output/PROCESSED_addresses_stats.json`:

```json
{
  "success_rate": 22.7    ← Try to increase this over time
}
```

Add rules → Run again → Check if success_rate increased!

---

## 💡 Common Adjustments

### Too Few Results (Want More Addresses)?

```python
# In config.py
PROCESSING_MODE = ProcessingMode.NORMAL    # Less strict
MIN_COMMA_COUNT = 1                        # Less strict structure
REQUIRE_DISTRICT = False                   # Don't require district
```

### Too Many Bad Results?

```python
# In config.py
PROCESSING_MODE = ProcessingMode.STRICT    # More strict
MIN_COMMA_COUNT = 2                        # Require proper structure
REQUIRE_WARD = True                        # Require ward level
```

---

## 📚 Need More Help?

- **Comprehensive guide**: `HOW_TO_USE.md`
- **All settings explained**: `config.py` (has comments)
- **Custom rules**: `custom_rules.py`

---

## 🎓 Learning Over Time

```
1. Run: python main.py
   ↓
2. Check: output/PROCESSED_addresses.xlsx
   ↓
3. Review: Skipped Addresses sheet
   ↓
4. Add rules: Update config.py
   ↓
5. Run again: python main.py
   ↓
6. Compare: Check if success_rate improved
```

**The more you use it, the smarter it gets!** 🧠

---

## Files You'll Edit:

- ✏️ `config.py` - Settings (95% of the time, edit this)
- ✏️ `custom_rules.py` - Complex custom logic (rarely needed)

## Files You'll Check:

- 📊 `output/PROCESSED_addresses.xlsx` - Results
- 📊 `output/PROCESSED_addresses_summary.txt` - Summary

## Files You Won't Touch:

- 👀 `main.py` - Core logic (rarely modify)
- 👀 `vietnamadminunits/` - Library

---

**Recommended**: Use `CONVERT` mode to handle 2025 administrative changes! 🔄  
Or use `STRICT` mode if you don't need conversion. 🎯

