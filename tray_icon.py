from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

class TrayIcon(QSystemTrayIcon):
    """
    Creates and manages the application's system tray icon and its context menu.
    This is a core part of the UI, fulfilling FR-UI-01.
    """
    def __init__(self, icon_path: str, parent=None):
        super().__init__(parent)

        # 1. Set the icon and tooltip
        self.setIcon(QIcon(icon_path))
        self.setToolTip("ChronoAI - Your Personal Calendar Assistant")

        # 2. Create the context menu
        self.menu = QMenu(parent)

        # 3. Create the actions for the menu
        self.show_action = QAction("Show Dashboard", self)
        self.sync_action = QAction("Sync Now", self)
        self.quit_action = QAction("Quit", self)

        # 4. Add actions to the menu
        self.menu.addAction(self.show_action)
        self.menu.addAction(self.sync_action)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_action)

        # 5. Set the context menu for the tray icon
        self.setContextMenu(self.menu)

        # The signals for these actions (e.g., self.show_action.triggered)
        # will be connected in the main application file where the main window
        # and other components are instantiated.

        # 6. Make the icon visible
        self.show()

    def show_message(self, title: str, message: str, msecs: int = 2000):
        """Displays a balloon message from the tray icon."""
        self.showMessage(title, message, self.icon(), msecs)