"""Main program"""

import pygame
from dataclasses import dataclass
from dataclasses import field
import ctypes
import win32gui
from ctypes import wintypes
from threading import Thread

global acceleration
global window_size
acceleration = 500
window_size = [300, 300]
@dataclass
class V2:
    x: float
    y: float

    # Returns coordinate representation
    def Coords(self):
        return [self.x, self.y]

@dataclass
class Circle:
    # The center of the circle
    center: V2
    # The radius of the circle
    radius: float = 10
    # Velocity of the circle
    velocity: V2 = field(init = False)

    # Create velocity after initialization to get around mutability restriction
    def __post_init__(self):
        velocity = V2(0, 0)

    # Draw self
    def Draw(self, screen, rect):
        pygame.draw.circle(screen, pygame.Color("black"), 
                           [self.center.x - rect.left,
                           self.center.y - rect.top],
                           self.radius)
 

def run(screen, objects):
    # Time calculations
    clock = pygame.time.Clock()
    clock.tick()
    deltaTime = 0

    # Initial window position setup
    wnd = pygame.display.get_wm_info()['window']
    rect = wintypes.RECT()
    ff=ctypes.windll.user32.GetWindowRect(wnd, ctypes.pointer(rect))
    old_rect = rect
    while True:
        # Calculating deltatime
        clock.tick(60)
        deltaTime = clock.get_time()
        rect = wintypes.RECT()

        ff=ctypes.windll.user32.GetWindowRect(wnd, ctypes.pointer(rect))

        wnd_horizontal = (rect.left - old_rect.left) / 60
        print(wnd_horizontal)
        old_rect = rect
        # Adjusting boundaries
        rect.right -= 15

        screen.fill((255, 255, 255))

        

        # Perform physics calculations
        if (deltaTime != 0):
            for object in objects:
                #object.CalculatePhysics(rect, deltaTime/1000)
                pass

        # Display objects
        for object in objects:
            object.Draw(screen, rect)
        
        pygame.display.flip()


if __name__ == '__main__':

    # Initialize pygame
    pygame.init()
    pygame.display.set_caption('Engine')
    screen = pygame.display.set_mode([window_size[0], window_size[1]])
    # Initial setup
    # Array of objects
    objects = []

    # Get the initial positions
    wnd = pygame.display.get_wm_info()['window']
    rect = wintypes.RECT()
    ff=ctypes.windll.user32.GetWindowRect(wnd, ctypes.pointer(rect))
    print(rect.left,rect.top,rect.right,rect.bottom)
    objects.append(Circle(V2((rect.left + rect.right)/2, rect.bottom - 80), 30))


    # Begin thread
    Thread(target = lambda: run(screen, objects), daemon = True).start()

    # Main basic drawing sequence
    while True:
        
        wnd = pygame.display.get_wm_info()['window']
        message = win32gui.GetMessage(wnd, 0, 0)
        #print(message)
        if message[0] != 0:
            win32gui.TranslateMessage(message[1])
            win32gui.DispatchMessage(message[1])
        
        for event in pygame.event.get():
            if event.type in [pygame.QUIT]:
                pygame.quit()
                raise SystemExit