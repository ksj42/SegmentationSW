'''
1. 이미지 전처리하고 AI를 위한 복셀 저장하기
'''

import pyqtgraph.opengl as gl
import open3d as o3d
import numpy as np
import pydicom
import pandas as pd
import os
import matplotlib.pyplot as plt
import cx_Oracle
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox

from pydicom.data import get_testdata_files
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QVector3D
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyleFactory
from PyQt5.QtWidgets import QMenuBar, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QButtonGroup, QPushButton, QMessageBox
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QMessageBox, QCheckBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QScrollArea, QGridLayout
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget
from PyQt5.QtGui import QCursor

# 열리는 창의 위치를 마우스가 있는 모니터의 중앙으로 위치시키기
class CenterOnMouseMonitor:
    def __init__(self, window):
        """
        Center the given window on the monitor where the mouse cursor is currently located.
        :param window: QMainWindow or QWidget instance that should be centered.

        center_util = CenterOnMouseMonitor(self)
        center_util.center()
        """
        self.window = window

    def center(self):
        """
        Centers the window on the monitor where the mouse cursor is located.
        """
        # Get the current mouse position
        mouse_position = QCursor.pos()

        # Get the number of monitors and their geometries
        desktop = QDesktopWidget()
        monitor_count = desktop.screenCount()

        for monitor in range(monitor_count):
            monitor_geometry = desktop.screenGeometry(monitor)
            if monitor_geometry.contains(mouse_position):
                # Calculate the center position of the monitor and move the window
                window_geometry = self.window.frameGeometry()
                monitor_center = monitor_geometry.center()
                window_geometry.moveCenter(monitor_center)
                self.window.move(window_geometry.topLeft())
                break

class ImageTileDisplay(QWidget):
    def __init__(self, images, cmap='gray', parent=None):
        super().__init__(parent)
        self.images = images
        self.cmap = cmap
        self.tile_size = (256, 256)  # Default tile size; will be adjusted dynamically
        self.selected_image_index = None  # Track selected image index
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        center_util = CenterOnMouseMonitor(self)
        center_util.center()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(QWidget())
        self.scroll_area.widget().setLayout(self.grid_layout)

        layout.addWidget(self.scroll_area)
        
        # Add confirm button
        self.confirm_button = QPushButton("확인")
        self.confirm_button.clicked.connect(self.on_confirm)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)
        self.adjust_tile_size()

    def adjust_tile_size(self):
        # Adjust tile size based on window size
        widget_size = self.scroll_area.viewport().size()
        num_columns = 4  # Assuming 4 images per row
        tile_width = widget_size.width() // num_columns
        tile_height = tile_width
        self.tile_size = (tile_width, tile_height)
        self.update_images()

    def update_images(self):
        # Clear existing layout
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Adding images to grid layout
        for idx, image in enumerate(self.images):
            pixmap = QPixmap.fromImage(self.apply_cmap_to_image(self.resize_image(image), self.cmap))
            
            # Create a container widget for each image and checkbox
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)

            # Create label for the image
            label = QLabel()
            label.setPixmap(pixmap)
            label.setScaledContents(True)
            label.setFixedSize(*self.tile_size)
            label.setProperty("index", idx)

            # Create checkbox
            checkbox = QCheckBox()
            checkbox.setProperty("index", idx)
            checkbox.stateChanged.connect(self.checkbox_changed)

            # Add label and checkbox to container
            container_layout.addWidget(label)
            container_layout.addWidget(checkbox, alignment=Qt.AlignCenter)

            row = idx // 4  # Assuming 4 images per row
            col = idx % 4
            self.grid_layout.addWidget(container, row, col)

        self.scroll_area.setWidgetResizable(True)

    def resize_image(self, np_array):
        # Resize image to tile size
        image = Image.fromarray(np_array)
        image = image.resize(self.tile_size, Image.Resampling.LANCZOS)
        return np.array(image)

    def apply_cmap_to_image(self, np_array, cmap):
        # Apply colormap using matplotlib
        plt_image = plt.get_cmap(cmap)(np_array/np_array.max())  # Apply colormap
        plt_image = (plt_image[:, :, :3] * 255).astype(np.uint8)  # Convert to RGB uint8

        # Convert to QImage
        height, width, channel = plt_image.shape
        bytes_per_line = 3 * width
        qimage = QImage(plt_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return qimage

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_tile_size()

    def checkbox_changed(self, state):
        checkbox = self.sender()
        if state == Qt.Checked:
            self.selected_image_index = checkbox.property("index")
            print(f"Selected image index: {self.selected_image_index}")
        else:
            self.selected_image_index = None

    def on_confirm(self):
        if self.selected_image_index is not None:
            start_index = self.selected_image_index
            end_index = min(start_index + 96, len(self.images))
            selected_images = self.images[start_index:end_index]
            if len(selected_images) < 96:
                selected_images.extend([None] * (96 - len(selected_images)))

            self.process_selected_images(selected_images)
        else:
            print("No image selected")

    def process_selected_images(self, images):
        # Handle the 96 images
        print(f"Processing {len(images)} selected images.")
        # Add further processing code here
        # for i in range(len(images)):
        #     print(i+self.selected_image_index, images[i].shape if images[i] is not None else "None")

        self.images = np.stack(images)

        #print(self.images.shape)


class BoneClavicle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

        self.bone_images = []
        self.generate_voxel_for_AI(self.main_window.folder_path)  # Replace with actual path

        # Show images in a tiled layout
        if self.bone_images:
            self.image_display_widget = ImageTileDisplay(self.bone_images, cmap='gray')
            self.image_display_widget.setWindowTitle("Tiled Images")
            self.image_display_widget.resize(800, 600)  # Initial size of the window
            self.image_display_widget.show()

        print('test')
        print(self.image_display_widget.images.shape)

    def window_image(self, image, window_center, window_width):
        img_min = window_center - window_width // 2
        img_max = window_center + window_width // 2
        window_image = image.copy()
        window_image[window_image < img_min] = img_min
        window_image[window_image > img_max] = img_max
        return window_image

    def generate_voxel_for_AI(self, path):
        file_list = os.listdir(path)
        file_list_py = [file for file in file_list if file.endswith('.dcm')]
        study_id = 0

        for i in range(len(file_list_py)):
            try:
                medical_image = pydicom.read_file(os.path.join(path, file_list_py[i]))
                image = medical_image.pixel_array

                intercept = medical_image.RescaleIntercept
                slope = medical_image.RescaleSlope
                hu_image = image * slope + intercept

                bone_image = self.window_image(hu_image, 450, 850)
                self.bone_images.append(bone_image)

                # 이미지 저장 코드
                if study_id != int(medical_image.StudyID):
                    study_dir = os.path.join(r'H:\Project\08_clavicle_software_python\sw\v1.0.5\img', medical_image.StudyDescription)
                    os.makedirs(study_dir, exist_ok=True)
                plt.imsave(os.path.join(study_dir, f'img_{i}.png'), bone_image)
                study_id = int(medical_image.StudyID)

            except Exception as e:
                print(f"Error processing {file_list_py[i]}: {e}")

class SelectionDialog(QDialog):

    def __init__(self, parent=None):
        super(SelectionDialog, self).__init__(parent)
        self.setWindowTitle("부위 선택")
        self.setGeometry(100, 100, 300, 200)
        self.selected_model = ''

        layout = QVBoxLayout(self)
        self.button_group = QButtonGroup(self)

        # 라디오 버튼 생성
        self.radio_clavicle = QRadioButton("쇄골", self)
        self.button_group.addButton(self.radio_clavicle)
        layout.addWidget(self.radio_clavicle)

        self.radio_scapula = QRadioButton("견갑골", self)
        self.button_group.addButton(self.radio_scapula)
        layout.addWidget(self.radio_scapula)

        self.radio_sample1 = QRadioButton("샘플1", self)
        self.button_group.addButton(self.radio_sample1)
        layout.addWidget(self.radio_sample1)

        self.radio_sample2 = QRadioButton("샘플2", self)
        self.button_group.addButton(self.radio_sample2)
        layout.addWidget(self.radio_sample2)

        self.radio_sample3 = QRadioButton("샘플3", self)
        self.button_group.addButton(self.radio_sample3)
        layout.addWidget(self.radio_sample3)

        # 확인 버튼 생성 및 추가
        self.confirm_button = QPushButton("확인", self)
        layout.addWidget(self.confirm_button)

        # 확인 버튼 클릭 시 처리
        self.confirm_button.clicked.connect(self.on_confirm)

        center_util = CenterOnMouseMonitor(self)
        center_util.center()

    def on_confirm(self):
        if self.radio_clavicle.isChecked():
            self.selected_model = 'clavicle'
            self.accept()  # 다이얼로그 종료
        else:
            self.selected_model = 'scapular'
            self.accept()
            #QMessageBox.warning(self, "경고", "쇄골을 선택해주세요.")

class DICOMTagsDialog(QtWidgets.QDialog):
    def __init__(self, dicom_tags_df, parent=None):
        super(DICOMTagsDialog, self).__init__(parent)
        self.setWindowTitle("DICOM Tags Information")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.table_view = QtWidgets.QTableView(self)
        self.layout.addWidget(self.table_view)

        self.populate_data(dicom_tags_df)

        center_util = CenterOnMouseMonitor(self)
        center_util.center()

        

    def populate_data(self, dicom_tags_df):
        if dicom_tags_df is not None and not dicom_tags_df.empty:
            model = PandasModel(dicom_tags_df)
            self.table_view.setModel(model)
        else:
            self.table_view.setModel(QtGui.QStandardItemModel())

class PandasModel(QAbstractTableModel):
    def __init__(self, dataframe, parent=None):
        super(PandasModel, self).__init__(parent)
        self._data = dataframe

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            else:
                return str(section + 1)
        return None

class MeshViewer(gl.GLViewWidget):
    def __init__(self, parent=None):
        super(MeshViewer, self).__init__(parent)
        self.setObjectName("MeshViewer")
        self.initialize_gl()
        self.last_pos = None

    def initialize_gl(self):
        self.draw_axes()
        self.setCameraPosition(distance=350)

    def draw_axes(self):
        x = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [10, 0, 0]]), color=(1, 0, 0, 1), width=2, antialias=True)
        y = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 10, 0]]), color=(0, 1, 0, 1), width=2, antialias=True)
        z = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, 10]]), color=(0, 0, 1, 1), width=2, antialias=True)
        self.addItem(x)
        self.addItem(y)
        self.addItem(z)

    def plot_mesh(self, vertices, faces, file_type):
        # 중심 계산 및 이동
        center = vertices.mean(axis=0)
        vertices -= center

        mesh_data = gl.MeshData(vertexes=vertices, faces=faces)
        
        if file_type.lower() == 'stl':
            # STL 파일에 대한 그레이스케일 색상 적용
            colors = np.ones((vertices.shape[0], 4)) * 0.7  # 밝은 회색
            mesh_data.setVertexColors(colors)
            mesh_item = gl.GLMeshItem(meshdata=mesh_data, smooth=True, drawEdges=False, shader='shaded')
        else:
            mesh_item = gl.GLMeshItem(meshdata=mesh_data, smooth=False, drawFaces=True, drawEdges=True, edgeColor=(1, 1, 1, 1))
        
        self.addItem(mesh_item)

    def plot_point_cloud(self, points):
        # 중심 계산 및 이동
        center = points.mean(axis=0)
        points -= center

        scatter = gl.GLScatterPlotItem(pos=points, color=(1, 1, 1, 1), size=2, pxMode=True)

        self.addItem(scatter)

    def clear_items(self):
        for item in self.items:
            self.removeItem(item)
        self.draw_axes()

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            self.last_pos = event.pos()
            return

        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()

        if event.buttons() == Qt.LeftButton:
            self.orbit(-dx, -dy)
        elif event.buttons() == Qt.MidButton:
            self.pan(dx, dy, 0)

        self.last_pos = event.pos()

    def mouseReleaseEvent(self, event):
        self.last_pos = None


class DICOMInfoDialog(QtWidgets.QDialog):
    def __init__(self, dicom_data, parent=None):
        super(DICOMInfoDialog, self).__init__(parent)
        self.setWindowTitle("DICOM Information")
        self.setGeometry(100, 100, 600, 400)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.text_browser = QtWidgets.QTextBrowser(self)
        self.layout.addWidget(self.text_browser)

        self.populate_data(dicom_data)

        center_util = CenterOnMouseMonitor(self)
        center_util.center()

    def populate_data(self, dicom_data):
        if dicom_data:
            summaries = []
            for dicom_file, ds in dicom_data:
                summary = f"파일명: {os.path.basename(dicom_file)}\n"
                summary += f"환자 이름: {ds.get('PatientName', '정보 없음')}\n"
                summary += f"환자 ID: {ds.get('PatientID', '정보 없음')}\n"
                summary += f"촬영일: {ds.get('StudyDate', '정보 없음')}\n"
                summary += f"기기 모델: {ds.get('ManufacturerModelName', '정보 없음')}\n"
                summaries.append(summary)
            self.text_browser.setPlainText("\n\n".join(summaries))
        else:
            self.text_browser.setPlainText("DICOM 데이터가 없습니다.")

class FileLoader:
    def __init__(self, text_browser):
        self.text_browser = text_browser
        self.dicom_data = []  # List to store tuples of (file_path, dataset)
        self.dicom_tags_df = pd.DataFrame()  # DataFrame to store DICOM tag information

    def load_file(self, file_type):
        options = QtWidgets.QFileDialog.Options()
        file_name = None
        folder_name = None
        if file_type == "PLY":
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "PLY 파일 선택", "", "PLY Files (*.ply)", options=options)
        elif file_type == "STL":
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "STL 파일 선택", "", "STL Files (*.stl)", options=options)
        elif file_type == "NPY":
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Numpy 파일 선택", "", "Numpy Files (*.npy)", options=options)
        elif file_type == "DICOM":
            folder_name = QtWidgets.QFileDialog.getExistingDirectory(None, "DICOM 폴더 선택", "", options=options)
        else:
            return None

        if file_name:
            self.text_browser.append(f"파일 로드 완료: {file_name}")
            return file_name
        elif folder_name:
            self.text_browser.append(f"폴더 로드 완료: {folder_name}")
            return folder_name
        else:
            self.text_browser.append(f"파일 로드 취소")
            return None

    def summarize_dicom_folder(self, folder_path):
        try:
            dicom_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.dcm')]
            self.dicom_data = []  # Clear previous data
            summaries = []
            list_total_info = []

            for dicom_file in dicom_files:
                ds = pydicom.dcmread(dicom_file)
                self.dicom_data.append((dicom_file, ds))  # Store dataset
                summary = f"파일명: {os.path.basename(dicom_file)}\n"
                summary += f"환자 이름: {ds.get('PatientName', '정보 없음')}\n"
                summary += f"환자 ID: {ds.get('PatientID', '정보 없음')}\n"
                summary += f"촬영일: {ds.get('StudyDate', '정보 없음')}\n"
                summary += f"기기 모델: {ds.get('ManufacturerModelName', '정보 없음')}\n"
                summaries.append(summary)

                # Extract tags
                tag_AccessionNumber = ds.get('AccessionNumber', 'No AccessionNumber')
                tag_SeriesDescription = ds.get('SeriesDescription', 'No SeriesDescription')
                tag_SliceThickness = ds.get('SliceThickness', 'No SliceThickness')
                tag_PixelSpacing = ds.get('PixelSpacing', 'No PixelSpacing')
                tag_PatientSex = ds.get('PatientSex', 'No PatientSex')
                tag_PatientAge = ds.get('PatientAge', 'No PatientAge')

                list_total_info.append([
                    os.path.basename(dicom_file),
                    tag_AccessionNumber,
                    tag_SeriesDescription,
                    tag_SliceThickness,
                    tag_PixelSpacing,
                    tag_PatientSex,
                    tag_PatientAge
                ])

            # Convert list to DataFrame
            col = ['Filename', 'AccessionNumber', 'SeriesDescription', 'SliceThickness', 'PixelSpacing', 'PatientSex', 'PatientAge']
            self.dicom_tags_df = pd.DataFrame(data=list_total_info, columns=col)
            
            return "\n\n".join(summaries)
        except Exception as e:
            self.text_browser.append(f"파일을 로드하는 동안 오류가 발생했습니다: {str(e)}")
            return None

    def parse_mesh(self, file_path):
        try:
            ext = file_path.split('.')[-1].lower()
            if ext == 'ply':
                mesh = o3d.io.read_triangle_mesh(file_path)
                if not mesh.is_empty() and len(mesh.triangles) > 0:
                    # 정상적으로 삼각형 메시를 읽은 경우
                    vertices = np.asarray(mesh.vertices)
                    triangles = np.asarray(mesh.triangles)
                    return vertices, triangles
                else:
                    # 삼각형 메시가 없고, 점 클라우드만 있는 경우
                    point_cloud = o3d.io.read_point_cloud(file_path)
                    if not point_cloud.is_empty():
                        points = np.asarray(point_cloud.points)
                        return points, None  # 점 클라우드만 반환
                    else:
                        raise ValueError("파일에 유효한 데이터가 없습니다.")
            elif ext == 'stl':
                mesh = o3d.io.read_triangle_mesh(file_path)
                if not mesh.is_empty():
                    vertices = np.asarray(mesh.vertices)
                    triangles = np.asarray(mesh.triangles)
                    return vertices, triangles
                else:
                    raise ValueError("STL 파일이 비어 있습니다.")
            else:
                raise ValueError("지원하지 않는 파일 형식입니다.")
        except Exception as e:
            self.text_browser.append(f"파일을 로드하는 동안 오류가 발생했습니다: {str(e)}")
            return None, None

class CustomMenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent=None):
        super(CustomMenuBar, self).__init__(parent)
        self.setObjectName("CustomMenuBar")
        self.setup_ui()
        
    def setup_ui(self):
        self.isDragging = False
        self.dragPosition = None
        
        # 로고 이미지 추가
        self.logoLabel = QLabel(self)
        self.logoLabel.setPixmap(QtGui.QPixmap(r'H:\Project\08_clavicle_software_python\sw\v1.0.4\logo2.png').scaled(25, 25, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logoLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # 버튼을 담을 QWidget 생성
        self.buttonWidget = QtWidgets.QWidget(self)
        self.buttonLayout = QtWidgets.QHBoxLayout(self.buttonWidget)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setSpacing(0)

        # 최소화, 최대화, 닫기 버튼 생성
        self.minimize_button = QtWidgets.QPushButton()
        self.minimize_button.setIcon(QtGui.QIcon(r'H:\Project\08_clavicle_software_python\sw\v1.0.4\최소화2.png'))
        self.minimize_button.setIconSize(QtCore.QSize(10, 10))
        self.minimize_button.setFlat(True)
        self.minimize_button.clicked.connect(self.minimize)

        self.maximize_button = QtWidgets.QPushButton()
        self.maximize_button.setIcon(QtGui.QIcon(r'H:\Project\08_clavicle_software_python\sw\v1.0.4\최대화2.png'))
        self.maximize_button.setIconSize(QtCore.QSize(10, 10))
        self.maximize_button.setFlat(True)
        self.maximize_button.clicked.connect(self.maximize)

        self.close_button = QtWidgets.QPushButton()
        self.close_button.setIcon(QtGui.QIcon(r'H:\Project\08_clavicle_software_python\sw\v1.0.4\종료2.png'))
        self.close_button.setIconSize(QtCore.QSize(10, 10))
        self.close_button.setFlat(True)
        self.close_button.clicked.connect(self.close)

        # 버튼들을 레이아웃에 추가
        self.buttonLayout.addWidget(self.minimize_button)
        self.buttonLayout.addWidget(self.maximize_button)
        self.buttonLayout.addWidget(self.close_button)

        # 로고와 버튼들을 메뉴 바에 추가
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.logoLabel)
        self.layout.addStretch()  # 로고와 버튼 사이에 공간을 추가하여 버튼을 오른쪽으로 밀어줌
        self.layout.addWidget(self.buttonWidget)

        self.setLayout(self.layout)

        # 메뉴 항목 생성
        self.create_menus()
        self.setStyleSheet("""
            QMenuBar {
                background-color: #3a3a3a;
                color: white;  
                padding: 7px;  
                padding-left: 20;
            }
            QPushButton {
                background: none;
                border: none;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)

    def create_menus(self):
        # 파일 메뉴
        self.menuFile = QtWidgets.QMenu("파일", self)
        self.actionExit = QtWidgets.QAction("Exit", self)
        self.actionExit.triggered.connect(self.parent().close)
        self.menuFile.addAction(self.actionExit)

        # 불러오기 메뉴
        self.menuLoad = QtWidgets.QMenu("불러오기", self)
        self.actionLoadPLY = QtWidgets.QAction(".ply 파일", self)
        self.actionLoadPLY.triggered.connect(lambda: self.parent().load_file("PLY"))
        self.menuLoad.addAction(self.actionLoadPLY)

        self.actionLoadSTL = QtWidgets.QAction(".stl 파일", self)
        self.actionLoadSTL.triggered.connect(lambda: self.parent().load_file("STL"))
        self.menuLoad.addAction(self.actionLoadSTL)

        self.actionLoadNPY = QtWidgets.QAction(".npy 파일", self)
        self.actionLoadNPY.triggered.connect(lambda: self.parent().load_file("NPY"))
        self.menuLoad.addAction(self.actionLoadNPY)

        self.actionLoadDICOM = QtWidgets.QAction("DICOM 폴더", self)
        self.actionLoadDICOM.triggered.connect(self.parent().load_dicom_folder)
        self.menuLoad.addAction(self.actionLoadDICOM)

        # 자동 분할 메뉴
        self.menuInference = QtWidgets.QMenu("자동 분할", self)
        self.actionAutoSplit = QtWidgets.QAction("골 선택", self)
        self.actionAutoSplit.triggered.connect(self.parent().show_selection_dialog)
        self.menuInference.addAction(self.actionAutoSplit)

        # 플레이트 추천 메뉴
        self.menuPlate = QtWidgets.QMenu("플레이트 추천", self)

        # 도구 메뉴
        self.menuTool = QtWidgets.QMenu("도구", self)
        self.actionPrintDICOM = QtWidgets.QAction("DICOM 정보 출력", self)
        self.actionPrintDICOM.triggered.connect(self.parent().show_dicom_info)
        self.menuTool.addAction(self.actionPrintDICOM)

        self.actionPrintDICOMTags = QtWidgets.QAction("DICOM 태그 정보 출력", self)
        self.actionPrintDICOMTags.triggered.connect(self.parent().show_dicom_tags)
        self.menuTool.addAction(self.actionPrintDICOMTags)

        # self.actionConnectDB = QtWidgets.QAction("Oracle DB 접속", self)
        # self.actionConnectDB.triggered.connect(self.parent().show_connect_db)
        # self.menuTool.addAction(self.actionConnectDB)

        # DB 메뉴
        self.menuConnectDB = QtWidgets.QMenu("DB 접속", self)
        self.actionConnectDB = QtWidgets.QAction("Oracle DB 접속", self)
        self.actionConnectDB.triggered.connect(self.parent().show_connect_db)
        self.menuConnectDB.addAction(self.actionConnectDB)

        self.actionUploadDB = QtWidgets.QAction("DB 이미지 업로드", self)
        self.actionUploadDB.triggered.connect(self.parent().DB_upload_img)
        self.menuConnectDB.addAction(self.actionUploadDB)

        self.actionDownloadDB = QtWidgets.QAction("DB 이미지 다운로드", self)
        self.actionDownloadDB.triggered.connect(self.parent().DB_download_img)
        self.menuConnectDB.addAction(self.actionDownloadDB)

        self.actionCloseDB = QtWidgets.QAction("DB 종료", self)
        self.actionCloseDB.triggered.connect(self.parent().close_connect_db)
        self.menuConnectDB.addAction(self.actionCloseDB)


        # 메뉴 바에 추가
        self.addMenu(self.menuFile)
        self.addMenu(self.menuLoad)
        self.addMenu(self.menuInference)
        self.addMenu(self.menuPlate)
        self.addMenu(self.menuTool)
        self.addMenu(self.menuConnectDB)

    def minimize(self):
        self.parentWidget().showMinimized()

    def maximize(self):
        window_state = self.parentWidget().windowState()
        if window_state & QtCore.Qt.WindowMaximized:
            self.parentWidget().showNormal()
        else:
            self.parentWidget().showMaximized()

    def close(self):
        self.parentWidget().close()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.isDragging = True
            self.dragPosition = event.globalPos() - self.parentWidget().frameGeometry().topLeft()
            event.accept()
        super(CustomMenuBar, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isDragging and event.buttons() == QtCore.Qt.LeftButton:
            self.parentWidget().move(event.globalPos() - self.dragPosition)
            event.accept()
        super(CustomMenuBar, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.isDragging = False
        self.dragPosition = None
        event.accept()
        super(CustomMenuBar, self).mouseReleaseEvent(event)

class DBConnectionWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DBConnectionWindow, self).__init__(parent)

        self.cursorDB = None
        self.connectionDB = None

        self.setWindowTitle('Oracle DB 접속 정보 입력')
        self.setGeometry(300, 300, 400, 200)
        
        layout = QVBoxLayout(self)
        
        self.hostLabel = QLabel('호스트 (IP 주소 또는 도메인):')
        self.hostInput = QLineEdit()
        layout.addWidget(self.hostLabel)
        layout.addWidget(self.hostInput)
        
        self.portLabel = QLabel('포트:')
        self.portInput = QLineEdit()
        layout.addWidget(self.portLabel)
        layout.addWidget(self.portInput)
        
        self.sidLabel = QLabel('SID:')
        self.sidInput = QLineEdit()
        layout.addWidget(self.sidLabel)
        layout.addWidget(self.sidInput)
        
        self.userLabel = QLabel('사용자 이름:')
        self.userInput = QLineEdit()
        layout.addWidget(self.userLabel)
        layout.addWidget(self.userInput)
        
        self.passwordLabel = QLabel('비밀번호:')
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.passwordLabel)
        layout.addWidget(self.passwordInput)
        
        self.connectButton = QPushButton('연결')
        self.connectButton.clicked.connect(self.connectToDB)
        layout.addWidget(self.connectButton)
        
        self.setLayout(layout)

        center_util = CenterOnMouseMonitor(self)
        center_util.center()
    
    def connectToDB(self):
        host = self.hostInput.text()
        port = self.portInput.text()
        sid = self.sidInput.text()
        user = self.userInput.text()
        password = self.passwordInput.text()
        
        dsn = cx_Oracle.makedsn(host, port, sid=sid)
        try:
            connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
            QMessageBox.information(self, '연결 성공', '데이터베이스에 성공적으로 연결되었습니다.')
            self.parent().file_loader.text_browser.append("데이터베이스 접속 성공.")
            #connection.close()
            self.connectionDB = connection
            self.cursorDB = connection.cursor()
            
            self.accept()
        except cx_Oracle.DatabaseError as e:
            QMessageBox.critical(self, '연결 실패', f'데이터베이스 연결에 실패했습니다: {e}')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 기본 제목 표시줄 제거
        self.setWindowIcon(QIcon(r'H:\Project\08_clavicle_software_python\sw\v1.0.4\logo.jpg'))  # 로고 이미지 경로 설정
        self.setupUi()
        self.file_loader = FileLoader(self.textBrowser)
        self.PatientTag = pd.DataFrame()
        self.is_maximized = False  # 화면이 최대화된 상태인지 여부를 추적합니다.
        self.folder_path = ''
        self.db = None

    def setupUi(self):
        # 다크 테마 배경색
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QMenuBar {
                background-color: #3a3a3a;
                color: white;  
                padding: 5px;
            }
            QMenuBar::item {
                background-color: #3a3a3a;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #4a4a4a;
            }
            QMenu {
                background-color: #3a3a3a;
                color: white;
            }
            QMenu::item:selected {
                background-color: #4a4a4a;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QTextBrowser {
                background-color: #3a3a3a;
                color: #dcdcdc;
                border: 1px solid #555;
            }
            QTreeView {
                background-color: #3a3a3a;
                color: #dcdcdc;
                border: 1px solid #555;
            }
            QSplitter::handle {
                    background-color: #4a4a4a;  /* 원하는 색상으로 변경 */
            } 
        """)

        self.data = 0
        self.size_width = 1200
        self.size_height = 602
        self.size_bazel = 0

        self.setObjectName("MainWindow")
        self.resize(self.size_width + self.size_bazel, self.size_height)

        self.centralwidget = QtWidgets.QWidget(self)
        self.menuBar = CustomMenuBar(self)
        self.setMenuBar(self.menuBar)
        self.centralwidget.setObjectName("centralwidget")

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self.centralwidget)
        self.splitter.setObjectName("splitter")

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

        self.update_layout()  # 초기 레이아웃 설정

    def show_selection_dialog(self):
        dialog = SelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.file_loader.text_browser.append(r"{}을 선택했습니다.".format(dialog.selected_model))
            self.file_loader.text_browser.append(str(self.PatientTag))
            # 처리 클래스 호출
            clss_bone_clavicle = BoneClavicle(self)
            #clss_bone_clavicle.exec_()

            


    def update_layout(self):
        # 메뉴 바 크기와 위치 설정
        self.menuBar.setGeometry(0, 0, self.width(), 30)  # 메뉴 바 높이 조정

        # 중앙 위젯의 크기와 위치 설정
        self.centralwidget.setGeometry(0, 30, self.width(), self.height() - 30)

        # splitter의 크기와 위치 설정
        self.splitter.setGeometry(0, 0, self.centralwidget.width(), self.centralwidget.height() - 110)

        # textBrowser의 크기와 위치 설정
        self.textBrowser.setGeometry(0, self.splitter.height(), self.centralwidget.width(), 110)

        # splitter의 크기 비율 조정
        self.splitter.setSizes([int(self.size_width / 4), int(3 * self.size_width / 4)])   

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        self.update_layout()

    def load_file(self, file_type):
        file_path = self.file_loader.load_file(file_type)
        if file_path:
            self.graphicsView.clear_items()  # 이전 항목 삭제
            vertices, faces = self.file_loader.parse_mesh(file_path)
            if vertices is not None:
                if faces is not None:
                    # 삼각형 메시의 경우
                    self.graphicsView.plot_mesh(vertices, faces, file_type)
                else:
                    # 점 클라우드의 경우
                    self.graphicsView.plot_point_cloud(vertices)

    def show_dicom_info(self):
        dialog = DICOMInfoDialog(self.file_loader.dicom_data, self)
        dialog.exec_()

    def show_dicom_tags(self):
        dialog = DICOMTagsDialog(self.file_loader.dicom_tags_df, self)
        dialog.exec_()

    def show_connect_db(self):
        self.db = DBConnectionWindow(self)
        self.db.exec_()

    def DB_upload_img(self):
        image_path = r"H:\Project\08_clavicle_software_python\sw\v1.0.5\img\sample.png"
        print(image_path)
        with open(image_path, 'rb') as file:
            image_data = file.read()

        sql = "INSERT INTO image_table (image_name, image_data) VALUES (:name, :data)"
        self.db.cursorDB.execute(sql, name="sample.png", data=image_data)
        self.db.connectionDB.commit()
        self.file_loader.text_browser.append("데이터베이스에 이미지 업로드가 완료되었습니다.")

    def DB_download_img(self):
        output_path = r"H:\Project\08_clavicle_software_python\sw\v1.0.5\img\downloaded_sample.png"
        sql_last_id = "SELECT MAX(id) AS last_id FROM image_table"
        self.db.cursorDB.execute(sql_last_id)
        result = self.db.cursorDB.fetchone()
        image_id = result[0]

        sql = "SELECT image_data FROM image_table WHERE id = :id"
        self.db.cursorDB.execute(sql, id=image_id)
        result = self.db.cursorDB.fetchone()
        
        if result:
            lob = result[0]
            # LOB 데이터 읽기
            image_data = lob.read()
            self.file_loader.text_browser.append(f"Image data length: {len(image_data)} bytes")
            
            with open(output_path, 'wb') as file:
                file.write(image_data)
            self.file_loader.text_browser.append("Image downloaded successfully!")

    def close_connect_db(self):
        self.db.cursorDB.close()
        self.db.connectionDB.close()
        self.file_loader.text_browser.append("데이터베이스 연결이 종료되었습니다.")

    def extract_voxel_from_dicom(self):
        
        pass

    def load_dicom_folder(self):
        self.folder_path = self.file_loader.load_file("DICOM")
        

        if self.folder_path:
            summary = self.file_loader.summarize_dicom_folder(self.folder_path)
            if summary:
                self.file_loader.text_browser.append("\n")
                self.file_loader.text_browser.append(summary)
        
        self.preprocess_from_dicom(self.folder_path)

        ## 코드 작성
    def preprocess_from_dicom(self, patient_path):

        col=['PatientNumber','AccessionNumber', 'SeriesDescription', 'SliceThickness', 'PixelSpacing', 'PatientSex', 'PatientAge']
        df = pd.DataFrame(columns=col)
        list_total_info=[]
        accession_path = patient_path
        dicom_list = os.listdir(accession_path)
        dicom_path = accession_path+'/'+dicom_list[5]
        medical_image = pydicom.read_file(dicom_path)

        try:
            tag_AccessionNumber=medical_image.AccessionNumber
        except:
            tag_AccessionNumber='No AccessionNumber'
        try:
            tag_SeriesDescription=medical_image.SeriesDescription
        except:
            tag_SeriesDescription='No SeriesDescription'
        try:
            tag_SliceThickness=medical_image.SliceThickness
        except:
            tag_SliceThickness='No SliceThickness'
        try:
            tag_PixelSpacing=medical_image.PixelSpacing
        except:
            tag_PixelSpacing='No PixelSpacing'
        try:
            tag_PatientSex=medical_image.PatientSex
        except:
            tag_PatientSex='No PatientSex'
        try:
            tag_PatientAge=medical_image.PatientAge
        except:
            tag_PatientAge='No PatientAge'
            
        list_single_info=[]
        list_single_info.append(tag_AccessionNumber)
        list_single_info.append(tag_SeriesDescription)
        list_single_info.append(tag_SliceThickness)
        list_single_info.append(tag_PixelSpacing)
        list_single_info.append(tag_PatientSex)
        list_single_info.append(tag_PatientAge)

        list_total_info.append(list_single_info)
        np_total_info = np.array(list_total_info, dtype=object)

        col=['AccessionNumber', 'SeriesDescription', 'SliceThickness', 'PixelSpacing', 'PatientSex', 'PatientAge']
        df = pd.DataFrame(columns=col,data=np_total_info)
        self.file_loader.text_browser.append(str(df))
        self.PatientTag = df

    def toggle_maximize(self):
        if self.is_maximized:
            self.showNormal()
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True

        self.update_layout()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
