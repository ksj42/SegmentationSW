import glfw
from OpenGL.GL import *
import glm
import numpy as np
import plyfile

# PLY 파일을 읽고 정점 데이터를 가져오는 함수
def read_ply(filename):
    data = plyfile.PlyData.read(filename)
    vertices = np.vstack([data['vertex']['x'], data['vertex']['y'], data['vertex']['z']]).T
    return vertices

# 쉐이더 소스 코드
vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 aPos;

void main()
{
    gl_Position = vec4(aPos, 1.0);
}
"""

fragment_shader_source = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
}
"""

# 메인 함수
def main():
    # GLFW 초기화
    if not glfw.init():
        return

    # GLFW 창 생성
    window = glfw.create_window(800, 600, "Simple PLY Visualization", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # OpenGL 초기화
    glEnable(GL_DEPTH_TEST)

    # 쉐이더 컴파일 및 링크
    shader_program = compile_shader(vertex_shader_source, fragment_shader_source)

    # PLY 파일 읽기
    vertices = read_ply(r'H:\Project\02_CT_segmentation\PointClund_new\data\Generated_bone\v1_9_selected\Generated_bone_120-130.ply')

    # Vertex Buffer Object (VBO) 생성 및 데이터 업로드
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Vertex Array Object (VAO) 생성 및 설정
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    # 메인 루프
    while not glfw.window_should_close(window):
        # 화면 지우기
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 쉐이더 사용
        glUseProgram(shader_program)

        # VAO 바인딩 후 그리기
        glBindVertexArray(vao)
        glDrawArrays(GL_POINTS, 0, len(vertices))

        # 버퍼 교환 및 이벤트 처리
        glfw.swap_buffers(window)
        glfw.poll_events()

    # GLFW 종료
    glfw.terminate()

# 쉐이더 컴파일 함수
def compile_shader(vertex_shader_source, fragment_shader_source):
    # 버텍스 쉐이더 컴파일
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)

    # 컴파일 오류 확인
    if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(vertex_shader)
        glDeleteShader(vertex_shader)
        raise RuntimeError(f"Vertex shader compilation error: {error}")

    # 프래그먼트 쉐이더 컴파일
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    # 컴파일 오류 확인
    if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(fragment_shader)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        raise RuntimeError(f"Fragment shader compilation error: {error}")

    # 프로그램 생성 및 링크
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    # 링크 오류 확인
    if not glGetProgramiv(shader_program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(shader_program)
        glDeleteProgram(shader_program)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        raise RuntimeError(f"Shader program linking error: {error}")

    # 쉐이더 객체 삭제
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program

if __name__ == "__main__":
    main()
