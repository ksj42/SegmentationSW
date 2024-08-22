'''
1. AI를 위한 이미지 전처리
'''

import pyqtgraph.opengl as gl
import open3d as o3d
import numpy as np
import pydicom
import pandas as pd
import os
import matplotlib.pyplot as plt

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

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class BoneClavicle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.initUI()
        self.main_window.file_loader.text_browser.append(self.main_window.folder_path)
        self.main_window.file_loader.text_browser.append("BoneClavicle initialization complete.")
        self.generate_voxel_for_AI(self.main_window.folder_path)

    def initUI(self):
        self.setWindowTitle("Bone Image Viewer")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.layout.addWidget(self.confirm_button)

        self.selected_image_index = None

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
        file_len = len(file_list_py)
        study_id = 0
        self.bone_images = []

        for i in range(file_len):
            try:
                medical_image = pydicom.read_file(os.path.join(path, file_list_py[i]))
                image = medical_image.pixel_array

                intercept = medical_image.RescaleIntercept
                slope = medical_image.RescaleSlope
                hu_image = image * slope + intercept

                bone_image = self.window_image(hu_image, 450, 850)
                self.bone_images.append(bone_image)  # bone_image를 리스트에 저장

                # 이미지 저장 코드
                if study_id != int(medical_image.StudyID):
                    study_dir = os.path.join(r'H:\Project\08_clavicle_software_python\sw\v1.0.5\img', medical_image.StudyDescription)
                    os.makedirs(study_dir, exist_ok=True)

                plt.imsave(os.path.join(study_dir, f'img_{i}.png'), bone_image)
                study_id = int(medical_image.StudyID)

            except Exception as e:
                print(f"Error processing {file_list_py[i]}: {e}")
                pass

        self.display_images()

    def numpy_to_qimage(self, image):
        height, width = image.shape
        bytes_per_line = width
        qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        return qimage

    def display_images(self):
        rows = 10
        cols = 10
        for idx, bone_image in enumerate(self.bone_images):
            if idx >= rows * cols:
                break  # 100개 이상의 이미지를 보여주지 않음

            image_label = QLabel(self)
            qimage = self.numpy_to_qimage(bone_image)
            pixmap = QPixmap.fromImage(qimage).scaled(100, 100, Qt.KeepAspectRatio)
            image_label.setPixmap(pixmap)
            image_label.mousePressEvent = lambda event, index=idx: self.select_image(index)
            self.grid_layout.addWidget(image_label, idx // cols, idx % cols)

    def select_image(self, index):
        self.selected_image_index = index
        QMessageBox.information(self, "Image Selected", f"Selected image index: {index}")

    def confirm_selection(self):
        if self.selected_image_index is None:
            QMessageBox.warning(self, "No Selection", "No image selected!")
            return

        start_idx = self.selected_image_index
        end_idx = min(start_idx + 95, len(self.bone_images))

        selected_images = self.bone_images[start_idx:end_idx]
        np_array = np.array(selected_images)
        print("Numpy array shape:", np_array.shape)

        # 이후 np_array를 원하는 대로 처리하면 됩니다.
        QMessageBox.information(self, "Selection Confirmed", f"Selected {len(selected_images)} images from index {start_idx}.")


# class BoneClavicle():
#     def __init__(self, parent=None):
#         self.main_window = parent
#         self.main_window.file_loader.text_browser.append(self.main_window.folder_path)
#         self.main_window.file_loader.text_browser.append("BoneClavicle initialization complete.")
#         self.generate_voxel_for_AI(self.main_window.folder_path)

#     def window_image(self, image, window_center, window_width):
#         img_min = window_center - window_width // 2
#         img_max = window_center + window_width // 2
#         window_image = image.copy()
#         window_image[window_image < img_min] = img_min
#         window_image[window_image > img_max] = img_max
#         return window_image

#     def generate_voxel_for_AI(self, path):

#         file_list = os.listdir(path)
#         file_list_py = [file for file in file_list if file.endswith('.dcm')] ## 파일명 끝이 .csv인 경우

#         file_len=len(file_list_py)
#         study_id=0
#         for i in range(file_len):
#             try:
#                 medical_image = pydicom.read_file(path+'\\'+file_list_py[i])
#                 image = medical_image.pixel_array

#                 intercept = medical_image.RescaleIntercept
#                 slope = medical_image.RescaleSlope
#                 hu_image = image * slope + intercept

#                 bone_image = self.window_image(hu_image, 450, 850)

        
#                 if study_id != int(medical_image.StudyID):
#                     os.mkdir(r'H:\Project\08_clavicle_software_python\sw\v1.0.5\img\\{}'.format(medical_image.StudyDescription))
#                     plt.imsave(r'H:\Project\08_clavicle_software_python\sw\v1.0.5\img\\{}\\img_{}.png'.format(medical_image.StudyDescription,i),bone_image)
#                 else:
#                     plt.imsave(r'H:\Project\08_clavicle_software_python\sw\v1.0.5\img\\{}\\img_{}.png'.format(medical_image.StudyDescription,i),bone_image)

#                 study_id=int(medical_image.StudyID)
#             except:
#                 pass
        


class SelectionDialog(QDialog):

    def __init__(self, parent=None):
        super(SelectionDialog, self).__init__(parent)
        self.setWindowTitle("부위 선택")
        self.setGeometry(100, 100, 300, 200)
        self.selected_model = ''

        layout = QVBoxLayout(self)

        # 라디오 버튼 생성
        self.radio_clavicle = QRadioButton("쇄골", self)
        self.radio_scapula = QRadioButton("견갑골", self)

        # 버튼 그룹 생성
        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.radio_clavicle)
        self.button_group.addButton(self.radio_scapula)

        # 레이아웃에 라디오 버튼 추가
        layout.addWidget(self.radio_clavicle)
        layout.addWidget(self.radio_scapula)

        # 확인 버튼 생성 및 추가
        self.confirm_button = QPushButton("확인", self)
        layout.addWidget(self.confirm_button)

        # 확인 버튼 클릭 시 처리
        self.confirm_button.clicked.connect(self.on_confirm)

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
        self.menuMapping = QtWidgets.QMenu("플레이트 추천", self)

        # 도구 메뉴
        self.menuTool = QtWidgets.QMenu("도구", self)
        self.actionPrintDICOM = QtWidgets.QAction("DICOM 정보 출력", self)
        self.actionPrintDICOM.triggered.connect(self.parent().show_dicom_info)
        self.menuTool.addAction(self.actionPrintDICOM)

        self.actionPrintDICOMTags = QtWidgets.QAction("DICOM 태그 정보 출력", self)
        self.actionPrintDICOMTags.triggered.connect(self.parent().show_dicom_tags)
        self.menuTool.addAction(self.actionPrintDICOMTags)

        # 메뉴 바에 추가
        self.addMenu(self.menuFile)
        self.addMenu(self.menuLoad)
        self.addMenu(self.menuInference)
        self.addMenu(self.menuMapping)
        self.addMenu(self.menuTool)

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
            clss_bone_clavicle.show()

            


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
