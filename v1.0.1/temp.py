from PyQt5 import QtCore, QtGui, QtWidgets  # Import necessary PyQt5 modules

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1114, 602)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Create a QSplitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(0, 0, 1114, 560))
        
        # Left pane (QTreeView)
        self.treeView = QtWidgets.QTreeView(self.splitter)
        self.treeView.setObjectName("treeView")
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath('')
        self.treeView.setModel(self.model)
        self.treeView.setHeaderHidden(True)
        for col in range(1, self.model.columnCount()):
            self.treeView.hideColumn(col)
        
        # Right pane (QGraphicsView)
        self.graphicsView = QtWidgets.QGraphicsView(self.splitter)
        self.graphicsView.setObjectName("graphicsView")
        
        # Add splitter to central widget
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Menu bar and actions
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1114, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.actionSet_Path = QtWidgets.QAction(MainWindow)
        self.actionSet_Path.setObjectName("actionSet_Path")
        self.actionSet_Path.setText("경로 설정")
        self.actionSet_Path.triggered.connect(self.set_custom_path)
        self.menu.addAction(self.actionSet_Path)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        MainWindow.setMenuBar(self.menubar)
        
        # Status bar
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        # Connect signals and slots, translate UI
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Set initial splitter sizes
        self.splitter.setSizes([320, 794])  # Adjust the sizes as needed

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "파일"))
        self.menu_2.setTitle(_translate("MainWindow", "도구"))
        self.actionSet_Path.setText(_translate("MainWindow", "경로 설정"))

    def set_custom_path(self):
        path = self.browse_for_folder()
        if path:
            self.model.setRootPath(path)
            self.treeView.setRootIndex(self.model.index(path))
            # self.textBrowser.append(f"경로 설정 완료: {path}\n")

    def browse_for_folder(self):
        options = QtWidgets.QFileDialog.Options()  # Ensure QtWidgets.QFileDialog is used
        options |= QtWidgets.QFileDialog.ShowDirsOnly
        folder = QtWidgets.QFileDialog.getExistingDirectory(None, "폴더 선택", "", options)  # Use QtWidgets.QFileDialog.getExistingDirectory
        return folder

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
