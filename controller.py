import glfw
from typing import Optional

class Controller():
    # declarar tipo de chansey
    flappy_bird: Optional['FlappyBird'] # 'Chansey'
    tubes: Optional['TubeCreator']
    tube: Optional['Tube']


    def __init__(self): # referencia a objetos
        self.flappy_bird = None
        self.tubes = None

    def set_flappy_bird(self, flappy_bird):
        self.flappy_bird = flappy_bird

    def set_tubes(self, tubes):
        self.tubes = tubes
         
    def on_key(self, window, key, scancode, action, mods):

        if not self.flappy_bird.alive:
            print("You've already lost!")
            return
        
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return

        # todo add if nothign --> down
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

        elif (key == glfw.KEY_UP or key == glfw.KEY_SPACE) and action == glfw.PRESS:
            print("move up")
            self.flappy_bird.move_up()

        elif (key == glfw.KEY_UP or key == glfw.KEY_SPACE) and action == glfw.RELEASE:
            print("move down")
            self.flappy_bird.move_down()

        elif key == glfw.KEY_DOWN and action == glfw.PRESS:
            self.flappy_bird.move_down()

        else:
            print('Unknown key')

    def clear_gpu(self):
        self.flappy_bird.clear
        self.tubes.clear
