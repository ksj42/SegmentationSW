import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFileDialog, QAction, QTextBrowser, QSplitter, QTreeView, QMenuBar, QMenu, QStatusBar
from PyQt5.QtCore import Qt, QRect, QCoreApplication  # QtCore 추가
from PyQt5.QtGui import QIcon, QColor
from pyqtgraph.opengl import GLViewWidget, GLLinePlotItem, GLScatterPlotItem, MeshData, GLMeshItem


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1120, 602)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 텍스트 출력창 크기 제어
        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QRect(0, 470, 1120, 100))
        self.textBrowser.setObjectName("textBrowser")

        # Create a QSplitter
        self.splitter = QSplitter(Qt.Horizontal, self.centralwidget)
        self.splitter.setGeometry(QRect(0, 0, 1114, 460))

        # Left pane (QTreeView)
        self.treeView = QTreeView(self.splitter)
        self.treeView.setObjectName("treeView")

        # Right pane (OpenGL Widget)
        self.openglWidget = OpenGLWidget(self.splitter)
        self.openglWidget.setObjectName("openglWidget")

        # Add splitter to central widget
        MainWindow.setCentralWidget(self.centralwidget)

        # Menu bar and actions
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 1114, 460))
        self.menubar.setObjectName("menubar")
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.actionLoad = QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionLoad.setText("Load")
        self.actionLoad.triggered.connect(self.load_file)
        self.menu.addAction(self.actionLoad)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        MainWindow.setMenuBar(self.menubar)

        # Status bar
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Connect signals and slots, translate UI
        self.retranslateUi(MainWindow)
        QCoreApplication.instance().aboutToQuit.connect(MainWindow.close)  # QtCore 추가

        # Set initial splitter sizes
        self.splitter.setSizes([320, 800])  # Adjust the sizes as needed

        self.textBrowser.append(f"경로 설정 완료: {1}\n")
        self.textBrowser.append(f"경로 설정 완료: {2}\n")
        self.textBrowser.append(f"경로 설정 완료: {3}\n")
        self.textBrowser.append(f"경로 설정 완료: {4}\n")

        # Draw coordinate axes
        self.draw_axes()

    def draw_axes(self):
        # X axis (red)
        x = GLLinePlotItem(pos=np.array([[0, 0, 0], [10, 0, 0]]), color=QColor(255, 0, 0), width=2, antialias=True)
        self.openglWidget.addItem(x)
        # Y axis (green)
        y = GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 10, 0]]), color=QColor(0, 255, 0), width=2, antialias=True)
        self.openglWidget.addItem(y)
        # Z axis (blue)
        z = GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, 10]]), color=QColor(0, 0, 255), width=2, antialias=True)
        self.openglWidget.addItem(z)

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "파일 선택", "", "All Files (*);;Numpy Files (*.npy)", options=options)
        if file_name:
            self.plot_point_cloud(file_name)

    def plot_point_cloud(self, file_path):
        try:
            points = np.load(file_path)
            if points.shape[1] != 3:
                raise ValueError("Numpy array should have shape (N, 3)")

            scatter_plot = GLScatterPlotItem(pos=points, color=(1, 1, 1, 1), size=0.5)
            self.openglWidget.addItem(scatter_plot)
            self.textBrowser.append(f"파일 로드 완료: {file_path}")
        except Exception as e:
            self.textBrowser.append(f"파일을 로드하는 동안 오류가 발생했습니다: {str(e)}")

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "파일"))
        self.menu_2.setTitle(_translate("MainWindow", "도구"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))

class OpenGLWidget(GLViewWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundColor('k')  # 배경색을 검은색으로 설정
        self.setCameraPosition(distance=20)  # 카메라 위치 설정

    def initializeGL(self):
        GLViewWidget.initializeGL(self)
        self.opts['distance'] = 20

def main():
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
