from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

from .sample_data import build_sample_corpus
from .storage import as_json, resolve_store


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"


RAW_BUCKET = "raw"
PROCESSED_BUCKET = "processed"
CURATED_BUCKET = "curated"


def _load_documents(csv_path: str) -> List[Dict[str, str]]:
    with Path(csv_path).open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def _extract_metadata(document: Dict[str, str]) -> Dict[str, object]:
    tokens = document["text"].split()
    return {
        "document_id": document["document_id"],
        "file_name": document["file_name"],
        "document_type": document["document_type"],
        "source_system": document["source_system"],
        "owner_team": document["owner_team"],
        "character_count": len(document["text"]),
        "word_count": len(tokens),
        "contains_numeric_signal": any(char.isdigit() for char in document["text"]),
        "summary": " ".join(tokens[:18]),
    }


def _build_curated_record(metadata: Dict[str, object]) -> Dict[str, object]:
    doc_type = str(metadata["document_type"])
    classification = {
        "contract": "legal_operational_document",
        "invoice": "finance_document",
        "maintenance_report": "maintenance_signal_document",
        "shipment_notice": "supply_chain_document",
        "policy": "governance_document",
        "inspection_checklist": "field_readiness_document",
    }.get(doc_type, "other_document")

    return {
        "document_id": metadata["document_id"],
        "document_type": doc_type,
        "classification": classification,
        "storage_layer": CURATED_BUCKET,
        "summary": metadata["summary"],
    }


def run_pipeline() -> Dict[str, object]:
    sample_info = build_sample_corpus()
    runtime_mode, store = resolve_store()
    documents = _load_documents(sample_info["csv_path"])

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    processed_records: List[Dict[str, object]] = []
    curated_records: List[Dict[str, object]] = []

    for document in documents:
        raw_object_name = document["file_name"]
        store.put_text(RAW_BUCKET, raw_object_name, document["text"])

        metadata = _extract_metadata(document)
        processed_object_name = f"{document['document_id']}.json"
        store.put_text(PROCESSED_BUCKET, processed_object_name, as_json(metadata))
        processed_records.append(metadata)

        curated = _build_curated_record(metadata)
        curated_object_name = f"{document['document_id']}.json"
        store.put_text(CURATED_BUCKET, curated_object_name, as_json(curated))
        curated_records.append(curated)

    report = {
        "dataset_source": sample_info["dataset_source"],
        "runtime_mode": runtime_mode,
        "document_count": len(documents),
        "raw_object_count": len(store.list_objects(RAW_BUCKET)),
        "processed_object_count": len(store.list_objects(PROCESSED_BUCKET)),
        "curated_object_count": len(store.list_objects(CURATED_BUCKET)),
        "document_types": sorted({doc["document_type"] for doc in documents}),
        "maintenance_signal_documents": sum(
            1 for record in curated_records if record["classification"] == "maintenance_signal_document"
        ),
        "report_artifact": str(PROCESSED_DIR / "document_intelligence_minio_report.json"),
    }

    report_path = Path(report["report_artifact"])
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ARTIFACTS_DIR / "curated_documents.json").write_text(
        json.dumps(curated_records, indent=2), encoding="utf-8"
    )
    return report
