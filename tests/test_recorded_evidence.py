"""Offline checks of the evidence shipped with this portfolio entry."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class RecordedEvidenceTests(unittest.TestCase):
    def test_published_regression_source_matches_recorded_hash(self):
        import hashlib

        regression = read_json("evidence/observations.json")["regression"]
        source = ROOT / "regression/test_ai_tutor_connection_lifecycle.py"
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         regression["test_sha256_final"])
        self.assertEqual(regression["total"], 9)

    def test_http_results_distinguish_response_from_cleanup(self):
        record = read_json("evidence/observations.json")
        before = record["before_single_http"]
        after = record["after_single_http"]
        self.assertEqual((before["status"], after["status"]), (200, 200))
        self.assertTrue(before["worker_alive"])
        self.assertFalse(after["worker_alive"])
        self.assertEqual(after["app_close_counts_before_fixture_cleanup"], [1])
