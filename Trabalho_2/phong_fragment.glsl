// Fragment Shader para Phong Shading
// Este shader calcula a iluminação POR PIXEL usando o modelo de Phong
// Modelo: I = I_ambient + I_diffuse + I_specular

varying vec3 vertex_normal;      // Normal interpolada do vertex shader
varying vec3 vertex_position;    // Posição do fragmento
varying vec3 light_direction;    // Direção da luz

void main() {
    // Normalizar a normal (interpolação pode desnormalizar)
    vec3 N = normalize(vertex_normal);

    // Normalizar a direção da luz
    vec3 L = normalize(light_direction);

    // Calcular a direção da câmera (do fragmento para a câmera)
    // No espaço da câmera, a câmera está na origem (0,0,0)
    vec3 V = normalize(-vertex_position);

    // Calcular o vetor de reflexão da luz
    // R = 2(N·L)N - L  (fórmula da reflexão)
    vec3 R = reflect(-L, N);

    // --- COMPONENTE AMBIENTE (ambient) ---
    // Luz ambiente é constante, não depende da geometria
    vec3 ambient = gl_LightSource[0].ambient.rgb * gl_FrontMaterial.ambient.rgb;

    // --- COMPONENTE DIFUSA (diffuse) ---
    // Calcula quanto da luz atinge a superfície diretamente
    // Usa a lei de Lambert: I_d = I_light * k_d * (N·L)
    float diff_intensity = max(dot(N, L), 0.0);
    vec3 diffuse = gl_LightSource[0].diffuse.rgb *
                   gl_FrontMaterial.diffuse.rgb *
                   diff_intensity;

    // --- COMPONENTE ESPECULAR (specular) ---
    // Calcula o brilho especular (reflexos)
    // Usa o modelo de Phong: I_s = I_light * k_s * (R·V)^shininess
    float spec_intensity = 0.0;
    if (diff_intensity > 0.0) {
        // Só calcular especular se a superfície está voltada para a luz
        // Usar um shininess mínimo para evitar valores muito altos
        float shininess = max(gl_FrontMaterial.shininess, 4.0);
        spec_intensity = pow(max(dot(R, V), 0.0), shininess);
    }
    vec3 specular = gl_LightSource[0].specular.rgb *
                    gl_FrontMaterial.specular.rgb *
                    spec_intensity;

    // --- COR FINAL ---
    // Soma de todas as componentes (modelo de Phong completo)
    vec3 final_color = ambient + diffuse + specular;

    // Garantir que a cor está no intervalo [0, 1]
    final_color = clamp(final_color, 0.0, 1.0);

    // Definir a cor final do pixel com alpha = 1.0 (opaco)
    gl_FragColor = vec4(final_color, 1.0);
}
