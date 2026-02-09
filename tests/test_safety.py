import ast

from analyzer.visitors.safety_visitor import SafetyVisitor


def test_signal_leak_detection():
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

    assert "self.btn.clicked" in visitor.signal_leaks
    assert "self.iface.mapCanvas().xyCoordinates" not in visitor.signal_leaks


def test_ui_blocking_loop_detection():
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
    assert len(issues) >= 2
    # Check that they point to the correct lines (approximate)
    lines = [i["line"] for i in issues]
    assert 5 in lines  # getFeatures loop
    assert 10 in lines  # sleep loop


def test_qgs_task_protection():
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
    assert len(issues) == 0
