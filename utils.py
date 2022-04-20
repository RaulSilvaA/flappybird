
from OpenGL.GL import GL_STATIC_DRAW, GL_TRUE, GL_REPEAT, GL_NEAREST

import grafica.easy_shaders as es
import grafica.scene_graph as sg
import grafica.basic_shapes as bs
import grafica.transformations as tr

from grafica.images_path import getImagesPath


def create_gpu(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpu

def modify_texture_flappy(gpu_flappy, moving, size_bird): # todo make it a method!
    """
    If flappy bird is:
    moving down --> -1
    moving up --> 1
    not moving --> 0
    """

    if(moving == 1):
        print("IM FUCKING MOVING")
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_up.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    else: # center or down
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_center.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
   
    body_flappy = sg.SceneGraphNode('body_flappy') # todo check if we need to clear it
    body_flappy.transform = tr.uniformScale(size_bird)
    body_flappy.childs += [gpu_flappy]

    flappy = sg.SceneGraphNode('flappy')
    flappy.childs += [body_flappy]
    return flappy


def draw_image(pipeline, w, h, name_image):
    shape_bg = bs.createTextureQuad(1, 1)
    gpu_bg = create_gpu(shape_bg, pipeline)
    gpu_bg.texture = es.textureSimpleSetup(getImagesPath(name_image + ".png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    background = sg.SceneGraphNode(name_image)
    background.childs = [gpu_bg]

    background.transform = tr.scale(w, h, 0)

    sg.drawSceneGraphNode(background, pipeline, 'transform')

def draw_points(pipeline, number):
    shape_point = bs.createTextureQuadAdvance(0,1,0,1)
    nx0 = 0
    nx1 = nx0 + 0.2
    ny0 = 0
    ny1 = 0.5
    # first row
    if(number == 1):
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny0, ny1)
    if(number == 2):
        nx0 = nx1
        nx1 = nx0 + 0.2
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny0, ny1)
    if(number == 3):
        nx0 = 2*nx1
        nx1 = nx0 + 0.2
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny0, ny1)
    if(number == 4):
        nx0 = 3*nx1
        nx1 = nx0 + 0.2
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny0, ny1)
    if(number == 5):
        nx0 = 4*nx1
        nx1 = nx0 + 0.2
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny0, ny1)

    # second row
    if(number == 6):
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny1, 2*ny1)
    if(number == 7):
        nx0 = nx1
        nx1 = nx0 + 0.2
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny1, 2*ny1)
    if(number == 8):
        nx0 = 2*nx1
        nx1 = nx0 + 0.2
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny1, 2*ny1)
    if(number == 9):
        nx0 = 3*nx1
        nx1 = nx0 + 0.2
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny1, 2*ny1)
    if(number == 0):
        nx0 = 4*nx1
        nx1 = nx0 + 0.2
        shape_point = bs.createTextureQuadAdvance(nx0,nx1, ny1, 2*ny1)


    gpu_point = create_gpu(shape_point, pipeline)
    gpu_point.texture = es.textureSimpleSetup(getImagesPath("points"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    points = sg.SceneGraphNode('points')
    points.childs = [gpu_point]

    points.transform = tr.scale(w, h, 0)

    sg.drawSceneGraphNode(points, pipeline, 'transform')