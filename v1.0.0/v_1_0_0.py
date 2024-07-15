from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1114, 602)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(320, 451, 781, 111))
        self.textBrowser.setObjectName("textBrowser")
        
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setGeometry(QtCore.QRect(0, 0, 301, 406))
        self.treeView.setObjectName("treeView")

        # Model 설정
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath('')  # 기본 루트 경로 설정 (빈 문자열)
        self.treeView.setModel(self.model)
        
        # 파일 이름만 보이게 설정
        self.treeView.setHeaderHidden(True)
        for col in range(1, self.model.columnCount()):
            self.treeView.hideColumn(col)
        
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(510, 60, 591, 371))
        self.graphicsView.setObjectName("graphicsView")
        MainWindow.setCentralWidget(self.centralwidget)
        
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
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

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
            self.textBrowser.append(f"경로 설정 완료: {path}\n")

    def browse_for_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(None, "폴더 선택", "", options)
        return folder

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
    #test22222222
    tset = 123123
    print(test)
    print(test)
    print(test)
    print(test)
