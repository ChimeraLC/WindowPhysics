"""Main program"""

import pygame
from dataclasses import dataclass
import ctypes
import win32gui
from ctypes import wintypes
from threading import Thread

class Vector2:
    x: float
    y: float

class Rect:
    min: Vector2
    max: Vector2


def run(screen):
    wnd = pygame.display.get_wm_info()['window']
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        rect = wintypes.RECT()
        ff=ctypes.windll.user32.GetWindowRect(wnd, ctypes.pointer(rect))
        print(rect.left,rect.top,rect.right,rect.bottom)
        pygame.display.flip()

# End pygame
pygame.quit()


if __name__ == '__main__':

    # Initialize pygame
    pygame.init()

    screen = pygame.display.set_mode([500, 500])

    # Begin thread
    Thread(target = lambda: run(screen), daemon = True).start()

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
        