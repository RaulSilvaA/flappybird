import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
from grafica.images_path import getImagesPath
from OpenGL.GL import GL_STATIC_DRAW, GL_TRUE, GL_REPEAT, GL_NEAREST, glUniformMatrix4fv, glGetUniformLocation #,glClearColor

from typing import List
from random import random, randint

def create_gpu(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpu

def modify_texture_flappy(gpu_flappy, moving): # todo make it a method!
    """
    If flappy bird is:
    moving down --> -1
    moving up --> 1
    not moving --> 0
    """
    if(moving == 1):
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_up.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    else: # center or down
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_center.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
   
    body_flappy = sg.SceneGraphNode('body_flappy') # todo check if we need to clear it
    body_flappy.transform = tr.uniformScale(0.25)
    body_flappy.childs += [gpu_flappy]

    flappy = sg.SceneGraphNode('flappy')
    flappy.childs += [body_flappy]
    return flappy

def draw_background(pipeline, w, h):
    shape_bg = bs.createTextureQuad(1, 1)
    gpu_bg = create_gpu(shape_bg, pipeline)
    gpu_bg.texture = es.textureSimpleSetup(getImagesPath("background.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

    background = sg.SceneGraphNode('background')
    background.childs = [gpu_bg]

    background.transform = tr.scale(w, h, 0)

    sg.drawSceneGraphNode(background, pipeline, 'transform')

class FlappyBird(object):
    
    def __init__(self, pipeline):
        shape_flappy = bs.createTextureQuad(1,1)
        gpu_flappy = create_gpu(shape_flappy, pipeline)
        # gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_center.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        # body_flappy = sg.SceneGraphNode('body_flappy') # todo check if we need to clear it
        # body_flappy.transform = tr.uniformScale(0.25)
        # body_flappy.childs += [gpu_flappy]

        # flappy = sg.SceneGraphNode('flappy')
        # flappy.childs += [body_flappy]
        self.pos_x = -0.5 # initial position, constant
        self.pos_y = 0.5 # initial position
        self.alive = True
        self.moving = 0 # 0 down, 1 up
        self.points = 0 # the number of tubes the flappy bird passes throw it
        self.gpu_flappy = gpu_flappy
        self.model = modify_texture_flappy(self.gpu_flappy, self.moving) # todo: why not body_flappy

    def draw(self, pipeline):
        rotation = tr.identity()
        # dead
        if not self.alive:
            rotation = tr.matmul([
                tr.rotationZ(-30),
                tr.scale(-1, 1, 0)])# inverse
        # alive
        else:
            # moving up
            if(self.moving == 1):
                rotation = tr.rotationZ(30)
            # moving down
            else:
                rotation = tr.rotationZ(-30)
        # change texture: image flappy
        self.model = modify_texture_flappy(self.gpu_flappy, self.moving)
        # translate and rotate
        self.model.transform = tr.matmul([
            tr.translate(self.pos_x, self.pos_y, 0),
            rotation
        ])
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def move_up(self):
        if self.alive:
            if(self.pos_y < 1): 
                self.pos_y += 0.2
            self.moving = 1

    def move_down(self):
        if self.alive:
            if(self.pos_y > 0): 
                self.pos_y -= 0.05
            self.moving = 0

    def update(self, deltaTime):
        if self.alive:
            self.pos_y -= deltaTime * 0.7 # todo after X tubes, aumentar esto
            self.moving = 0
    
    def game_lost(self, tube_creator: 'TubeCreator'):
        """
        Return 0 if bird collision with a tube 
        Return 1 if bird pass throw the tube
        """
    
        if self.pos_y < -1 or self.pos_y > 1:
            self.alive = False
            tube_creator.die()
            return 0

        tubes = tube_creator.tubes
        # verify same position on axis x
        for tube in tubes:
            if self.pos_x == tube.pos_x:
                # flappy between tubes
                if self.pos_y > (-1 + tube.height_inf) and self.pos_y < (1 - tube.height_sup):
                    self.points += 1
                    return 1
                else:
                    self.alive = False
        return 0
            
    def clear(self):
        self.model.clear()
    

class Tube(object):

    def __init__(self, pipeline):
        self.pos_x = 0
        self.height_inf = randint(0.4, 1.2)  # todo make it random
        min_dy = 0.2
        max_dy = 2 - self.height_inf - 0.4
        self.height_sup= randint(min_dy, max_dy)

        shape_tube_inf = bs.createTextureQuad(1, 1)
        shape_tube_sup = bs.createTextureQuad(1, 1)

        gpu_tube_inf = create_gpu(shape_tube_inf, pipeline)
        gpu_tube_sup = create_gpu(shape_tube_sup, pipeline)

        gpu_tube_inf.texture = es.textureSimpleSetup(getImagesPath("tube.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        gpu_tube_sup.texture = es.textureSimpleSetup(getImagesPath("tube.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        tube_inf = sg.SceneGraphNode('tube_inf')
        pos_y = -1 + self.height_inf/2 # todo check this translation
        tube_inf.transform = tr.matmul([
            tr.translate(0, pos_y, 0),
            tr.scale(0.3, self.height_inf, 0)
        ])
        tube_inf.childs += [gpu_tube_inf]

        tube_sup = sg.SceneGraphNode('tube_sup')
        pos_y = 1 - self.height_sup/2
        tube_sup.transform = tr.matmul([
            tr.translate(0, pos_y, 0),
            tr.rotationZ(180), # todo check this rotation
            tr.scale(0.3, self.height_sup, 0)
        ])
        tube_sup.childs += [gpu_tube_sup]

        tube = sg.SceneGraphNode("tube")
        tube.childs = [tube_inf, tube_sup]

        self.model = tube


    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0, 0)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def update(self, dt):
        self.pos_x -= dt * 0.4

    def clear(self):
        self.model.clear()

class TubeCreator(object):
    tubes: List['Tube']

    def __init__(self, n_tubes: 'Int'):
        self.tubes = []
        self.n_tubes = n_tubes
        self.on = True # create tubes

    def die(self): 
        glClearColor(1, 0, 0, 1.0)  # Cambiamos a rojo
        # todo print game lost
        self.on = False  # stop creating tubes

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
