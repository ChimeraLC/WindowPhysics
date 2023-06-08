"""Main program"""

import pygame
import math
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

	def Magnitude(self):
		return math.sqrt(self.x * self.x + self.y * self.y)

	def Reduce(self, coef):
		self.x *= coef
		self.y *= coef

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
		self.velocity = V2(600, 600)
		self.elasticity = 0.8

	# Draw self
	def Draw(self, screen, rect):
		pygame.draw.circle(screen, pygame.Color("black"), 
							[self.center.x - rect.left,
							self.center.y - rect.top],
							self.radius)
	# Returns true if point is contained within the circle
	def Contains(self, point):
		return V2(point.x - self.center.x, point.y - 
					self.center.y).Magnitude() <= self.radius
	# Initial first movement
	def Move(self, deltaTime):
		self.center.x += self.velocity.x * deltaTime
		self.center.y += self.velocity.y * deltaTime
	# Sends circle back into boundaries
	def BoundaryCheck(self, rect):
		# right boundary
		if self.center.x + self.radius > rect.right:
			self.center.x = rect.right * 2 - self.center.x - 2 * self.radius
			self.velocity.x = -self.velocity.x
			self.velocity.Reduce(self.elasticity)
		# left boundary
		if self.center.x - self.radius < rect.left:
			self.center.x = rect.left * 2 - self.center.x + 2 * self.radius
			self.velocity.x = -self.velocity.x
			self.velocity.Reduce(self.elasticity)
			
		# top boundary
		if self.center.y - self.radius < rect.top:
			self.center.y = rect.top * 2 - self.center.y + 2 * self.radius
			self.velocity.y = -self.velocity.y
			self.velocity.Reduce(self.elasticity)
		# bottom boundary
		if self.center.y + self.radius > rect.bottom:
			self.center.y = rect.bottom * 2 - self.center.y - 2 * self.radius
			self.velocity.y = -self.velocity.y
			self.velocity.Reduce(self.elasticity)

	def CalculatePhysics(self, deltaTime):
		self.velocity.y += acceleration * deltaTime

	# Collisions with other objects
	def Collisions(self):
		pass



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

	# Mouse variables
	mouseX, mouseY = 0, 0
	selected = None

	while True:
        # Event handling
		
		for event in pygame.event.get():
			if event.type in [pygame.QUIT]:
				pygame.quit()
				return
			if event.type == pygame.MOUSEBUTTONDOWN:
				for object in objects:
					if object.Contains(mousePos):
						selected = object
			if event.type == pygame.MOUSEBUTTONUP:
				selected = None
		
		# Calculating deltatime
		clock.tick(60)
		deltaTime = clock.get_time() / 1000

		# Getting window position
		rect = wintypes.RECT()
		ff=ctypes.windll.user32.GetWindowRect(wnd, ctypes.pointer(rect))

		# Getting mouse position
		mouseX, mouseY = pygame.mouse.get_pos()
		mousePos = V2(mouseX + rect.left, mouseY + rect.top)

		wnd_horizontal = (rect.left - old_rect.left) / 60
		#print(wnd_horizontal)
		old_rect = rect
		# Adjusting boundaries
		rect.right -= 15
		rect.bottom -= 38

		screen.fill((255, 255, 255))

		# Perform initial movements
		if (deltaTime != 0):
			for object in objects:
				if selected == object:
					object.center = mousePos
					object.velocity = V2(0, 0)
				else:
					object.Move(deltaTime)

		# Perform boundary calcuations
		
		if (deltaTime != 0):
			for object in objects:
				object.BoundaryCheck(rect)

		# Perform physics calculations
		if (deltaTime != 0):
			for object in objects:
				object.CalculatePhysics(deltaTime)

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
		try:
			wnd = pygame.display.get_wm_info()['window']
		except:
			break
		message = win32gui.GetMessage(wnd, 0, 0)
		#print(message)
		if message[0] != 0:
			win32gui.TranslateMessage(message[1])
			win32gui.DispatchMessage(message[1])
		"""
		for event in pygame.event.get():
			if event.type in [pygame.QUIT]:
				pygame.quit()
				raise SystemExit
		"""