# -*- coding: utf-8 -*-
"""
Convert OLD addresses (63-province, before 2025) → NEW addresses (34-province, after 2025).

Usage:
    python main_convert_to_2025.py

Input: Excel/file with addresses in OLD (63-province) format.
Output: Same file with parsed NEW (34-province) address + OLD address columns.
Configure INPUT_FILE, ADDRESS_COLUMN, etc. in config.py.
"""
import config

# Force mode: old → new (CONVERT)
config.PROCESSING_MODE = config.ProcessingMode.CONVERT
config.apply_mode_overrides()

from app.run_address_processing import main

if __name__ == "__main__":
    main()
