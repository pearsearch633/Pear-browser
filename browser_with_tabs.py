import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QLineEdit, QToolBar,
    QAction, QStatusBar, QMessageBox, QWidget, QVBoxLayout, QMenu,
    QMenuBar, QInputDialog, QListWidget, QDockWidget, QFileDialog, QDialog, QHBoxLayout, QPushButton
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QKeySequence


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pear Browser")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #F5F5F5;")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_on_tab_change)
        self.setCentralWidget(self.tabs)

        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.add_navigation_buttons()
        self.create_centered_url_bar()
        self.add_menus()

        self.start_page_url = "https://www.google.com"
        self.create_new_tab(QUrl(self.start_page_url), "Startpagina")

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.bookmarks = []
        self.history = []
        self.downloads = []

    def add_navigation_buttons(self):
        self.back_action = QAction("←", self)
        self.back_action.triggered.connect(self.back)
        self.toolbar.addAction(self.back_action)

        self.forward_action = QAction("→", self)
        self.forward_action.triggered.connect(self.forward)
        self.toolbar.addAction(self.forward_action)

        self.reload_action = QAction("⟳", self)
        self.reload_action.triggered.connect(self.reload_page)
        self.toolbar.addAction(self.reload_action)

        self.new_tab_action = QAction("+", self)
        self.new_tab_action.triggered.connect(self.create_new_tab)
        self.toolbar.addAction(self.new_tab_action)

    def create_centered_url_bar(self):
        self.url_bar = QLineEdit()
        self.url_bar.setFixedHeight(36)
        self.url_bar.setPlaceholderText("Typ een webadres")
        self.url_bar.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCC;
                border-radius: 18px;
                padding: 5px 15px;
                background-color: #FFFFFF;
            }
        """)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)

        self.star_action = QAction("★", self)
        self.star_action.triggered.connect(self.add_bookmark)
        self.toolbar.addAction(self.star_action)

    def add_menus(self):
        menu = self.menu_bar.addMenu("Menu")

        downloads_action = QAction("Downloads", self)
        downloads_action.setShortcut(QKeySequence("Ctrl+J"))
        downloads_action.triggered.connect(self.open_downloads)
        menu.addAction(downloads_action)

        history_action = QAction("Geschiedenis", self)
        history_action.setShortcut(QKeySequence("Ctrl+H"))
        history_action.triggered.connect(self.open_history)
        menu.addAction(history_action)

        bookmarks_action = QAction("Bladwijzers", self)
        bookmarks_action.triggered.connect(self.show_bookmarks)
        menu.addAction(bookmarks_action)

        zoom_menu = QMenu("Zoom", self)
        zoom_in_action = QAction("Inzoomen", self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl+0"))
        zoom_in_action.triggered.connect(self.zoom_in)
        zoom_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Uitzoomen", self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.triggered.connect(self.zoom_out)
        zoom_menu.addAction(zoom_out_action)

        menu.addMenu(zoom_menu)

    def create_new_tab(self, qurl=None, label="Nieuw tabblad"):
        if not qurl:
            qurl = QUrl(self.start_page_url)
        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.urlChanged.connect(self.update_url_bar)
        browser.page().profile().downloadRequested.connect(self.handle_download)

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def update_url_on_tab_change(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser and isinstance(current_browser, QWebEngineView):
            self.url_bar.setText(current_browser.url().toString())
        else:
            self.url_bar.clear()

    def update_url_bar(self, qurl):
        current_browser = self.tabs.currentWidget()
        if current_browser == self.sender():
            self.url_bar.setText(qurl.toString())
            self.history.append(qurl.toString())

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url
        current_browser = self.tabs.currentWidget()
        if current_browser and isinstance(current_browser, QWebEngineView):
            current_browser.setUrl(QUrl(url))

    def back(self):
        current_browser = self.tabs.currentWidget()
        if current_browser and isinstance(current_browser, QWebEngineView):
            current_browser.back()

    def forward(self):
        current_browser = self.tabs.currentWidget()
        if current_browser and isinstance(current_browser, QWebEngineView):
            current_browser.forward()

    def reload_page(self):
        current_browser = self.tabs.currentWidget()
        if current_browser and isinstance(current_browser, QWebEngineView):
            current_browser.reload()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def add_bookmark(self):
        current_url = self.url_bar.text()
        name, ok = QInputDialog.getText(self, "Bladwijzer toevoegen", "Naam bladwijzer:")
        if ok and name:
            self.bookmarks.append((name, current_url))
            QMessageBox.information(self, "Bladwijzer toegevoegd", f"Bladwijzer '{name}' opgeslagen!")

    def show_bookmarks(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Bladwijzers")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        for name, url in self.bookmarks:
            list_widget.addItem(f"{name}: {url}")

        list_widget.itemDoubleClicked.connect(lambda item: self.navigate_to_bookmark(item.text().split(": ")[1]))
        layout.addWidget(list_widget)
        dialog.exec_()

    def navigate_to_bookmark(self, url):
        self.create_new_tab(QUrl(url), "Bladwijzer")

    def open_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Geschiedenis")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        for url in self.history:
            list_widget.addItem(url)

        list_widget.itemDoubleClicked.connect(lambda item: self.create_new_tab(QUrl(item.text()), "Geschiedenis"))
        layout.addWidget(list_widget)
        dialog.exec_()

    def open_downloads(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Downloads")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        for path in self.downloads:
            list_widget.addItem(path)

        list_widget.itemDoubleClicked.connect(lambda item: os.startfile(item.text()))
        layout.addWidget(list_widget)
        dialog.exec_()

    def handle_download(self, download):
        default_path = QFileDialog.getSaveFileName(self, "Bestand opslaan", download.path())[0]
        if default_path:
            download.setPath(default_path)
            download.accept()
            self.downloads.append(default_path)

    def zoom_in(self):
        current_browser = self.tabs.currentWidget()
        if current_browser and isinstance(current_browser, QWebEngineView):
            current_browser.setZoomFactor(current_browser.zoomFactor() + 0.1)

    def zoom_out(self):
        current_browser = self.tabs.currentWidget()
        if current_browser and isinstance(current_browser, QWebEngineView):
            current_browser.setZoomFactor(current_browser.zoomFactor() - 0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Pear Browser")
    window = Browser()
    window.show()
    sys.exit(app.exec_())
