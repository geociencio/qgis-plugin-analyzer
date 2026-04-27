import ast
import unittest

from analyzer.visitors.safety_visitor import SafetyVisitor


class TestSafety(unittest.TestCase):
    def test_signal_leak_detection(self):
        code = """
class MyPlugin:
    def initGui(self):
        self.iface.mapCanvas().xyCoordinates.connect(self.on_xy)
        self.btn.clicked.connect(self.do_something)

    def unload(self):
        self.iface.mapCanvas().xyCoordinates.disconnect(self.on_xy)
        # Missing disconnect for self.btn.clicked
    """
        tree = ast.parse(code)
        visitor = SafetyVisitor("test.py")
        visitor.visit(tree)

        self.assertIn("self.btn.clicked", visitor.signal_leaks)
        self.assertNotIn("self.iface.mapCanvas().xyCoordinates", visitor.signal_leaks)

    def test_ui_blocking_loop_detection(self):
        code = """
class MyPlugin:
    def run(self):
        # Case 1: Blocking loop in run() - a common UI handler
        for feature in self.layer.getFeatures():
            print(feature)

    def mousePressEvent(self, event):
        # Case 2: Handlers with 'Event' suffix
        while self.is_running:
            import time
            time.sleep(1)

    def safe_method(self):
        # Case 3: Wrapped in QgsTask should be fine
        task = QgsTask.fromFunction("task", self.slow_op)
        for i in range(100):
            self.do_something()
    """
        tree = ast.parse(code)
        visitor = SafetyVisitor("test.py")
        visitor.visit(tree)

        issues = [i for i in visitor.issues if i["type"] == "UI_BLOCKING_LOOP"]
        self.assertGreaterEqual(len(issues), 2)
        # Check that they point to the correct lines (approximate)
        lines = [i["line"] for i in issues]
        self.assertIn(5, lines)  # getFeatures loop
        self.assertIn(10, lines)  # sleep loop

    def test_qgs_task_protection(self):
        code = """
def run(self):
    # This loop is inside a function that uses QgsTask
    # It should NOT be flagged as blocking
    task = QgsTask.fromFunction("test", lambda: None)
    for i in range(100):
        self.layer.getFeatures()
    """
        tree = ast.parse(code)
        visitor = SafetyVisitor("test.py")
        visitor.visit(tree)

        issues = [i for i in visitor.issues if i["type"] == "UI_BLOCKING_LOOP"]
        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
