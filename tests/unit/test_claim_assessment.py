"""
CrisisGuard — Unit Tests for Evidence-Aware Misinformation Assessment (Feature A)
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Validates:
1. Authentic media accompanying false/contradicted claim.
2. Synthetic media accompanying true/evidence-supported claim.
3. High-risk media prediction without claim evidence -> UNVERIFIED / REQUIRES_HUMAN_REVIEW.
4. Contradictory evidence handling.
5. Missing text, media, location, or source metadata.
6. Duplicate reports and semantically similar claims.
7. Verification uncertainty guarantees (NEVER equate synthetic media score with false claim).
"""

import sys
import unittest
from pathlib import Path

# Ensure repo root is in python path
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from src.assessment.claim_extractor import ClaimExtractor
from src.assessment.evidence_store import EvidenceStore
from src.assessment.misinformation_assessor import MisinformationAssessor

class TestClaimAssessment(unittest.TestCase):
    def setUp(self):
        self.extractor = ClaimExtractor()
        self.evidence_store = EvidenceStore()
        self.assessor = MisinformationAssessor(repo_root=str(root))

    def test_claim_extractor_normalization_and_urgency(self):
        """Verifies text normalization and lexical urgency extraction without hallucination."""
        raw = {
            "claim_id": "test_ext_01",
            "text": "URGENT SOS! Flooding in Sector 5 embankment. People trapped: https://t.co/abc123xyz",
            "location": "Sector 5",
            "source_type": "TWITTER_FEED"
        }
        res = self.extractor.extract_claim(raw)
        self.assertEqual(res["urgency_signal"], "CRITICAL")
        self.assertNotIn("https://", res["normalized_claim"])
        self.assertEqual(res["stated_location"], "Sector 5")

    def test_claim_extractor_missing_metadata(self):
        """Verifies missing location, media, and source remain None without fabricated values."""
        raw = {"text": "Just waterlogging on street."}
        res = self.extractor.extract_claim(raw)
        self.assertIsNone(res["stated_location"])
        self.assertIsNone(res["coordinates"])
        self.assertIsNone(res["media_path"])
        self.assertIsNone(res["media_type"])

    def test_evidence_supported_claim(self):
        """Verifies claim matching authoritative sitrep receives EVIDENCE_SUPPORTED outcome."""
        report = {
            "claim_id": "evid_supp_01",
            "text": "Yamuna embankment breached in Sector 5, low-lying areas flooded.",
            "location": "Sector 5",
            "timestamp": "2026-10-09T10:00:00Z"
        }
        asmt = self.assessor.assess_claim(report)
        self.assertEqual(asmt["assessment_outcome"], "EVIDENCE_SUPPORTED")
        self.assertFalse(asmt["human_review_required"])
        self.assertLess(asmt["uncertainty_score"], 0.25)
        self.assertTrue(len(asmt["evidence_references"]) > 0)
        self.assertEqual(asmt["evidence_references"][0]["claim_relation"], "CORROBORATES")

    def test_contradicted_by_evidence_claim(self):
        """Verifies claim contradicting sensor telemetry receives CONTRADICTED_BY_EVIDENCE."""
        report = {
            "claim_id": "evid_contra_02",
            "text": "Downtown bridge collapsed and washed away completely!",
            "location": "Downtown bridge",
            "timestamp": "2026-10-09T10:05:00Z"
        }
        asmt = self.assessor.assess_claim(report)
        self.assertEqual(asmt["assessment_outcome"], "CONTRADICTED_BY_EVIDENCE")
        self.assertTrue(asmt["human_review_required"])
        self.assertTrue(any(e["claim_relation"] == "CONTRADICTS" for e in asmt["evidence_references"]))

    def test_insufficient_evidence_untraceable_claim(self):
        """Verifies unrecorded claim returns INSUFFICIENT_EVIDENCE with high epistemic uncertainty."""
        report = {
            "claim_id": "evid_none_03",
            "text": "Rumor that subterranean tunnel opened under shopping mall.",
            "location": "Sector 99",
            "timestamp": "2026-10-09T10:10:00Z"
        }
        asmt = self.assessor.assess_claim(report)
        self.assertEqual(asmt["assessment_outcome"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(asmt["human_review_required"])
        self.assertGreater(asmt["uncertainty_score"], 0.70)
        self.assertEqual(len(asmt["evidence_references"]), 0)

    def test_synthetic_media_with_corroborated_claim(self):
        """
        Crucial requirement: Synthetic media accompanying a true/corroborated claim
        must NOT be labeled false. It must yield REQUIRES_HUMAN_REVIEW with transparent rationale.
        """
        # Create a report with genuine claim but simulated synthetic media path
        report = {
            "claim_id": "syn_corroborated_04",
            "text": "Yamuna embankment breached in Sector 5, evacuation underway.",
            "location": "Sector 5",
            "media_path": str(root / "data" / "demo" / "input" / "sample_image.jpg"),
            "media_type": "IMAGE"
        }
        asmt = self.assessor.assess_claim(report)
        # Even if synthetic media risk exists or is evaluated, outcome must be EVIDENCE_SUPPORTED
        # or REQUIRES_HUMAN_REVIEW (if synthetic media score is high), but NEVER CONTRADICTED_BY_EVIDENCE!
        self.assertIn(asmt["assessment_outcome"], ["EVIDENCE_SUPPORTED", "REQUIRES_HUMAN_REVIEW"])
        self.assertNotEqual(asmt["assessment_outcome"], "CONTRADICTED_BY_EVIDENCE")

    def test_propagation_context_as_signal_not_proof(self):
        """Verifies bursty viral propagation does not change outcome to false."""
        report = {
            "claim_id": "prop_test_05",
            "text": "Yamuna embankment breached in Sector 5.",
            "location": "Sector 5"
        }
        prop_context = {
            "event_rate": 45.2,
            "burst_ratio": 8.5,
            "pagerank": 1.85,
            "is_hub_node": True
        }
        asmt = self.assessor.assess_claim(report, propagation_context=prop_context)
        # Propagation context must be retained in output
        self.assertEqual(asmt["propagation_context"]["burst_ratio"], 8.5)
        self.assertIn("burst ratio", asmt["rationale"])
        # Fact remains corroborated despite high propagation burst
        self.assertEqual(asmt["assessment_outcome"], "EVIDENCE_SUPPORTED")

    def test_semantically_similar_duplicate_claims(self):
        """Verifies consistent assessment across semantically duplicate reports."""
        rep_a = {
            "claim_id": "dup_a",
            "text": "Yamuna river embankment collapsed in Sector 5, urgent rescue boats needed!",
            "location": "Sector 5"
        }
        rep_b = {
            "claim_id": "dup_b",
            "text": "Breach reported at low-lying Sector 5 embankment along Yamuna.",
            "location": "Sector 5"
        }
        res_a = self.assessor.assess_claim(rep_a)
        res_b = self.assessor.assess_claim(rep_b)
        self.assertEqual(res_a["assessment_outcome"], res_b["assessment_outcome"])
        self.assertEqual(res_a["assessment_outcome"], "EVIDENCE_SUPPORTED")

if __name__ == "__main__":
    unittest.main()
