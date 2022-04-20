import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
from grafica.images_path import getImagesPath
from OpenGL.GL import GL_STATIC_DRAW, GL_TRUE, GL_REPEAT, GL_NEAREST, glUniformMatrix4fv, glGetUniformLocation, glClearColor

from numpy import arange
from typing import List
from random import random, choice

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
    # glUniform1f(glGetUniformLocation(pipeline.shaderProgram,
    #                 "texture_index"), controller.actual_sprite)
    if(moving == 1):
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_up.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    else: # center or down
        gpu_flappy.texture = es.textureSimpleSetup(getImagesPath("fp_center.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
   
    body_flappy = sg.SceneGraphNode('body_flappy') # todo check if we need to clear it
    body_flappy.transform = tr.uniformScale(size_bird)
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
        shape_flappy = bs.createTextureQuadAdvance(0.18,0.85,0.05,0.95)
        gpu_flappy = create_gpu(shape_flappy, pipeline)

        self.pos_x = -0.7# initial position, constant
        self.pos_y = 0.5 # initial position
        self.alive = True
        self.moving = 0 # 0 down, 1 up
        self.points = 0 # the number of tubes the flappy bird passes throw it
        self.size_bird = 0.25
        self.gpu_flappy = gpu_flappy
        self.model = modify_texture_flappy(self.gpu_flappy, self.moving, self.size_bird) # todo: why not body_flappy
        
    @property
    def width_bird_on_screen(self):
        #2 * (controller.mousePos[0] - width / 2) / width,
        width = 1000
        return 2 * (self.size_bird - width / 2) / width #* width/2

    @property
    def height_bird_on_screen(self):
        height = 800
        return 2 * (height / 2 - self.size_bird) / height


    def draw(self, pipeline):
        rotation = tr.identity()
        # dead
        if not self.alive:
            rotation = tr.matmul([
                tr.rotationZ(-30),
                tr.scale(-1, 1, 0)])# inverse
        # alive
        else:
            alpha = 0 # 3.14*1/7
            # moving up
            if(self.moving == 1): # todo detect when moving up (or create another function that is called from move_up)
                rotation = tr.rotationZ(alpha) 
            # moving down
            else:
                rotation = tr.rotationZ(-alpha)
        # change texture: image flappy
        #print("moving: ", self.moving)
        self.model = modify_texture_flappy(self.gpu_flappy, self.moving, self.size_bird)
        # translate and rotate
        self.model.transform = tr.matmul([
            tr.translate(self.pos_x, self.pos_y, 0),
            rotation
        ])
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def move_up(self):
        #print("move up")
        if self.alive:
            if(self.pos_y < 1): 
                self.pos_y += 0.25# * 300/2#0.15
            self.moving = 1

    def move_down(self):
        if self.alive:
            if(self.pos_y > 0): 
                self.pos_y -= 0.01
            self.moving = 0

    def update(self, deltaTime):
        if self.alive:
            self.pos_y -= deltaTime * 0.7 # todo after X tubes, aumentar esto
            self.moving = 0
    
    def game_lost(self, tube_creator: 'TubeCreator'):
        """
        Return 0 if bird collision with a tube 
        Return 1 if bird pass throw the tube

        https://stackoverflow.com/questions/53423548/opengl-3-0-window-collision-detection#53424612
        """
        # bird axis positions
        print("height: ", self.height_bird_on_screen)
        bird_x_left = self.pos_x - self.width_bird_on_screen/2 
        bird_x_right = self.pos_x + self.width_bird_on_screen/2
        bird_y_inf = self.pos_y - self.height_bird_on_screen/2 
        bird_y_sup = self.pos_y + self.height_bird_on_screen/2 

        #print("bird: ",bird_x_left, bird_x_right, bird_y_inf, bird_y_sup)

        alpha_error = 0.0

        if not ((bird_y_sup < 1) and (bird_y_inf > -1)):
            print("sorry")
            self.alive = False
            self.pos_y = -1 + self.size_bird/2 # todo fix this --> que sea mas lento
            tube_creator.die()
            return
        
        tubes = tube_creator.tubes
        # verify same position on axis x
        for tube in tubes:
            # tubes axis position
            same_axis_x = False
            tube_x_left = round(tube.pos_x - tube.width_screen/2,4)
            tube_x_right = round(tube.pos_x + tube.width_screen/2,4)
            tube_y_inf = round(-1 + tube.height_inf,4) # punto alto del tubo inf
            tube_y_sup = round(1 - tube.height_sup,4) # punto bajo del tubo sup

            print("tube: ", tube_x_left, tube_x_right, tube_y_inf, tube_y_sup)
            # bird collide before passing throw a tube
            if ((bird_x_right > tube_x_left - alpha_error) and (bird_x_right < tube_x_left + alpha_error)):
                print("HEEEEEEEY")
                # check same height
                if((bird_y_inf < (tube_y_inf + alpha_error)) or (bird_y_sup > (tube_y_sup - alpha_error))):
                    print("bird colide oups")
            
            # same height
            if((bird_y_inf < (tube_y_inf + alpha_error)) or ((bird_y_sup > (tube_y_sup - alpha_error)))):
                # bird collide passing throw the tube
                if((bird_x_left > tube_x_left) and (bird_x_left < tube_x_right)):
                    print("colide: finishing")
                    print("1: ", (bird_x_left > tube_x_left))
                    print("2: ", (bird_x_left < tube_x_right))
                if((bird_x_right > tube_x_left) and (bird_x_right < tube_x_right)):
                    print("colide starting")

            # # bird is passing (finishing)
            # if(tube_x_right > bird_x_left and tube_x_right < bird_x_right): same_axis_x = True
            # if(tube_x_left > bird_x_left and tube_x_left < bird_x_right): same_axis_x = True
            # if same_axis_x:
            #     # flappy between tubes
            #     print("altura inf: ",(self.pos_y - self.size_bird ) > (-1 + tube.height_inf)) 
            #     print("altura inf 1: ",(self.pos_y - self.size_bird )) 
            #     print("altura inf 2: ",(-1 + tube.height_inf)) 
            #     print("altura sup: ", (self.pos_y + self.size_bird) < (1 - tube.height_sup))
            #     print("altura sup 1: ", (self.pos_y + self.size_bird) )
            #     print("altura sup 2: ", (1 - tube.height_sup))
            #     if (round(self.pos_y - self.size_bird , 2) > round(-1 + tube.height_inf, 2)) and (round(self.pos_y + self.size_bird, 2) < round(1 - tube.height_sup, 2)):
            #         print("bird pass")
            #         self.points += 1
            #     else:
            #         print("here 3: bird lost")
            #         self.alive = False
            
    def clear(self):
        self.model.clear()
    

class Tube(object):

    def __init__(self, pipeline, pos_x = 1):
        self.pos_x = pos_x
        self.width = 1
        self.width_screen = 0.8
        # create tube with a random dy
        self.height_inf = choice(arange(0.4, 1.2, 0.1))  # todo make it random
        min_dy = 0.2
        max_dy = 2 - self.height_inf - 0.4
        self.height_sup= choice(arange(min_dy, max_dy, 0.1))

        # tube model
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
            tr.scale(self.width, self.height_inf, 0)
        ])
        tube_inf.childs += [gpu_tube_inf]

        tube_sup = sg.SceneGraphNode('tube_sup')
        pos_y = 1 - self.height_sup/2
        tube_sup.transform = tr.matmul([
            tr.translate(0, pos_y, 0),
            tr.rotationZ(3.14), # todo check this rotation
            tr.scale(self.width, self.height_sup, 0)
        ])
        tube_sup.childs += [gpu_tube_sup]

        tube = sg.SceneGraphNode("tube")
        tube.childs = [tube_inf, tube_sup]

        self.model = tube

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0, 0)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def update(self, dt):
        self.pos_x -= dt * 0.5

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
            self.tubes.append(Tube(pipeline)) # todo add a distance between tubes

    def draw(self, pipeline):
        for tube in self.tubes:
            tube.draw(pipeline)
    
    def update(self, dt):
        for tube in self.tubes:
            tube.update(dt)

    def clear(self):
        for tube in self.tubes:
            tube.model.clear()
