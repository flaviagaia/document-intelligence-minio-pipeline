from __future__ import annotations

import unittest

from src.pipeline import run_pipeline


class DocumentIntelligenceMinioPipelineTestCase(unittest.TestCase):
    def test_pipeline_contract(self) -> None:
        summary = run_pipeline()
        self.assertEqual(summary["dataset_source"], "document_intelligence_minio_local_sample")
        self.assertIn(summary["runtime_mode"], ["minio_s3_api", "local_filesystem_fallback"])
        self.assertEqual(summary["document_count"], 6)
        self.assertEqual(summary["raw_object_count"], 6)
        self.assertEqual(summary["processed_object_count"], 6)
        self.assertEqual(summary["curated_object_count"], 6)
        self.assertGreaterEqual(summary["maintenance_signal_documents"], 1)


if __name__ == "__main__":
    unittest.main()
