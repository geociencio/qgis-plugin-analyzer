from qgis.gui import QgsMapTool
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
import os

class {{class_name}}Tool(QgsMapTool):
    def __init__(self, canvas):
        super().__init__(canvas)

    def canvasReleaseEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        from qgis.PyQt.QtWidgets import QMessageBox
        QMessageBox.information(None, "Point Selected", f"X: {point.x()}, Y: {point.y()}")

class {{class_name}}:
    def __init__(self, iface):
        self.iface = iface
        self.tool = None
        self.action = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.action = QAction(QIcon(icon_path), 'Activate {{name}} Tool', self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.tool = {{class_name}}Tool(self.iface.mapCanvas())
        self.tool.setAction(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if self.action.isChecked():
            self.iface.mapCanvas().setMapTool(self.tool)
        else:
            self.iface.mapCanvas().unsetMapTool(self.tool)
