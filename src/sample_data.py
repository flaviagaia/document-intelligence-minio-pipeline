from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"


DOCUMENTS: List[Dict[str, object]] = [
    {
        "document_id": "DOC-1001",
        "file_name": "contract_vendor_a.txt",
        "document_type": "contract",
        "source_system": "vendor_portal",
        "owner_team": "procurement",
        "text": (
            "Service agreement for offshore inspection support. The supplier shall "
            "provide certified technicians and maintain safety documentation for every mobilization."
        ),
    },
    {
        "document_id": "DOC-1002",
        "file_name": "invoice_field_tools.txt",
        "document_type": "invoice",
        "source_system": "finance_mailbox",
        "owner_team": "accounts_payable",
        "text": (
            "Invoice for field tools rental covering pressure gauges, calibration kit, and freight. "
            "Payment term is net 30 days from approval."
        ),
    },
    {
        "document_id": "DOC-1003",
        "file_name": "maintenance_report_unit17.txt",
        "document_type": "maintenance_report",
        "source_system": "cmms_export",
        "owner_team": "maintenance",
        "text": (
            "Unit 17 reported abnormal vibration during night shift. Technician replaced the coupling, "
            "recorded oil contamination, and scheduled a follow-up inspection."
        ),
    },
    {
        "document_id": "DOC-1004",
        "file_name": "shipment_notice_valves.txt",
        "document_type": "shipment_notice",
        "source_system": "logistics_portal",
        "owner_team": "supply_chain",
        "text": (
            "Advance shipment notice for three pressure-control valves and one spare actuator. "
            "Expected arrival is Friday at the Rio warehouse."
        ),
    },
    {
        "document_id": "DOC-1005",
        "file_name": "policy_document_retention.txt",
        "document_type": "policy",
        "source_system": "knowledge_base",
        "owner_team": "compliance",
        "text": (
            "Retention policy requires maintenance and inspection records to be preserved for seven years. "
            "Access must be restricted to authorized operational and audit teams."
        ),
    },
    {
        "document_id": "DOC-1006",
        "file_name": "inspection_checklist_generator.txt",
        "document_type": "inspection_checklist",
        "source_system": "operations_workspace",
        "owner_team": "operations",
        "text": (
            "Checklist confirms hose integrity, seal condition, pressure tolerance, and emergency-stop validation "
            "before equipment dispatch."
        ),
    },
]


REFERENCE = {
    "storage_runtime": "MinIO S3-compatible object storage",
    "design_note": (
        "The project is structured around MinIO buckets named raw, processed, and curated. "
        "A deterministic local filesystem fallback is kept for reproducible execution."
    ),
    "integration_hint": (
        "Set MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, and optionally MINIO_SECURE "
        "to run the object-storage path against a live MinIO server."
    ),
}


def build_sample_corpus() -> Dict[str, str]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = RAW_DIR / "incoming_documents.csv"
    json_path = RAW_DIR / "storage_reference.json"

    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "document_id",
                "file_name",
                "document_type",
                "source_system",
                "owner_team",
                "text",
            ],
        )
        writer.writeheader()
        writer.writerows(DOCUMENTS)

    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(REFERENCE, json_file, indent=2)

    return {
        "dataset_source": "document_intelligence_minio_local_sample",
        "csv_path": str(csv_path),
        "reference_path": str(json_path),
    }
