"""
CrisisGuard — Claim Normalization and Extraction Module
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Extracts, normalizes, and parses crisis reports without inventing missing details.
Identifies key hazard entities, stated locations, urgency signals, and explicit resource requests.
"""

import re
from typing import Dict, Any, Optional, List

# Explicit urgency lexicon
CRITICAL_KEYWORDS = {
    "sos", "trapped", "drowning", "critical", "immediately", "dying", 
    "life-threatening", "casualty", "casualties", "submerged", "stranded"
}
HIGH_KEYWORDS = {
    "urgent", "evacuation", "evacuate", "breach", "collapsed", "fire", 
    "blaze", "flooding", "blackout", "hazard", "danger", "medic"
}
MEDIUM_KEYWORDS = {
    "advisory", "warning", "rising", "waterlogged", "isolated", "smoke", "damage"
}

# Resource keyword mappings
RESOURCE_KEYWORDS = {
    "RESCUE_BOAT": ["boat", "boats", "dinghy", "raft", "water rescue", "flooded rescue"],
    "AMBULANCE": ["ambulance", "medic", "paramedic", "injured", "hospital", "medical team"],
    "FIRE_TENDER": ["fire engine", "fire tender", "firefighter", "extinguish", "blaze"],
    "INFRASTRUCTURE_REPAIR_CREW": ["power grid", "transformer", "repair crew", "wire cut", "substation", "generator"],
    "RELIEF_SUPPLY_TRUCK": ["food", "drinking water", "rations", "blankets", "relief pack", "supplies"]
}

class ClaimExtractor:
    def __init__(self):
        pass

    def normalize_text(self, text: str) -> str:
        """Cleans and standardizes raw text without altering factual content."""
        if not text:
            return ""
        # Remove URLs
        cleaned = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Standardize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def extract_urgency(self, text: str) -> str:
        """Determines urgency level based strictly on explicit lexical evidence."""
        text_lower = text.lower()
        words = set(re.findall(r'\b[a-z\-]+\b', text_lower))
        
        if any(w in words for w in CRITICAL_KEYWORDS):
            return "CRITICAL"
        if any(w in words for w in HIGH_KEYWORDS):
            return "HIGH"
        if any(w in words for w in MEDIUM_KEYWORDS):
            return "MEDIUM"
        return "LOW"

    def extract_resource_demands(self, text: str) -> List[str]:
        """Identifies explicit resource requirements without inventing quantities."""
        text_lower = text.lower()
        demanded = []
        for res_type, keywords in RESOURCE_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                demanded.append(res_type)
        return demanded

    def extract_claim(self, raw_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses incoming report into a structured, normalized claim representation.
        Does not fabricate missing location, timestamp, or source.
        """
        raw_text = raw_report.get("text", "") or raw_report.get("report_text", "")
        claim_id = raw_report.get("claim_id") or raw_report.get("report_id") or raw_report.get("event_id", "claim_unknown")
        
        normalized = self.normalize_text(raw_text)
        urgency = self.extract_urgency(normalized)
        demanded_resources = self.extract_resource_demands(normalized)
        
        # Explicit location preservation
        location = raw_report.get("location")
        coordinates = raw_report.get("coordinates") or raw_report.get("location_coords")

        return {
            "claim_id": claim_id,
            "raw_text": raw_text,
            "normalized_claim": normalized,
            "urgency_signal": urgency,
            "demanded_resource_types": demanded_resources,
            "stated_location": location,
            "coordinates": coordinates,
            "timestamp": raw_report.get("timestamp") or raw_report.get("event_time"),
            "source_type": raw_report.get("source_type", "USER_REPORT"),
            "media_path": raw_report.get("media_path"),
            "media_type": raw_report.get("media_type")
        }
