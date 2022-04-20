
import glfw # GLFW just sets up the window and context
import sys
from OpenGL.GL import * #glUseProgram, glClearColor, glEnable, glBlendFunc, glClear, GL_BLEND, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA 

from model import *
from controller import Controller
from utils import draw_image

n_tubes = 3

""" 
TODO:
- fix dx between tubes
- detect when win
- call program "flappy -N"
- show how many points
"""
if __name__ == '__main__':
    
    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1000
    height = 600

    window = glfw.create_window(width, height, 'Wrong Flappy Bird', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    # set the controller
    controller = Controller()

    # set the current window
    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

    # A simple shader program that implements transformations
    pipeline = es.SimpleTextureTransformShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # glfw will swap buffers as soon as possible
    #glfw.swap_interval(0)

    # create objects
    flappy_bird = FlappyBird(pipeline)
    tubes = TubeCreator(n_tubes)

    controller.set_flappy_bird(flappy_bird)
    controller.set_tubes(tubes)

    t0 = 0

    # Application loop
    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # todo check this with the background

        # Using the time as the x_0 parameter
        if flappy_bird.alive:
            ti = glfw.get_time()
            dt = ti - t0
            t0 = ti
        else: 
            dt = 0 # stop the game

        # create tubes
        tubes.create_tube(pipeline, 1)
        tubes.update(dt)
        flappy_bird.update(dt)

        # check if flappy collide with a tube
        flappy_bird.game_lost(tubes)

        # draw the models and background
        if flappy_bird.alive:
            # Setting up the background
            draw_image(pipeline,2,2,"background") 
            # todo detect if pass throw all the tubes
            print("points: ", flappy_bird.points)
            if(flappy_bird.points == n_tubes): # todo fix this
                print("WIN!!!!!")
                draw_image(pipeline,1,1,"win")
        else:
            glClearColor(1, 0, 0, 1.0)
            draw_image(pipeline,1,1,"lose")
            # asign final points

        tubes.draw(pipeline)
        flappy_bird.draw(pipeline)

        
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    controller.clear_gpu()
    glfw.terminate()

    