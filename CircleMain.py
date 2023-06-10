"""Main program"""

import pygame
import math
from dataclasses import dataclass
from dataclasses import field
import ctypes
import win32gui
from ctypes import wintypes
from threading import Thread
from _thread import interrupt_main

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

	def AccurateTan(self):
		if (self.x == 0):
			point_angle = -math.pi/2
			if self.y > 0:
				point_angle = math.pi/2
		elif (self.y == 0):
			point_angle = math.pi
			if self.x > 0:
				point_angle = 0
		else:
			point_angle = math.atan(self.y / self.x)
			if (self.x < 0):
				point_angle += math.copysign(math.pi, self.y)
		return point_angle
	
	# Arithmetic override methods
	def __add__(self, other):
		return V2(self.x + other.x, self.y + other.y)
	
	def __sub__(self, other):
		return V2(self.x - other.x, self.y - other.y)
	
	def Dot(self, other):
		return self.x * other.x + self.y * other.y

# TODO: distinguish between bouncing and sliding

@dataclass
class Circle:
    # The center of the circle
	center: V2
	# The radius of the circle
	radius: float = 10
	# Velocity of the circle
	velocity: V2 = field(init = False)
	# Recent objects to prevent sticky sliding
	recentObjects: list = field(init = False)
	recentObjectsOld: list = field(init = False)

	# Create velocity after initialization to get around mutability restriction
	def __post_init__(self):
		self.velocity = V2(600, 600)
		self.elasticity = 0.8
		self.recentObjects = []
		self.recentObjectsOld = []

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
		self.center.y += deltaTime * (self.velocity.y + 
				deltaTime * acceleration / 2)
	# Moves the circle to be within the bounds of the window
	def Bound(self, rect):
		#TODO: change this to be using math.max
		if self.center.x > rect.right - self.radius:
			self.center.x = rect.right - self.radius
		if self.center.x < rect.left + self.radius:
			self.center.x = rect.left + self.radius
		if self.center.y > rect.bottom - self.radius:
			self.center.y = rect.bottom - self.radius
		if self.center.y < rect.top + self.radius:
			self.center.y = rect.top + self.radius
	# Sends circle back into boundaries
	def BoundaryCheck(self, rect, wnd_mv):
		# right boundary
		if self.center.x + self.radius > rect.right:
			self.center.x = rect.right * 2 - self.center.x - 2 * self.radius
			self.velocity.x = -self.velocity.x + wnd_mv.x
			self.velocity.Reduce(self.elasticity)
		# left boundary
		if self.center.x - self.radius < rect.left:
			self.center.x = rect.left * 2 - self.center.x + 2 * self.radius
			self.velocity.x = -self.velocity.x + wnd_mv.x
			self.velocity.Reduce(self.elasticity)
			
		# top boundary
		if self.center.y - self.radius < rect.top:
			self.center.y = rect.top * 2 - self.center.y + 2 * self.radius
			self.velocity.y = -self.velocity.y + wnd_mv.y
			self.velocity.Reduce(self.elasticity)

		# bottom boundary
		if self.center.y + self.radius > rect.bottom:
			self.center.y = rect.bottom * 2 - self.center.y - 2 * self.radius
			self.velocity.y = -self.velocity.y + wnd_mv.y
			self.velocity.Reduce(self.elasticity)

	def CalculatePhysics(self, rect, deltaTime):
		self.velocity.y += acceleration * deltaTime

	# Collisions with other objects
	def Collision(self, other):
		# First check if theyre colliding
		distance = offset = V2(other.center.x - self.center.x, other.center.y - 
	      self.center.y).Magnitude()
		offset = distance - self.radius - other.radius
		if (offset <= 0):
			# Including in recent collisions
			self.recentObjects.append(other)
			other.recentObjects.append(self)
			# Calculating mass
			mass_self = math.pow(self.radius, 2)
			mass_other = math.pow(other.radius, 2)
			# Finding scaled distance V2
			dist = other.center - self.center
			dist.Reduce(1/distance)

			# Finding velocity effects
			change = 2 * (self.velocity - other.velocity).Dot(dist) / (mass_self + mass_other)
			self.velocity.x = self.velocity.x - change *  dist.x * mass_other
			self.velocity.y = self.velocity.y - change * dist.y * mass_other
			other.velocity.x = other.velocity.x + change * dist.x * mass_self
			other.velocity.y = other.velocity.y + change * dist.y * mass_self

			# Applying bounce velcoity reductions
			if (self.recentObjectsOld.count(other) == 0):
				self.velocity.Reduce(self.elasticity)
			if (other.recentObjectsOld.count(self) == 0):
				other.velocity.Reduce(self.elasticity)
			
			# Accounting for overlap to prevent sticking
			col_tan = (self.center - other.center).AccurateTan()
			self.Reflect(col_tan, offset / 2)
			other.Reflect(col_tan, -offset / 2)

	# Reflects velocity accross the given angle
	def Reflect(self, ang, offset):
		cur_ang = self.velocity.AccurateTan()
		cur_mag = self.velocity.Magnitude()
		new_ang = ang * 2 - cur_ang + math.pi
		self.center.x -= math.cos(ang) * offset
		self.center.y -= math.sin(ang) * offset

	# Exchanges old recent with recent
	def CycleRecent(self):
		self.recentObjectsOld = self.recentObjects
		self.recentObjects = []


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
	newSelect = False

	while True:
        # Event handling
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				print("Exiting")
				interrupt_main()
				return
			if event.type == pygame.MOUSEBUTTONDOWN:
				# Picking up existing object
				for object in objects:
					if object.Contains(mousePos):
						selected = object
				# Creating new object
				if (selected == None):
					objects.append(Circle(V2(0, 0), 10))
					selected = objects[-1]
					newSelect = True
			if event.type == pygame.MOUSEBUTTONUP:
				selected = None
				newSelect = False
		
		# Calculating deltatime
		clock.tick(60)
		deltaTime = clock.get_time() / 1000

		# Getting window position
		rect = wintypes.RECT()
		ff=ctypes.windll.user32.GetWindowRect(wnd, ctypes.pointer(rect))

		
		# Adjusting boundaries
		rect.right -= 15
		rect.bottom -= 38

		# Getting mouse position
		mouseX, mouseY = pygame.mouse.get_pos()
		mousePos = V2(mouseX + rect.left, mouseY + rect.top)

		# Calculating boundary movement
		wnd_horizontal = (rect.left - old_rect.left) / deltaTime
		wnd_vertical = (rect.bottom - old_rect.bottom) / deltaTime
		wnd_mv = V2(wnd_horizontal, wnd_vertical)
		old_rect = rect

		screen.fill((255, 255, 255))

		# Perform initial movements
		if (deltaTime != 0):
			for object in objects:
				if selected == object:
					object.center = mousePos
					# Keep object in frame
					object.Bound(rect)
					object.velocity = V2(0, 0)
					# If its newly created, have it grow
					if newSelect:
						object.radius += deltaTime * 10
				else:
					object.Move(deltaTime)

		# Perform boundary calcuations
		
		if (deltaTime != 0):
			for object in objects:
				object.BoundaryCheck(rect, wnd_mv)

		# Perform physics calculations
		if (deltaTime != 0):
			for object in objects:
				object.CalculatePhysics(rect, deltaTime)

		# Check for collisions
		if (deltaTime != 0):
			for object in objects:
				object.CycleRecent()
			for object_num in range(len(objects)):
				for object_num_2 in range(object_num + 1, len(objects)):
					objects[object_num].Collision(objects[object_num_2])

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
	#objects.append(Circle(V2((rect.left + rect.right)/2, rect.bottom - 80), 30))
	#objects.append(Circle(V2((rect.left + rect.right)/2, rect.bottom - 160), 20))
	#objects.append(Circle(V2((rect.left + rect.right)/2, rect.bottom - 240), 10))


	# Begin thread
	thread = Thread(target = lambda: run(screen, objects), daemon = True)
	thread.start()

	# Main basic drawing sequence
	try:
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
	except KeyboardInterrupt:
		pygame.quit()