import json
import unittest
from unittest.mock import MagicMock, patch
from analyzer.engine import ScoringEngine, ProjectAnalyzer
import pathlib

class TestScoring(unittest.TestCase):
    def setUp(self):
        self.scoring = ScoringEngine(project_type="qgis")

    def test_maint_score_penalty(self):
        # Case: Large project with many warnings
        # 28k lines, 686 warnings (no errors)
        modules_data = [{"lines": 28000, "functions": [{"complexity": 1}]}]
        # 686 warnings (started with 'W' or others)
        ruff_findings = [{"code": "W123"}] * 686
        
        score = self.scoring._get_maint_score(modules_data, ruff_findings)
        
        # Total lines = 28000
        # Line factor = 28000 / 100 = 280
        # Penalty base = 3 * 686 = 2058 (since they are warnings)
        # Lint penalty = (2058 / 280) * 5 = 7.35 * 5 = 36.75
        # Lint score = 100 - 36.75 = 63.25
        # Func score = 100 (comp 1)
        # Total score = 0.7*100 + 0.3*63.25 = 70 + 18.975 = 88.975
        
        self.assertLess(score, 90.0)
        self.assertGreater(score, 0.0)

    def test_bonus_capping(self):
        # Case: Score + Bonus >= 100 but there are findings
        modules_data = [{"lines": 100, "functions": [{"complexity": 1}]}]
        ruff_findings = [{"code": "W123"}] # One warning
        semantic = {"cycles": [], "metrics": {}, "missing_resources": []}
        
        # Mock modernization bonus to be 5.0
        with patch.object(ScoringEngine, '_get_modernization_bonus', return_value=5.0):
            scores = self.scoring.calculate_project_scores(
                modules_data, ruff_findings, None, semantic
            )
            # Maint score should be capped at 99.9
            self.assertEqual(scores['maint_score'], 99.9)

    def test_perfect_score_no_findings(self):
        modules_data = [{"lines": 100, "functions": [{"complexity": 1}]}]
        ruff_findings = []
        semantic = {"cycles": [], "metrics": {}, "missing_resources": []}

        scores = self.scoring.calculate_project_scores(
            modules_data, ruff_findings, None, semantic
        )
        self.assertEqual(scores['maint_score'], 100.0)

    @patch("subprocess.run")
    def test_ruff_flag_and_strict(self, mock_run):
        # Setup mock
        mock_run.return_value = MagicMock(stdout='[]', stderr='', returncode=0)
        
        analyzer = ProjectAnalyzer("/tmp")
        analyzer.config = MagicMock(strict=True)
        
        analyzer.run_ruff_audit()
        
        # Verify --output-format is used
        args, kwargs = mock_run.call_args
        cmd = args[0]
        self.assertIn("--output-format", cmd)
        self.assertNotIn("--format", cmd)
        
        # Verify strict rules are added
        self.assertIn("--select", cmd)

if __name__ == "__main__":
    unittest.main()
