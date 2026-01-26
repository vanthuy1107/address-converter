# 🎯 Address Processing System - Overview

## ✅ What You Have Now

A **reusable, learning address processing system** that can be customized for any case.

---

## 📁 Main Files

### 🔧 Files You'll Edit:

| File | Purpose | Edit Frequency |
|------|---------|----------------|
| **`config.py`** | All settings and rules | **95% of the time** |
| **`custom_rules.py`** | Complex custom logic | **5% of the time** |

### 🚀 Files You'll Run:

| File | Purpose |
|------|---------|
| **`main.py`** | Main processing script - just run it! |

### 📚 Documentation:

| File | What It Contains |
|------|------------------|
| **`QUICK_START.md`** | ⚡ Start here for immediate use |
| **`HOW_TO_USE.md`** | 📘 Complete guide with examples |
| **`SYSTEM_OVERVIEW.md`** | 📋 This file - system overview |

---

## 🎮 How To Use

### For HAFELE (or Current Case):
```bash
python main.py
```

### For New Client/File:
1. Edit `config.py` lines 22-24 (file name, column name)
2. Run: `python main.py`
3. Check `output/` folder for results

---

## 📊 Output Files

Every run creates files in `output/` folder:

| File | What It Contains |
|------|------------------|
| **`PROCESSED_addresses.xlsx`** | Main Excel with 2 sheets:<br/>• Valid Addresses (with coordinates)<br/>• Skipped Addresses (with reasons) |
| **`PROCESSED_addresses_valid.csv`** | CSV format of valid addresses |
| **`PROCESSED_addresses_summary.txt`** | Human-readable summary |
| **`PROCESSED_addresses_stats.json`** | Machine-readable statistics |
| **`failed_addresses_log.txt`** | Learning log for failures |
| **`successful_patterns_log.txt`** | Learning log for successes |

---

## 🎓 Learning Process

### The System Learns With You:

```
┌─────────────────────────────────────────────────────────┐
│  CASE 1: Process HAFELE addresses                       │
│  → Learn patterns from HAFELE data                      │
│  → Add HAFELE-specific rules to config.py              │
│  → Success rate: 22.7%                                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  CASE 2: Process Client XYZ addresses                   │
│  → Reuse HAFELE rules + add XYZ-specific rules         │
│  → Success rate improves because system learned!        │
│  → Success rate: 35%                                    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  CASE 3: Process another case                           │
│  → System now has rules from HAFELE + XYZ + ...        │
│  → Success rate: 50%+                                   │
│  → System becomes smarter over time! 🧠                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Levels

### Level 1: Basic (Most Common)
**Edit `config.py` only**

Change these settings:
- `INPUT_FILE` - Your file name
- `ADDRESS_COLUMN` - Your column name
- `PROCESSING_MODE` - STRICT/NORMAL/LENIENT

**Example:**
```python
INPUT_FILE = "new_client.xlsx"
ADDRESS_COLUMN = "delivery_address"
PROCESSING_MODE = ProcessingMode.STRICT
```

### Level 2: Add Rules
**Edit `config.py` - Add patterns**

Add cleaning patterns:
```python
CUSTOM_CLEANING_RULES = [
    (r'#REF\d+', ''),  # Remove your pattern
]
```

Add skip patterns:
```python
CUSTOM_SKIP_PATTERNS = [
    r'warehouse',      # Skip your pattern
]
```

### Level 3: Advanced (Rare)
**Edit `custom_rules.py` - Complex logic**

Add custom functions:
```python
def clean_special_case(address):
    # Your complex logic here
    return cleaned_address

CUSTOM_CLEANERS.append(clean_special_case)
```

---

## 📈 Success Metrics

After each run, check **`output/PROCESSED_addresses_stats.json`**:

```json
{
  "success_rate": 22.73,        ← Main metric to track
  "total_addresses": 506,
  "successful": 115,
  "with_coordinates": 115,
  "with_ward": 91,              ← Higher = more precise
  "skip_reasons": {             ← What to improve
    "No province parsed": 170
  }
}
```

**Goal:** Increase `success_rate` with each iteration!

---

## 💡 Common Scenarios

### Scenario 1: New Client, Similar Format to HAFELE
```python
# In config.py
INPUT_FILE = "new_client.xlsx"
ADDRESS_COLUMN = "address"
# Keep all other settings the same!
```
**Result:** Should work immediately with ~20-25% success rate

### Scenario 2: Different Address Format
```python
# In config.py
INPUT_FILE = "client_b.xlsx"
# Add their specific cleaning patterns
CUSTOM_CLEANING_RULES = [
    (r'their_pattern', ''),
]
```
**Result:** Success rate improves based on patterns added

### Scenario 3: Want More Results (Lower Quality OK)
```python
# In config.py
PROCESSING_MODE = ProcessingMode.NORMAL  # or LENIENT
MIN_COMMA_COUNT = 1
REQUIRE_DISTRICT = False
```
**Result:** ~50-65% success rate, but lower quality

---

## 🎯 Best Practices

### 1. Start Strict, Then Adjust
Always start with `STRICT` mode first:
```python
PROCESSING_MODE = ProcessingMode.STRICT
```
Then adjust if needed.

### 2. Track Every Run
Keep the statistics files:
```
output/
  PROCESSED_addresses_stats_run1.json
  PROCESSED_addresses_stats_run2.json
  PROCESSED_addresses_stats_run3.json
```
Compare to see improvement!

### 3. Document What You Learn
Add comments in `config.py`:
```python
# 2025-10-16: Client XYZ uses this format
CUSTOM_CLEANING_RULES = [
    (r'XYZ_\d+', ''),  # Remove XYZ codes
]
```

### 4. Version Your Config
When you have good rules for a client:
```bash
cp config.py config_hafele.py
cp config.py config_client_xyz.py
```

### 5. Build Your Rule Library
Over time, you'll have:
- General rules (work for everyone)
- Client-specific rules (in separate configs)
- Industry-specific rules (e.g., logistics, retail)

---

## 🔄 Workflow Example

```
Week 1: HAFELE Case
├── Run: python main.py
├── Result: 22.7% success
├── Review: Check skipped addresses
├── Action: Add 3 cleaning rules
├── Re-run: python main.py
└── Result: 28% success ✅ Improved!

Week 2: Client ABC Case
├── Copy HAFELE rules
├── Edit config.py for ABC
├── Run: python main.py
├── Result: 35% success ✅ Better start!
└── (ABC benefited from HAFELE learnings)

Week 3: Client XYZ Case
├── Use rules from HAFELE + ABC
├── Add XYZ-specific rules
├── Run: python main.py
└── Result: 45% success ✅ Getting better!

Month 2: General Processing
├── Rules library is mature
├── Most cases: 40-60% success out of the box
└── System has learned a lot! 🎓
```

---

## 🎓 System Philosophy

> **"Every case teaches the system something new."**

- Case 1: Learn basic patterns
- Case 2: Learn variations
- Case 3: Learn edge cases
- Case 10: System is mature and smart!

The `config.py` and `custom_rules.py` files become your **knowledge base** that grows with experience.

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Success rate too low | Use `NORMAL` or `LENIENT` mode |
| Too many bad results | Use `STRICT` mode, increase `MIN_COMMA_COUNT` |
| Specific pattern failing | Add to `CUSTOM_CLEANING_RULES` |
| Addresses should be skipped | Add to `CUSTOM_SKIP_PATTERNS` |
| Need complex logic | Edit `custom_rules.py` |

---

## 📞 Quick Commands

```bash
# Run processing
python main.py

# Check results
cd output
dir    # Windows
ls     # Mac/Linux

# View statistics
cat PROCESSED_addresses_stats.json
```

---

## 🎯 Summary

✅ **What you built:**
- Reusable address processing system
- Configurable for any case
- Learns and improves over time

✅ **How to use it:**
1. Edit `config.py` (95% of the time)
2. Run `python main.py`
3. Check `output/` folder
4. Add learnings back to `config.py`

✅ **Key files:**
- `config.py` - Your settings
- `main.py` - Just run it
- `output/PROCESSED_addresses.xlsx` - Your results

✅ **Documentation:**
- `QUICK_START.md` - Start here
- `HOW_TO_USE.md` - Detailed guide
- `SYSTEM_OVERVIEW.md` - This overview

---

**You now have a smart address processing system that learns with you!** 🚀

