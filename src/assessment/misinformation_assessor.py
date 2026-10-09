"""
CrisisGuard — Evidence-Aware Misinformation Assessment Engine
Author: B.SIVASAI (Roll Number: 2023BCS0228)
Course: CSE412 — Big Data & Large-Scale Computing

Core implementation for Feature A:
1. Ingests crisis reports across text and optional media (image/video).
2. Extracts normalized claim, urgency signals, and requested resources without hallucination.
3. Classifies crisis category and humanitarian prior using validated Phase 7 CrisisMMD model.
4. Executes synthetic-media forensics using Phase 6 ResNet-18 (Platt-calibrated for image) or Temporal (video).
5. Queries EvidenceStore for traceable reference records (NDMA, CWC telemetry, municipal logs, fire dispatch).
6. Separates synthetic-media forensics from claim verification (NEVER combines into an arbitrary score).
7. Evaluates propagation context as observational signals rather than deception proof.
8. Emits schema-compliant assessments matching schemas/assessment/assessment_schema.json.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

import jsonschema

# Local modules
from src.assessment.claim_extractor import ClaimExtractor
from src.assessment.evidence_store import EvidenceStore

logger = logging.getLogger("CrisisGuard.Assessment")

VALID_CRISIS_CATEGORIES = [
    "affected_individuals",
    "infrastructure_and_utility_damage",
    "not_humanitarian",
    "other_relevant_information",
    "rescue_volunteering_or_donation_effort",
    "unclassified"
]

class MisinformationAssessor:
    def __init__(self, repo_root: Optional[str] = None):
        if repo_root is None:
            self.root = Path(__file__).resolve().parent.parent.parent
        else:
            self.root = Path(repo_root)

        self.claim_extractor = ClaimExtractor()
        self.evidence_store = EvidenceStore()
        
        # Load JSON Schema
        schema_path = self.root / "schemas" / "assessment" / "assessment_schema.json"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        else:
            self.schema = None
            logger.warning(f"Assessment schema not found at {schema_path}")

        # Lazy load crisis classification model
        self.vectorizer = None
        self.text_model = None
        self._init_text_model()

        # Media inference engine placeholder
        self.media_engine = None

    def _init_text_model(self):
        vec_path = self.root / "models" / "crisis_information" / "crisismmd" / "crisismmd_tfidf_vectorizer.joblib"
        model_path = self.root / "models" / "crisis_information" / "crisismmd" / "crisismmd_baseline_logistic.joblib"
        if vec_path.exists() and model_path.exists():
            try:
                import joblib
                self.vectorizer = joblib.load(vec_path)
                self.text_model = joblib.load(model_path)
                logger.info("Loaded CrisisMMD TF-IDF + Logistic Regression model.")
            except Exception as e:
                logger.warning(f"Could not load CrisisMMD text model: {e}")

    def _init_media_engine(self):
        if self.media_engine is None:
            try:
                sys.path.append(str(self.root / "scripts" / "synthetic_media"))
                from infer_media import UnifiedMediaInferenceEngine
                config_path = str(self.root / "config" / "synthetic_media.yaml")
                self.media_engine = UnifiedMediaInferenceEngine(config_path=config_path)
                logger.info("Initialized UnifiedMediaInferenceEngine.")
            except Exception as e:
                logger.warning(f"Could not initialize media inference engine: {e}")

    def classify_text(self, text: str) -> tuple[str, float]:
        """Classifies crisis text into standard categories with confidence."""
        if not text or not self.vectorizer or not self.text_model:
            return "unclassified", 0.0

        try:
            categories = [
                "affected_individuals",
                "infrastructure_and_utility_damage",
                "not_humanitarian",
                "other_relevant_information",
                "rescue_volunteering_or_donation_effort"
            ]
            X = self.vectorizer.transform([text])
            pred_idx = int(self.text_model.predict(X)[0])
            probs = self.text_model.predict_proba(X)[0]
            cat_name = categories[pred_idx] if pred_idx < len(categories) else "other_relevant_information"
            return cat_name, round(float(probs[pred_idx]), 4)
        except Exception as e:
            logger.warning(f"Text classification error: {e}")
            return "unclassified", 0.0

    def assess_media(self, media_path: Optional[str], media_type: Optional[str]) -> tuple[Optional[float], str]:
        """
        Runs synthetic media forensics.
        Returns (synthetic_risk, calibration_status).
        """
        if not media_path or not Path(media_path).exists():
            return None, "NOT_APPLICABLE"

        self._init_media_engine()
        if not self.media_engine:
            return None, "NOT_APPLICABLE"

        try:
            mtype = (media_type or "").upper()
            if mtype == "IMAGE" or media_path.lower().endswith((".jpg", ".jpeg", ".png")):
                rec = self.media_engine.infer_image(media_path, content_id=f"img_{uuid.uuid4().hex[:6]}")
                risk = rec.get("synthetic_media_risk")
                status = rec.get("calibration_status", "CALIBRATED_PLATT")
                return risk, status
            elif mtype == "VIDEO" or media_path.lower().endswith((".mp4", ".avi", ".mov")):
                rec = self.media_engine.infer_video(media_path, content_id=f"vid_{uuid.uuid4().hex[:6]}")
                risk = rec.get("synthetic_media_risk")
                return risk, "UNCALIBRATED"
        except Exception as e:
            logger.warning(f"Media inference failed: {e}")
            return None, "NOT_APPLICABLE"

        return None, "NOT_APPLICABLE"

    def assess_claim(self, raw_report: Dict[str, Any], propagation_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes end-to-end evidence-aware claim assessment.
        Ensures strict separation between synthetic media risk and claim veracity.
        """
        # Step 1: Extraction & Normalization
        extracted = self.claim_extractor.extract_claim(raw_report)
        normalized_text = extracted["normalized_claim"]
        raw_text = extracted["raw_text"]
        location = extracted["stated_location"]

        # Step 2: Crisis classification
        cat, cat_conf = self.classify_text(normalized_text)

        # Step 3: Synthetic media forensics
        media_present = bool(extracted.get("media_path") and Path(extracted["media_path"]).exists())
        syn_risk, cal_status = self.assess_media(extracted.get("media_path"), extracted.get("media_type"))

        # Step 4: Evidence retrieval from authentic traceable baseline
        evidence_records = self.evidence_store.query_evidence(normalized_text, location=location)

        # Step 5: Claim verification logic based on verifiable evidence
        has_contradiction = any(e["claim_relation"] == "CONTRADICTS" for e in evidence_records)
        has_corroboration = any(e["claim_relation"] == "CORROBORATES" for e in evidence_records)

        # Determine outcome and rationale
        if has_contradiction:
            outcome = "CONTRADICTED_BY_EVIDENCE"
            review_required = True
            uncertainty = 0.15  # Low uncertainty because authoritative contradiction exists
            contradiction_details = "; ".join([e["detail"] for e in evidence_records if e["claim_relation"] == "CONTRADICTS"])
            rationale = f"Claim is directly contradicted by verified reference evidence: {contradiction_details}."
            if syn_risk is not None and syn_risk > 0.5:
                rationale += f" Attached media also exhibits high synthetic-media risk ({syn_risk:.2f})."
        elif has_corroboration:
            outcome = "EVIDENCE_SUPPORTED"
            # If media is synthetic but claim fact is corroborated, flag for human review
            if syn_risk is not None and syn_risk > 0.65:
                outcome = "REQUIRES_HUMAN_REVIEW"
                review_required = True
                uncertainty = 0.35
                corroboration_details = "; ".join([e["detail"] for e in evidence_records if e["claim_relation"] == "CORROBORATES"])
                rationale = (f"Claim fact is corroborated by official records ({corroboration_details}), "
                             f"but accompanying media exhibits high synthetic risk ({syn_risk:.2f}, {cal_status}). "
                             f"Human review required to confirm whether media is synthetic illustration of real event.")
            else:
                review_required = False
                uncertainty = 0.10
                corroboration_details = "; ".join([e["detail"] for e in evidence_records if e["claim_relation"] == "CORROBORATES"])
                rationale = f"Claim is corroborated by traceable authority evidence: {corroboration_details}."
        else:
            # No direct corroboration or contradiction
            if len(evidence_records) > 0:
                outcome = "UNVERIFIED"
                review_required = True
                uncertainty = 0.60
                rationale = "Available reference records are inconclusive regarding the specific factual assertions in this report."
            else:
                outcome = "INSUFFICIENT_EVIDENCE"
                review_required = True
                uncertainty = 0.85
                rationale = "Zero traceable reference records, official situation reports, or sensor telemetry available for this incident or location."

            # If media shows high synthetic risk on unverified claim, require review
            if syn_risk is not None and syn_risk > 0.60:
                outcome = "REQUIRES_HUMAN_REVIEW"
                rationale += f" High synthetic-media risk ({syn_risk:.2f}) detected on unverified claim; triage needed."

        # Step 6: Propagation context integration (purely contextual, non-falsifying)
        prop_data = {
            "event_rate": None,
            "burst_ratio": None,
            "pagerank": None,
            "is_hub_node": None
        }
        if propagation_context:
            for k in prop_data:
                if k in propagation_context:
                    prop_data[k] = propagation_context[k]
            if prop_data.get("burst_ratio") and prop_data["burst_ratio"] > 3.0:
                rationale += f" [Context: High viral burst ratio {prop_data['burst_ratio']:.1f}x observed in propagation stream]."

        # Step 7: Construct final assessment record
        assessment_record = {
            "assessment_id": f"asmt_{uuid.uuid4().hex[:10]}",
            "claim_id": str(extracted["claim_id"]),
            "report_text": raw_text,
            "extracted_claim": normalized_text,
            "crisis_category": cat,
            "category_confidence": cat_conf,
            "media_present": media_present,
            "media_type": extracted.get("media_type") if media_present else None,
            "synthetic_media_risk": syn_risk,
            "calibration_status": cal_status,
            "propagation_context": prop_data,
            "evidence_references": evidence_records,
            "assessment_outcome": outcome,
            "rationale": rationale,
            "uncertainty_score": uncertainty,
            "human_review_required": review_required,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provenance": "crisisguard_evidence_aware_assessor_v1"
        }

        # Step 8: Validate against JSON schema
        if self.schema:
            try:
                jsonschema.validate(instance=assessment_record, schema=self.schema)
            except jsonschema.ValidationError as ve:
                logger.error(f"Schema validation error in assessment record: {ve.message}")
                raise ve

        return assessment_record
