#!/usr/bin/env python3
"""
CrisisGuard — Phase 7: Text Preprocessing Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Provides deterministic, reproducible text normalization for crisis texts:
- Unicode NFKC normalization
- HTML entity unescaping
- URL normalization -> [URL]
- User mention normalization -> [USER]
- Whitespace and line break compaction
- Preservation of original raw text alongside cleaned output
"""

import re
import html
import unicodedata
from typing import Optional

def preprocess_crisis_text(text: Optional[str]) -> str:
    """Deterministically cleans crisis social media text without over-stripping content.
    
    Args:
        text: Raw input string or None
        
    Returns:
        Cleaned, normalized string. Returns empty string if input is None or empty.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
        
    # 1. Unicode NFKC normalization
    t = unicodedata.normalize("NFKC", text)
    
    # 2. HTML unescaping (e.g. &amp; -> &, &lt; -> <)
    t = html.unescape(t)
    
    # 3. URL normalization
    t = re.sub(r"https?://\S+|www\.\S+", "[URL]", t)
    
    # 4. User handle normalization
    t = re.sub(r"@\w+", "[USER]", t)
    
    # 5. Normalize newline and tab characters to spaces
    t = re.sub(r"[\r\n\t]+", " ", t)
    
    # 6. Compact multiple spaces
    t = re.sub(r"\s+", " ", t)
    
    return t.strip()

if __name__ == "__main__":
    test_cases = [
        "RT @RedCross: Evacuate NOW! Flooding reported on I-95 &amp; route 4: https://t.co/xyz123 \n\n Stay safe! #flood",
        None,
        "   Severe   wind damage in @TownHall    http://emergency.gov   ",
        "No special tokens here."
    ]
    print("Testing Preprocessing Engine:")
    for tc in test_cases:
        print(f"RAW  : {tc}")
        print(f"CLEAN: {preprocess_crisis_text(tc)}")
        print("-" * 50)
