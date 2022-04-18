import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
from grafica.images_path import getImagesPath
from OpenGL.GL import GL_STATIC_DRAW, GL_TRUE, GL_REPEAT, GL_NEAREST, glUniformMatrix4fv, glGetUniformLocation #,glClearColor

from typing import List
from random import random, choice
# drawSceneGraphNode ? what does it

def create_gpu(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpu

def modify_texture_flappy(gpu_flappy, moving):
    """
    If flappy bird is:
    moving down --> -1
    moving up --> 1
    not moving --> 0
    """
    if(moving == 1):
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_up.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    if(moving == 0):
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_center.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    if(moving == -1):
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_down.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    body_flappy = sg.SceneGraphNode('body_flappy') # todo check if we need to clear it
    body_flappy.transform = tr.scale(0.01, 0.01, 1)
    body_flappy.childs += [gpu_flappy]

    flappy = sg.SceneGraphNode('flappy')
    flappy.childs += [body_flappy]
    return flappy

class FlappyBird(object):
    
    def __init__(self, pipeline):
        shape_flappy = bs.createTextureQuad(1,1)
        gpu_flappy = create_gpu(shape_flappy, pipeline)
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_center.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        body_flappy = sg.SceneGraphNode('body_flappy') # todo check if we need to clear it
        body_flappy.transform = tr.uniformScale(0.1)
        body_flappy.childs += [gpu_flappy]

        flappy = sg.SceneGraphNode('flappy')
        flappy.childs += [body_flappy]

        self.model = flappy # todo: why not body_flappy
        self.pos_x = 0.2 # initial position
        self.pos_y = 0.5 # initial position
        self.alive = True
        self.moving = 0 # -1 down, 0 center, 1 up

    def draw(self, pipeline):
        self.model.transform = tr.matmul([
            tr.translate(self.pos_x, self.pos_y, 0),
            tr.uniformScale(0.3)
        ])
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def move_up(self):
        if self.alive:
            if(self.pos_y < 1): 
                self.pos_y += 0.2
            self.moving = 1
            # body_flappy = modify_texture_flappy(self.gpu_flappy, self.moving)
            # self.model = body_flappy

    def move_down(self):
        if self.alive:
            if(self.pos_y > 0): 
                self.pos_y -= 0.2
            self.moving = -1
            # body_flappy = modify_texture_flappy(gpu_flappy, self.moving)
            # self.model = body_flappy

    def update(self, deltaTime):
        if self.alive:
            self.pos_y -= deltaTime * 10
            self.moving = 0
            # body_flappy = modify_texture_flappy(gpu_flappy, self.moving)
            # self.model = body_flappy
        # todo else: flappy reverse dead
    
    def game_lost(self, tube_creator: 'TubeCreator'):
        """
        Return true if bird collision with a tube 
        """
        tubes = tube_creator.tubes
        # verify same position on axis x
        for tube in tubes:
            if self.pos_x == tube.pos_x:
                # flappy between tubes
                if self.pos_y > tube.height_inf and self.pos_y < tube.height_sup:
                    return
                else:
                    return true
        return False
        
    def clear(self):
        self.model.clear()
    

class Tube(object):

    def __init__(self, pipeline):
        self.pos_x = -0.7
        self.height_inf = 0.5 #choice([0.3, 0.5, 0.6, 0.7])  # todo make it random

        shape_tube_inf = bs.createTextureQuad(1, 1)#self.height_inf)
        shape_tube_sup = bs.createTextureQuad(1,  1)#0.9 - self.height_inf)

        gpu_tube_inf = create_gpu(shape_tube_inf, pipeline)
        gpu_tube_sup = create_gpu(shape_tube_sup, pipeline)

        gpu_tube_inf.texture = es.textureSimpleSetup(getImagesPath("tube.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        gpu_tube_sup.texture = es.textureSimpleSetup(getImagesPath("tube.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        tube_inf = sg.SceneGraphNode('tube_inf')
        tube_inf.transform = tr.matmul([
            tr.translate(0, -0.5, 0),
            tr.uniformScale(0.3)
        ])
        tube_inf.childs += [gpu_tube_inf]

        tube_sup = sg.SceneGraphNode('tube_sup')
        tube_sup.transform = tr.matmul([
            tr.translate(0, 0.5, 0),
            tr.uniformScale(0.3),
            tr.rotationZ(3.14*180) # todo check this rotation
        ])
        tube_sup.childs += [gpu_tube_sup]

        tube = sg.SceneGraphNode("tube")
        tube.childs = [tube_inf, tube_sup]
        self.model = tube_inf

    @property
    def height_sup(self):
        return 0.9 - self.height_inf

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, -0.5, 1)#self.height_inf, 0)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def update(self, dt):
        self.pos_x -= dt

    def clear(self):
        self.model.clear()

class TubeCreator(object):
    tubes: List['Tube']

    def __init__(self, n_tubes: 'Int'):
        self.tubes = []
        self.n_tubes = n_tubes
        self.on = True

    # def die(self):  # DARK SOULS
    #     glClearColor(1, 0, 0, 1.0)  # Cambiamos a rojo
    #     self.on = False  # Dejamos de generar huevos, si es True es porque el jugador ya perdió

    def create_tube(self, pipeline):
        if len(self.tubes) >= self.n_tubes or not self.on:  # No puede haber un máximo de 10 huevos en pantalla
            return
        if random() < 0.01:
            self.tubes.append(Tube(pipeline))

    def draw(self, pipeline):
        for tube in self.tubes:
            tube.draw(pipeline)
    
    def update(self, dt):
        for tube in self.tubes:
            tube.update(dt)

    def clear(self):
        for tube in self.tubes:
            tube.model.clear()
