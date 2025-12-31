import unittest
import pathlib
from src.analyzer.validators import is_ssrf_safe
from src.analyzer.utils import safe_path_resolve

class TestSecurity(unittest.TestCase):
    def test_ssrf_safe_urls(self):
        # Public URLs should be safe
        self.assertTrue(is_ssrf_safe("https://google.com"))
        self.assertTrue(is_ssrf_safe("https://github.com/qgis/QGIS"))
        
        # Private/Local URLs should be blocked
        self.assertFalse(is_ssrf_safe("http://127.0.0.1"))
        self.assertFalse(is_ssrf_safe("http://localhost"))
        self.assertFalse(is_ssrf_safe("http://192.168.1.1"))
        self.assertFalse(is_ssrf_safe("http://10.0.0.1"))
        self.assertFalse(is_ssrf_safe("http://172.16.0.1"))
        self.assertFalse(is_ssrf_safe("http://169.254.169.254")) # AWS Meta-data
        self.assertFalse(is_ssrf_safe("http://[::1]"))
        
    def test_path_traversal_protection(self):
        base = pathlib.Path("/tmp/project").resolve()
        
        # Safe paths
        self.assertEqual(safe_path_resolve(base, "metadata.txt"), base / "metadata.txt")
        self.assertEqual(safe_path_resolve(base, "src/analyzer/engine.py"), base / "src/analyzer/engine.py")
        
        # Traversal attempts
        with self.assertRaises(ValueError):
            safe_path_resolve(base, "../passwd")
            
        with self.assertRaises(ValueError):
            safe_path_resolve(base, "../../etc/shadow")
            
        with self.assertRaises(ValueError):
            safe_path_resolve(base, "/etc/passwd")

if __name__ == "__main__":
    unittest.main()
