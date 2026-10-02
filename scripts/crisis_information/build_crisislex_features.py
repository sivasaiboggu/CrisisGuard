#!/usr/bin/env python3
"""
CrisisGuard — Phase 7: CrisisLex Linguistic & Contextual Feature Extraction
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Extracts domain-specific crisis lexicon indicators, event context, and surface
linguistic features from CrisisLex (88,015 records across 32 disaster events).
Strictly adheres to Step 14: Does NOT fabricate arbitrary severity or fake truth.
"""

import re
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd

# Domain lexicon patterns
CASUALTY_TERMS = set(["dead", "killed", "injured", "injury", "injuries", "casualty", "casualties", "death", "deaths", "hospital", "body", "bodies", "fatalities"])
DAMAGE_TERMS = set(["damage", "damaged", "destroy", "destroyed", "destruction", "collapse", "collapsed", "debris", "bridge", "road", "roads", "power", "blackout", "flooded", "underwater"])
RESCUE_TERMS = set(["rescue", "rescued", "shelter", "evacuate", "evacuation", "evacuations", "aid", "relief", "volunteer", "volunteers", "donation", "supplies", "redcross", "fema"])
ALERT_TERMS = set(["warning", "warnings", "alert", "alerts", "caution", "advisory", "emergency", "urgent", "watch", "siren", "danger", "hazard"])

def extract_lexicon_features(text: str) -> dict:
    if not text or not isinstance(text, str):
        return {
            "casualty_term_count": 0,
            "damage_term_count": 0,
            "rescue_term_count": 0,
            "alert_term_count": 0,
            "has_casualty_keyword": False,
            "has_damage_keyword": False,
            "has_rescue_keyword": False,
            "has_alert_keyword": False,
            "total_crisis_keywords": 0
        }
    
    tokens = re.findall(r"\b\w+\b", text.lower())
    token_set = set(tokens)
    
    c_count = len(token_set.intersection(CASUALTY_TERMS))
    d_count = len(token_set.intersection(DAMAGE_TERMS))
    r_count = len(token_set.intersection(RESCUE_TERMS))
    a_count = len(token_set.intersection(ALERT_TERMS))
    total_kw = c_count + d_count + r_count + a_count
    
    return {
        "casualty_term_count": c_count,
        "damage_term_count": d_count,
        "rescue_term_count": r_count,
        "alert_term_count": a_count,
        "has_casualty_keyword": c_count > 0,
        "has_damage_keyword": d_count > 0,
        "has_rescue_keyword": r_count > 0,
        "has_alert_keyword": a_count > 0,
        "total_crisis_keywords": total_kw
    }

def extract_surface_features(raw_text: str, clean_text: str) -> dict:
    raw = raw_text if isinstance(raw_text, str) else ""
    clean = clean_text if isinstance(clean_text, str) else ""
    
    char_len = len(clean)
    tokens = clean.split()
    token_count = len(tokens)
    
    # Uppercase ratio computed on raw text to capture shout/urgency intent
    alpha_chars = [c for c in raw if c.isalpha()]
    upper_chars = [c for c in alpha_chars if c.isupper()]
    upper_ratio = (len(upper_chars) / len(alpha_chars)) if alpha_chars else 0.0
    
    exclamation_count = raw.count("!")
    question_count = raw.count("?")
    url_count = raw.count("http://") + raw.count("https://")
    mention_count = raw.count("@")
    
    return {
        "char_length": char_len,
        "token_count": token_count,
        "uppercase_ratio": round(upper_ratio, 4),
        "exclamation_count": exclamation_count,
        "question_count": question_count,
        "url_count": url_count,
        "mention_count": mention_count
    }

def build_crisislex_features():
    print("=" * 65)
    print("CRISISGUARD PHASE 7: CRISISLEX LINGUISTIC & CONTEXT ENGINE")
    print("=" * 65)
    
    root = Path(__file__).resolve().parent.parent.parent
    input_path = root / "data" / "processed" / "crisislex" / "crisislex_records.parquet"
    out_dir = root / "data" / "features" / "crisis_information"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_parquet = out_dir / "crisislex_features.parquet"
    
    if not input_path.exists():
        raise FileNotFoundError(f"CrisisLex dataset not found at {input_path}")
        
    df = pd.read_parquet(input_path)
    print(f"Loaded CrisisLex dataset: {df.shape[0]} records, {df.shape[1]} columns")
    
    # Event-level message volume aggregation
    event_counts = df["disaster_event"].value_counts().to_dict()
    print(f"Aggregating context across {len(event_counts)} disaster events...")
    
    lex_records = []
    surface_records = []
    
    for idx, row in df.iterrows():
        raw_t = row["raw_text"]
        clean_t = row["clean_text"]
        
        lex_feat = extract_lexicon_features(clean_t)
        surf_feat = extract_surface_features(raw_t, clean_t)
        
        lex_records.append(lex_feat)
        surface_records.append(surf_feat)
        
    df_lex = pd.DataFrame(lex_records)
    df_surf = pd.DataFrame(surface_records)
    
    # Merge extracted features
    feat_df = df.copy()
    for col in df_lex.columns:
        feat_df[col] = df_lex[col]
    for col in df_surf.columns:
        feat_df[col] = df_surf[col]
        
    # Add event context
    feat_df["event_total_volume"] = feat_df["disaster_event"].map(event_counts)
    feat_df["provenance"] = "crisislex_t6_and_t26_processed"
    feat_df["feature_extraction_version"] = "crisislex_context_v1"
    
    print(f"Extracted linguistic & context features: {feat_df.shape[1]} total columns")
    print(f"Keyword presence summary:")
    print(f"  Casualty keywords: {feat_df['has_casualty_keyword'].sum()} ({feat_df['has_casualty_keyword'].mean()*100:.2f}%)")
    print(f"  Damage keywords:   {feat_df['has_damage_keyword'].sum()} ({feat_df['has_damage_keyword'].mean()*100:.2f}%)")
    print(f"  Rescue keywords:   {feat_df['has_rescue_keyword'].sum()} ({feat_df['has_rescue_keyword'].mean()*100:.2f}%)")
    print(f"  Alert keywords:    {feat_df['has_alert_keyword'].sum()} ({feat_df['has_alert_keyword'].mean()*100:.2f}%)")
    
    feat_df.to_parquet(out_parquet, index=False)
    print(f"\nSaved CrisisLex feature layer to: {out_parquet}")
    print(f"Output entity count: {len(feat_df)} rows")
    return True

if __name__ == "__main__":
    success = build_crisislex_features()
    sys.exit(0 if success else 1)
