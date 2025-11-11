// Vertex Shader para Phong Shading
// Este shader passa as normais e posições para o fragment shader
// onde os cálculos de iluminação serão feitos por pixel

varying vec3 vertex_normal;      // Normal interpolada para o fragment shader
varying vec3 vertex_position;    // Posição do vértice no espaço da câmera
varying vec3 light_direction;    // Direção da luz

void main() {
    // Transformar a posição do vértice para o espaço da tela
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;

    // Calcular a normal no espaço da câmera
    // Usar a transposta da matriz inversa do ModelView para normais
    vec3 normal_eye = normalize(vec3(gl_ModelViewMatrix * vec4(gl_Normal, 0.0)));
    vertex_normal = normal_eye;

    // Calcular a posição do vértice no espaço da câmera
    vec4 vertex_in_eye = gl_ModelViewMatrix * gl_Vertex;
    vertex_position = vec3(vertex_in_eye);

    // Passar a posição da luz para o fragment shader
    // A luz já está no espaço da câmera
    vec4 light_pos = gl_LightSource[0].position;

    // Se w=1, é luz posicional; se w=0, é luz direcional
    if (light_pos.w == 0.0) {
        // Luz direcional
        light_direction = normalize(vec3(light_pos));
    } else {
        // Luz posicional
        light_direction = normalize(vec3(light_pos) - vertex_position);
    }
}
