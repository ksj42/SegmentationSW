import numpy as np
from mayavi import mlab

# 예제 넘파이 포인트 클라우드 데이터 생성
# 실제 데이터를 사용하려면, 파일에서 데이터를 읽어와 numpy 배열로 변환하세요
num_points = 1000
points = np.load(r"H:\Project\Generated_bone_130-140.npy")
points = np.random.rand(num_points, 3) * 10
# 포인트 클라우드 시각화
def visualize_point_cloud(points):
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]

    mlab.points3d(x, y, z, mode='point', colormap='cool', scale_factor=1)
    mlab.xlabel('X')
    mlab.ylabel('Y')
    mlab.zlabel('Z')
    mlab.show()

visualize_point_cloud(points)


# from vispy import app, scene

# # 캔버스 생성 및 뷰 설정
# canvas = scene.SceneCanvas(keys='interactive', size=(600, 400), show=True)
# view = canvas.central_widget.add_view()

# # 3D 축 추가
# axis = scene.visuals.XYZAxis(parent=view.scene)

# # 카메라 설정
# view.camera = 'turntable'  # 또는 'arcball'

# # 애플리케이션 실행
# if __name__ == '__main__':
#     app.run()