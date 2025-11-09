import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import sin, cos, radians

def draw_sphere():
    quadric = gluNewQuadric()
    # Enable normals for proper lighting
    gluQuadricNormals(quadric, GLU_SMOOTH)
    # Set material properties for the sphere
    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.1, 0.05, 1.0])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.5, 0.2, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
    gluSphere(quadric, 1, 32, 32)
    gluDeleteQuadric(quadric)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption('PyOpenGL Ball Lighting Demo')

    glViewport(0, 0, 800, 600)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 800 / 600, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])

    light_pos = [3.0, 3.0, 3.0, 1.0]
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    light_pos[0] -= 0.2
                if event.key == K_RIGHT:
                    light_pos[0] += 0.2
                if event.key == K_UP:
                    light_pos[1] += 0.2
                if event.key == K_DOWN:
                    light_pos[1] -= 0.2

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(0,0,8, 0,0,0, 0,1,0)
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        draw_sphere()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
