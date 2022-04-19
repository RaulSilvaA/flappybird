
import glfw
import sys
from OpenGL.GL import glUseProgram, glClearColor, glEnable, glBlendFunc, glClear, GL_BLEND, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA 

from model import *
from controller import Controller

n_tubes = 10

if __name__ == '__main__':
    
    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 800
    height = 800

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

    # todo: choose a shader program
    # A simple shader program with position and texture coordinates as inputs.
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
        ti = glfw.get_time()
        dt = ti - t0
        t0 = ti

        # create tubes
        tubes.create_tube(pipeline)
        tubes.update(dt)
        flappy_bird.update(dt)

        print("pos y bird: ", flappy_bird.pos_y)

        # check if flappy collide with a tube
        flappy_bird.game_lost(tubes)
        # todo: delete tubes

        # Setting up the background
        draw_background(pipeline,2,2) 
        # draw the models
        flappy_bird.draw(pipeline)
        tubes.draw(pipeline)

        # if not flappy_bird.alive:
        #     print("LOST")
        #     # todo: display LOST on the screen
        
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    controller.clear_gpu()
    glfw.terminate()

    