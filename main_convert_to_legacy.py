# -*- coding: utf-8 -*-
"""
Convert NEW addresses (34-province, after 2025) → OLD addresses (63-province, before 2025).

Usage:
    python main_convert_to_legacy.py

Input: Excel/file with addresses in NEW (34-province) format.
Output: Same file with parsed OLD (63-province) address + input (NEW) address columns.
Configure INPUT_FILE, ADDRESS_COLUMN, etc. in config.py.
"""
import config

# Force mode: new → old (CONVERT_TO_LEGACY)
config.PROCESSING_MODE = config.ProcessingMode.CONVERT_TO_LEGACY
config.apply_mode_overrides()

from run_address_processing import main

if __name__ == "__main__":
    main()
