from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph.opengl as gl
import open3d as o3d
import numpy as np

class MeshViewer(gl.GLViewWidget):
    def __init__(self, parent=None):
        super(MeshViewer, self).__init__(parent)
        self.setObjectName("MeshViewer")
        self.initialize_gl()

    def initialize_gl(self):
        self.draw_axes()

    def draw_axes(self):
        # X axis (red)
        x = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [10, 0, 0]]), color=QtGui.QColor(255, 0, 0), width=2, antialias=True)
        self.addItem(x)
        # Y axis (green)
        y = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 10, 0]]), color=QtGui.QColor(0, 255, 0), width=2, antialias=True)
        self.addItem(y)
        # Z axis (blue)
        z = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, 10]]), color=QtGui.QColor(0, 0, 255), width=2, antialias=True)
        self.addItem(z)

    def plot_mesh(self, vertices, faces):
        mesh_data = gl.MeshData(vertexes=vertices, faces=faces)
        mesh_item = gl.GLMeshItem(meshdata=mesh_data, smooth=False, drawFaces=True, drawEdges=True, edgeColor=(1, 1, 1, 1))
        self.addItem(mesh_item)


class FileLoader:
    def __init__(self, text_browser):
        self.text_browser = text_browser

    def load_file(self, file_type):
        options = QtWidgets.QFileDialog.Options()
        if file_type == "PLY":
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "PLY 파일 선택", "", "PLY Files (*.ply)", options=options)
        elif file_type == "STL":
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "STL 파일 선택", "", "STL Files (*.stl)", options=options)
        elif file_type == "NPY":
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Numpy 파일 선택", "", "Numpy Files (*.npy)", options=options)
        else:
            return None
        
        if file_name:
            self.text_browser.append(f"파일 로드 완료: {file_name}")
            return file_name
        else:
            self.text_browser.append(f"파일 로드 취소")
            return None

    def parse_mesh(self, file_path):
        try:
            ext = file_path.split('.')[-1].lower()
            if ext in ['ply', 'stl']:
                mesh = o3d.io.read_triangle_mesh(file_path)
                if mesh.is_empty():
                    raise ValueError("파일 형식이 올바르지 않습니다.")
                vertices = np.asarray(mesh.vertices)
                triangles = np.asarray(mesh.triangles)
                vertex_data = vertices[triangles].reshape(-1, 3)
                faces = np.arange(vertex_data.shape[0]).reshape(-1, 3)
                return vertex_data, faces
            else:
                raise ValueError("지원하지 않는 파일 형식입니다.")
        except Exception as e:
            self.text_browser.append(f"파일을 로드하는 동안 오류가 발생했습니다: {str(e)}")
            return None, None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(1120, 602)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(0, 470, 1120, 100))
        self.textBrowser.setObjectName("textBrowser")

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(0, 0, 1114, 460))

        self.treeView = QtWidgets.QTreeView(self.splitter)
        self.treeView.setObjectName("treeView")
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath('')
        self.treeView.setModel(self.model)
        self.treeView.setHeaderHidden(True)
        for col in range(1, self.model.columnCount()):
            self.treeView.hideColumn(col)

        self.graphicsView = MeshViewer(self.splitter)
        self.graphicsView.setObjectName("graphicsView")

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1114, 460))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("파일")

        self.actionExit = QtWidgets.QAction(self)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.setText("Exit")
        self.menuFile.addAction(self.actionExit)

        self.menuLoad = QtWidgets.QMenu(self.menubar)
        self.menuLoad.setObjectName("menuLoad")
        self.menuLoad.setTitle("불러오기")        

        self.menuInference = QtWidgets.QMenu(self.menubar)
        self.menuInference.setObjectName("menuInference")
        self.menuInference.setTitle("Segmentation") 

        self.menuMapping = QtWidgets.QMenu(self.menubar)
        self.menuMapping.setObjectName("menuMapping")
        self.menuMapping.setTitle("변환작업") 

        self.menuTool = QtWidgets.QMenu(self.menubar)
        self.menuTool.setObjectName("menuTool")
        self.menuTool.setTitle("도구")

        self.groupFormat = QtWidgets.QActionGroup(self)

        self.actionLoadPLY = QtWidgets.QAction(self)
        self.actionLoadPLY.setObjectName("actionLoadPLY")
        self.actionLoadPLY.setText(".ply 파일")
        self.groupFormat.addAction(self.actionLoadPLY)
        self.menuLoad.addAction(self.actionLoadPLY)
        
        self.actionLoadSTL = QtWidgets.QAction(self)
        self.actionLoadSTL.setObjectName("actionLoadSTL")
        self.actionLoadSTL.setText(".stl 파일")
        self.groupFormat.addAction(self.actionLoadSTL)
        self.menuLoad.addAction(self.actionLoadSTL)
        
        self.actionLoadNPY = QtWidgets.QAction(self)
        self.actionLoadNPY.setObjectName("actionLoadNPY")
        self.actionLoadNPY.setText(".npy 파일")
        self.groupFormat.addAction(self.actionLoadNPY)
        self.menuLoad.addAction(self.actionLoadNPY)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuLoad.menuAction())
        self.menubar.addAction(self.menuInference.menuAction())
        self.menubar.addAction(self.menuMapping.menuAction())
        self.menubar.addAction(self.menuTool.menuAction())
        self.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        self.setup_connections()
        
        self.splitter.setSizes([320, 800])

        self.file_loader = FileLoader(self.textBrowser)

    def setup_connections(self):
        self.actionLoadPLY.triggered.connect(lambda: self.load_file("PLY"))
        self.actionLoadSTL.triggered.connect(lambda: self.load_file("STL"))
        self.actionLoadNPY.triggered.connect(lambda: self.load_file("NPY"))

    def load_file(self, file_type):
        file_path = self.file_loader.load_file(file_type)
        if file_path:
            vertices, faces = self.file_loader.parse_mesh(file_path)
            if vertices is not None and faces is not None:
                self.graphicsView.plot_mesh(vertices, faces)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "3D File Viewer"))
        self.menuFile.setTitle(_translate("MainWindow", "파일"))
        self.menuTool.setTitle(_translate("MainWindow", "도구"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
