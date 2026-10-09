"""
CrisisGuard — Evidence Store for Misinformation Assessment
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Stores traceable, authentic reference records, official situation reports,
and ground-truth sensor telemetry for evidence-aware claim assessment.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class EvidenceStore:
    def __init__(self):
        # Curated reference baseline records with spatial, temporal, and semantic bounds
        self.reference_records: List[Dict[str, Any]] = [
            {
                "source_id": "NDMA_SITREP_2026_09_FLOOD",
                "source_type": "OFFICIAL_DISASTER_AGENCY",
                "authority": "National Disaster Management Authority (NDMA)",
                "event_name": "Yamuna Basin Flood Triage",
                "keywords": ["embankment", "river", "breach", "bridge", "yamuna", "downtown", "evacuation"],
                "established_fact": "Yamuna river water level exceeded danger mark by 1.2m; Sector 5 low-lying embankment breached; evacuation advisory active.",
                "status_assertions": {
                    "embankment_breached": True,
                    "evacuation_active": True,
                    "boats_deployed": True,
                    "bridge_collapsed": False  # Crucial: Bridge is OPERATIONAL, not collapsed
                },
                "location_keywords": ["sector 5", "yamuna", "downtown", "delhi", "ito"],
                "temporal_validity": "2026-09-01T00:00:00Z/2026-10-31T23:59:59Z",
                "confidence": 0.99
            },
            {
                "source_id": "CWC_GAUGE_TELEMETRY_0884",
                "source_type": "GROUND_SENSOR_TELEMETRY",
                "authority": "Central Water Commission (CWC)",
                "event_name": "Old Railway Bridge Water Gauge Telemetry",
                "keywords": ["gauge", "water level", "flow", "bridge", "railway"],
                "established_fact": "Water gauge reading 208.66m (High flood level). Railway bridge structure intact; monitored hourly.",
                "status_assertions": {
                    "bridge_collapsed": False,
                    "water_level_danger": True
                },
                "location_keywords": ["old railway bridge", "downtown bridge", "yamuna bridge"],
                "temporal_validity": "2026-09-01T00:00:00Z/2026-10-31T23:59:59Z",
                "confidence": 1.00
            },
            {
                "source_id": "MUNICIPAL_INFRA_LOG_7741",
                "source_type": "VERIFIED_MUNICIPAL_SITREP",
                "authority": "Delhi Municipal Corporation Emergency Cell",
                "event_name": "Power Grid & Substation Status",
                "keywords": ["power", "grid", "electricity", "substation", "blackout"],
                "established_fact": "Kashmere Gate 220kV Substation operational; localized 11kV feeder isolation in waterlogged Sector 5.",
                "status_assertions": {
                    "citywide_blackout": False,
                    "sector_5_power_cut": True
                },
                "location_keywords": ["kashmere gate", "sector 5", "civil lines"],
                "temporal_validity": "2026-09-01T00:00:00Z/2026-10-31T23:59:59Z",
                "confidence": 0.98
            },
            {
                "source_id": "FIRE_SERVICE_DISPATCH_LOG_112",
                "source_type": "EMERGENCY_DISPATCH_RECORD",
                "authority": "Delhi Fire & Rescue Services",
                "event_name": "Commercial Building Fire Log",
                "keywords": ["fire", "commercial", "chemical", "warehouse", "blaze"],
                "established_fact": "Industrial warehouse fire in Mayapuri Phase II contained; zero toxic chemical explosion.",
                "status_assertions": {
                    "chemical_cloud": False,
                    "fire_contained": True
                },
                "location_keywords": ["mayapuri", "phase 2", "industrial area"],
                "temporal_validity": "2026-09-01T00:00:00Z/2026-10-31T23:59:59Z",
                "confidence": 0.99
            }
        ]

    def add_reference_record(self, record: Dict[str, Any]):
        """Dynamically add verified situation report or sensor record."""
        self.reference_records.append(record)

    def query_evidence(self, text: str, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves matching evidence records based on semantic keywords,
        location matching, and factual assertions.
        """
        text_lower = text.lower()
        matched = []

        for ref in self.reference_records:
            # Check keyword match
            kw_matches = sum(1 for kw in ref["keywords"] if kw in text_lower)
            loc_match = False
            if location:
                loc_lower = location.lower()
                loc_match = any(lk in loc_lower for lk in ref["location_keywords"])
            else:
                loc_match = any(lk in text_lower for lk in ref["location_keywords"])

            if kw_matches >= 2 or (kw_matches >= 1 and loc_match):
                # Analyze relation: check for contradictory vs corroborating claims
                relation = "INCONCLUSIVE"
                detail = ref["established_fact"]

                # Specific contradiction checks
                if "bridge collapsed" in text_lower or "bridge destroyed" in text_lower or "bridge washed away" in text_lower:
                    if ref["status_assertions"].get("bridge_collapsed") is False:
                        relation = "CONTRADICTS"
                        detail = f"Contradicts verified ground telemetry ({ref['authority']}): bridge structure is verified intact and operational."
                elif "chemical cloud" in text_lower or "toxic explosion" in text_lower:
                    if ref["status_assertions"].get("chemical_cloud") is False:
                        relation = "CONTRADICTS"
                        detail = f"Contradicts official fire log ({ref['authority']}): fire contained with zero chemical hazard."
                elif "citywide blackout" in text_lower:
                    if ref["status_assertions"].get("citywide_blackout") is False:
                        relation = "CONTRADICTS"
                        detail = f"Contradicts municipal grid status ({ref['authority']}): grid operational; only localized sector isolations."
                elif "embankment breached" in text_lower or "embankment collapsed" in text_lower or ("embankment" in text_lower and ("breach" in text_lower or "collapsed" in text_lower or "broken" in text_lower)) or "flash flood" in text_lower:
                    if ref["status_assertions"].get("embankment_breached") is True:
                        relation = "CORROBORATES"
                        detail = f"Corroborates official SITREP ({ref['authority']}): low-lying embankment breach officially confirmed."
                elif "evacuation" in text_lower or "rescue boat" in text_lower:
                    if ref["status_assertions"].get("evacuation_active") is True:
                        relation = "CORROBORATES"
                        detail = f"Corroborates active advisory ({ref['authority']}): official evacuation underway."

                matched.append({
                    "source_id": ref["source_id"],
                    "source_type": ref["source_type"],
                    "claim_relation": relation,
                    "detail": detail,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

        return matched
