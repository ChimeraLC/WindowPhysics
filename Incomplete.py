"""Main program"""

import pygame
from dataclasses import dataclass
import ctypes
import win32gui
from ctypes import wintypes
from threading import Thread

global acceleration
global window_size
acceleration = 500
window_size = [300, 300]


@dataclass
class Rect:
    min: list[float]
    max: list[float]
    velocity: list[float]

    # Converts into polygon representation
    def ConvertRect(self):
        return [[self.min[0], self.min[1]], [self.min[0], self.max[1]],
          [self.max[0], self.max[1]], [self.max[0], self.min[1]]]
    
    # Given the upper left corner of the screen corner, converts to polygon
    def ConvertRectShifted(self, corner):
        return [[self.min[0] - corner[0], self.min[1] - corner[1]],
          [self.min[0] - corner[0], self.max[1] - corner[1]],
          [self.max[0] - corner[0], self.max[1] - corner[1]], 
          [self.max[0] - corner[0], self.min[1] - corner[1]]]
    
    def CalculatePhysics(self, rect, deltaTime):

        # Horizontal borders
        if self.max[1] <= rect.bottom:
            change = deltaTime * (self.velocity[1] + deltaTime * acceleration / 2)
            self.max[1] += change
            self.min[1] += change
            self.velocity[1] += acceleration * deltaTime
        
        if self.max[1] >= rect.bottom:
            change = rect.bottom - self.max[1]
            if (self.velocity[1] < change):
                change = deltaTime * (self.velocity[1] + deltaTime * acceleration / 2)
                self.max[1] += change
                self.min[1] += change
                self.velocity[1] += acceleration * deltaTime
            else:
                self.max[1] += change
                self.min[1] += change
                self.velocity[1] = change / deltaTime / 200

        # Vertical borders
        if self.min[0] < rect.left:
            change = rect.left - self.min[0]
            self.min[0] += change
            self.max[0] += change

        if self.max[0] > rect.right:
            change = rect.right - self.max[0]
            self.min[0] += change
            self.max[0] += change

        

def run(screen, objects):
    wnd = pygame.display.get_wm_info()['window']
    clock = pygame.time.Clock()
    clock.tick()
    deltaTime = 0
    while True:
        # Calculating deltatime
        clock.tick(60)
        deltaTime = clock.get_time()
        print(deltaTime)

        rect = wintypes.RECT()
        ff=ctypes.windll.user32.GetWindowRect(wnd, ctypes.pointer(rect))
        # Adjusting boundaries
        rect.right -= 15
        #print(rect.left,rect.top,rect.right,rect.bottom)
        #print(objects[0])
        #print(objects[0].ConvertRectShifted([rect.left, rect.top]))
                
        screen.fill((255, 255, 255))

        # Perform physics calculations
        if (deltaTime != 0):
            for object in objects:
                object.CalculatePhysics(rect, deltaTime/1000)

        # Display objects
        for object in objects:
            pygame.draw.polygon(screen, pygame.Color('red'), 
              object.ConvertRectShifted([rect.left, rect.bottom - window_size[1]]))
        
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
    objects.append(Rect([(rect.left + rect.right)/2 - 15, rect.bottom - 30], 
                        [(rect.left + rect.right)/2 + 15, rect.bottom], [0, 0]))


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
        

    # End pygame
    pygame.quit()