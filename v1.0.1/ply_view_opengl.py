from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph.opengl as gl
import open3d as o3d
import numpy as np

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
        
        # Right pane (QGLView)
        self.graphicsView = gl.GLViewWidget(self.splitter)
        self.graphicsView.setObjectName("graphicsView")
        
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
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionLoad.setText("Load")
        self.actionLoad.triggered.connect(self.load_file)
        self.menu.addAction(self.actionLoad)
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

        # Draw coordinate axes
        self.draw_axes()

    def draw_axes(self):
        # X axis (red)
        x = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [10, 0, 0]]), color=QtGui.QColor(255, 0, 0), width=2, antialias=True)
        self.graphicsView.addItem(x)
        # Y axis (green)
        y = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 10, 0]]), color=QtGui.QColor(0, 255, 0), width=2, antialias=True)
        self.graphicsView.addItem(y)
        # Z axis (blue)
        z = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, 10]]), color=QtGui.QColor(0, 0, 255), width=2, antialias=True)
        self.graphicsView.addItem(z)

    def load_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "파일 선택", "", "All Files (*);;PLY Files (*.ply);;STL Files (*.stl)", options=options)
        if file_name:
            self.plot_mesh(file_name)

    def plot_mesh(self, file_path):
        try:
            ext = file_path.split('.')[-1].lower()
            if ext == 'ply':
                mesh = o3d.io.read_triangle_mesh(file_path)
            elif ext == 'stl':
                mesh = o3d.io.read_triangle_mesh(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            if not mesh.is_empty():
                vertices = np.asarray(mesh.vertices)
                triangles = np.asarray(mesh.triangles)

                vertex_data = vertices[triangles].reshape(-1, 3)
                faces = np.arange(vertex_data.shape[0]).reshape(-1, 3)

                mesh_data = gl.MeshData(vertexes=vertex_data, faces=faces)
                mesh_item = gl.GLMeshItem(meshdata=mesh_data, smooth=False, drawFaces=True, drawEdges=True, edgeColor=(1, 1, 1, 1))
                self.graphicsView.addItem(mesh_item)
                self.textBrowser.append(f"파일 로드 완료: {file_path}")
            else:
                self.textBrowser.append(f"파일 형식이 올바르지 않습니다: {file_path}")
        except Exception as e:
            self.textBrowser.append(f"파일을 로드하는 동안 오류가 발생했습니다: {str(e)}")

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
        self.actionLoad.setText(_translate("MainWindow", "Load"))

    def browse_for_folder(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ShowDirsOnly
        folder = QtWidgets.QFileDialog.getExistingDirectory(None, "폴더 선택", "", options)
        return folder

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

