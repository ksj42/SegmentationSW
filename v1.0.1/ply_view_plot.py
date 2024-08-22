from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import trimesh

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111, projection='3d')
        super(MplCanvas, self).__init__(fig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1120, 602)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # 텍스트 출력창 크기 제어
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(0, 470, 1120, 100))
        self.textBrowser.setObjectName("textBrowser")

        # Create a QSplitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(0, 0, 1114, 460))
        
        # Left pane (QTreeView)
        self.treeView = QtWidgets.QTreeView(self.splitter)
        self.treeView.setObjectName("treeView")
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath('')
        self.treeView.setModel(self.model)
        self.treeView.setHeaderHidden(True)
        for col in range(1, self.model.columnCount()):
            self.treeView.hideColumn(col)
        
        # Right pane (Matplotlib Canvas)
        self.canvas = MplCanvas(self.centralwidget, width=5, height=4, dpi=100)
        self.splitter.addWidget(self.canvas)
        
        # Add splitter to central widget
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Menu bar and actions
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1114, 460))
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
        self.splitter.setSizes([320, 800])  # Adjust the sizes as needed

        self.textBrowser.append(f"경로 설정 완료: {1}\n")
        self.textBrowser.append(f"경로 설정 완료: {2}\n")
        self.textBrowser.append(f"경로 설정 완료: {3}\n")
        self.textBrowser.append(f"경로 설정 완료: {4}\n")

        # 예시: 3D 플롯을 Canvas에 추가하기
        self.plot_3d()

    def plot_3d(self):
        # ply 파일 로드
        self.load_ply(r'H:\Project\02_CT_segmentation\Pointcloud_to_stl\Generated_bone.ply')

    def load_ply(self, filepath):
        # ply 파일 로드
        mesh = trimesh.load(filepath)
        
        if isinstance(mesh, trimesh.PointCloud):
            # Point cloud 처리
            points = mesh.vertices
            self.canvas.axes.scatter(points[:, 0], points[:, 1], points[:, 2])
            
        elif isinstance(mesh, trimesh.Trimesh):
            # Mesh 처리
            vertices = mesh.vertices
            faces = mesh.faces
            self.canvas.axes.plot_trisurf(vertices[:, 0], vertices[:, 1], vertices[:, 2], triangles=faces)

        self.canvas.draw()

    def set_custom_path(self):
        path = self.browse_for_folder()
        if path:
            self.model.setRootPath(path)
            self.treeView.setRootIndex(self.model.index(path))
            self.textBrowser.append(f"경로 설정 완료: {path}\n")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "파일"))
        self.menu_2.setTitle(_translate("MainWindow", "도구"))
        self.actionSet_Path.setText(_translate("MainWindow", "경로 설정"))

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
