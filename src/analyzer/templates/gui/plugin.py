from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
import os

class {{class_name}}:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.action = QAction(
            QIcon(icon_path),
            self.tr('Run {{name}}'),
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.tr('&{{name}}'), self.action)

    def unload(self):
        self.iface.removePluginMenu(self.tr('&{{name}}'), self.action)
        self.iface.removeToolBarIcon(self.action)

    def tr(self, message):
        from qgis.PyQt.QtCore import QCoreApplication
        return QCoreApplication.translate('{{class_name}}', message)

    def run(self):
        from qgis.PyQt.QtWidgets import QMessageBox
        QMessageBox.information(None, self.tr('{{name}}'), self.tr('Hello from {{name}}!'))
