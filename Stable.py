"""Main program"""

import pygame
from dataclasses import dataclass
from dataclasses import field
import math

global acceleration
global window_size
acceleration = 500
window_size = [500, 500]

@dataclass
class V2:
    x: float
    y: float

@dataclass
class Rect:
    # Center of the rectangle
    position: V2
    # Height of rectangle
    height: float
    # Width of rectangle
    width: float
    # Angle from rectangle to center of right edge
    angle: float = 0
    # Counterclowise angular velocity
    angular_velocity: float = 0
    # Velocity of position
    velocity: float = field(init = False)
    # Angle used for position calculations
    diagonal_angle: float = field(init = False)
    diagonal_length: float = field(init = False)

    # Calculate corner angle to avoid calculating it multiple times
    def __post_init__(self):
        velocity = V2(0, 0)
        self.diagonal_angle = math.atan(self.height / self.width)
        self.diagonal_length = math.sqrt(self.height * self.height + 
                                           self.width * self.width) / 2

    # Converts into polygon representation, ccw starting from top left
    def ConvertRect(self):
        return [[self.position.x + self.diagonal_length * 
                   math.cos(self.angle + self.diagonal_angle),
                 self.position.y + self.diagonal_length * 
                   math.sin(self.angle + self.diagonal_angle)],
                 [self.position.x + self.diagonal_length * 
                   math.cos(self.angle - self.diagonal_angle),
                 self.position.y + self.diagonal_length * 
                   math.sin(self.angle - self.diagonal_angle)],
                 [self.position.x + self.diagonal_length * 
                   math.cos(self.angle + self.diagonal_angle + math.pi),
                 self.position.y + self.diagonal_length * 
                   math.sin(self.angle + self.diagonal_angle + math.pi)],
                 [self.position.x + self.diagonal_length * 
                   math.cos(self.angle - self.diagonal_angle + math.pi),
                 self.position.y + self.diagonal_length * 
                   math.sin(self.angle - self.diagonal_angle + math.pi)]]

    # Checks if a given point lies within the rectangle
    def Contains(self, point):
        distX = point.x - self.position.x
        distY = point.y - self.position.y
        #finding angle and distance
        # Edge cases
        if (distX == 0):
            point_angle = -math.pi/2
        elif (distY == 0):
            point_angle = 0
        else:
            point_angle = math.atan(distY / distX)
            if (distX < 0):
                point_angle += math.copysign(math.pi, distY)
        point_distance = math.sqrt(distX * distX + distY * distY)
        # Find the rotated distance between point and position
        total_angle = self.angle - point_angle
        rotX = point_distance * math.cos(total_angle)
        rotY = point_distance * math.sin(total_angle)
        if (abs(rotX) <= self.width / 2 and abs(rotY) <= self.height / 2):
            return True
        return False

    def CalculatePhysics(self, deltaTime):
        self.angle += deltaTime * math.pi / 6
        if self.angle >= math.pi:
            self.angle -= 2 * math.pi
        pass
    
if __name__ == '__main__':

    # Initialize pygame
    pygame.init()
    pygame.display.set_caption('Engine')
    screen = pygame.display.set_mode([window_size[0], window_size[1]])
    # Initial setup
    # Array of objects
    objects = []
    objects.append(Rect(V2(100, 100), 100, 100, angle = math.pi/4))
    # Clock
    clock = pygame.time.Clock()
    clock.tick()
    deltaTime = 0

    # Mouse
    mouseDown = True
    mouseX, mouseY = 0, 0
    # Main basic drawing sequence
    while True:
        # Getting mouse position
        mouseX, mouseY = pygame.mouse.get_pos()
        mousePos = V2(mouseX, mouseY)
        # pygame events
        for event in pygame.event.get():
            # quitting pygame
            if event.type in [pygame.QUIT]:
                pygame.quit()
                raise SystemExit
            # mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

        # Calculating deltatime
        clock.tick(60)
        deltaTime = clock.get_time()
                
        screen.fill((255, 255, 255))

        # Perform physics calculations
        if (deltaTime != 0):
            for object in objects:
                object.CalculatePhysics(deltaTime/1000)

        # Display objects
        for object in objects:
            if (object.Contains(mousePos)):
              pygame.draw.polygon(screen, pygame.Color('green'), 
                object.ConvertRect())
            else:
              pygame.draw.polygon(screen, pygame.Color('red'), 
                object.ConvertRect())
                
        
        pygame.display.flip()
        
    # End pygame
    pygame.quit()
                
        
        