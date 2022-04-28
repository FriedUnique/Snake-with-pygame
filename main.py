from utils import SplashText, Text, Button

import pygame, random, os

from math import ceil
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Vector:
    x: float
    y: float

@dataclass
class Level:
    name: str
    tickSpeed: int
    appleCount: int

@dataclass
class Colors:
    name: str
    chequered0: tuple
    chequered1: tuple
    appleColor: tuple
    backColor : tuple


levels = {
    "easy": Level("easy", 7.5, 3), 
    "hard" : Level("hard", 10, 2), 
    "insane": Level("insane", 15, 1)
    }
LVL = list(levels.keys())[0]

colors = {"green": Colors("green", (170, 215, 81), (155, 200, 73), (156, 50, 50), (237, 246, 249))} 
THEME = "green"

# region init
pygame.init()

GRIDSIZE = Vector(15, 15)             # how many cells are in the grid
CELLSIZE = 40
fieldOffset = Vector(100, 50)

screenX, screenY = (CELLSIZE*GRIDSIZE.x + fieldOffset.x*2, CELLSIZE*GRIDSIZE.y + fieldOffset.y*2)
screen = pygame.display.set_mode((screenX, screenY))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

fontSize = 38 - ceil(700/screenY)*2
scoreText = Text(position=(25, 30), color=(13, 13, 26), text="0", fontSize=42)     # will display the current score

splash = SplashText(screenX, screenY, fontSize=fontSize+20)  # will pop-up after you died
splash.textColor = (156, 50, 50)
splash.bgColor = colors[THEME].chequered1

# directions 
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

#endregion

class MainMenu:
    def __init__(self, levelDict: Dict[str, Level]):
        self.isToggled = True
        self.buttons: Dict[str, Button] = {}

        #! need a better way to spawn the buttons depending on the size of the window. (adapt scale and stuff)

        w, h = int(screenX/2), int(screenY/2)
        keys = list(levelDict.keys())

        self.buttons[keys[0]] = Button(keys[0], (w-int(screenX/4), screenY-150), (15, 6), text=keys[0], onClicked=self.choose, fontSize=fontSize)
        self.buttons[keys[1]] = Button(keys[1], (w, screenY-150), (15, 6), text=keys[1], onClicked=self.choose, fontSize=fontSize)
        self.buttons[keys[2]] = Button(keys[2], (w+int(screenX/4), screenY-150), (15, 6), text=keys[2], onClicked=self.choose, fontSize=fontSize)

        self.titleText = Text((w, h-50), color=(255, 255, 255), text="Snake", fontSize=fontSize+20)
    
    def choose(self, b: Button):
        global LVL
        LVL = b.name
        self.toggle()
        appleSpawn()
        snake.reset()

    def drawMenu(self, screen):
        if not self.isToggled: return

        pygame.draw.rect(screen, (38, 41, 84), (0, 0, screenX, screenY))
        for i, b in enumerate(self.buttons):
            self.buttons[b].draw(screen)

        self.titleText.draw(screen)

    def update(self, screen):
        if not self.isToggled: return

        for i, b in enumerate(self.buttons):
            self.buttons[b].handleEvents()

    def toggle(self):
        self.isToggled = not self.isToggled

        for i, b in enumerate(self.buttons):
            self.buttons[b].isActive = self.isToggled

        self.titleText.isActive = self.isToggled

class Snake:
    def __init__(self):
        self.positions = []
        self.snakeLength = 1
        self.dir = RIGHT
        self.headSprite = self.loadHeadSprite()
        self.bodySprite = self.loadBodySprite()

        self.moved = True
        self.nearApple = False
    
    def loadHeadSprite(self):
        # pygame.Surface((CELLSIZE, CELLSIZE))
        idle = pygame.transform.scale(pygame.image.load(os.path.join("src", "snakeHead_idle.png")), (CELLSIZE, CELLSIZE))
        eat = pygame.transform.scale(pygame.image.load(os.path.join("src", "snakeHead_eat.png")), (CELLSIZE, CELLSIZE))

        return [idle, eat]
    
    def loadBodySprite(self):
        return pygame.transform.scale(pygame.image.load(os.path.join("src", "snakeBody.png")), (CELLSIZE, CELLSIZE))

    def animateMouth(self, radius: int):
        self.nearApple = False
        for apple in apples:
            aPos = apple.position

            if aPos[0] - (radius*CELLSIZE) <= self.positions[0][0] and aPos[0] + (radius*CELLSIZE) >= self.positions[0][0]:
                if aPos[1] - (radius*CELLSIZE) <= self.positions[0][1] and aPos[1] + (radius*CELLSIZE) >= self.positions[0][1]:
                    self.nearApple = True

    def turn(self, targetDir):
        if self.moved == False:

            return

        # you cant move in the opposite direction you are currently moving in
        if self.snakeLength > 1 and (targetDir[0] * -1, targetDir[1] * -1) == self.dir:
            return
        else:
            self.dir = targetDir
            self.moved = False

    def move(self):
        # called before draw
        head = self.positions[0]
        newPos = ((head[0] + (self.dir[0]*CELLSIZE)), head[1] + (self.dir[1]*CELLSIZE))

        # test if collided with wall
        if newPos[0] > screenX - CELLSIZE - fieldOffset.x or newPos[0] < fieldOffset.x or newPos[1] > screenY - CELLSIZE - fieldOffset.y or newPos[1] < fieldOffset.y:
            splash.loadInfo(f"You died! Score: {score}", "MENU", mainMenu.toggle)
            return

        # test if crash into you self
        if len(self.positions) > 2 and newPos in self.positions[2:]:
            splash.loadInfo(f"You died! Score: {score}", "MENU", mainMenu.toggle)
            return
            
        # actual moving
        self.positions.insert(0, newPos) # new head pos
        if len(self.positions) > self.snakeLength:
            self.positions.pop() # default last
        
        #self.animateMouth(2)
        self.moved = True

    def reset(self):
        global score
        scoreText.changeText("0")

        for apple in apples:
            apple.random_pos()

        score = 0
        self.snakeLength = 1
        self.positions = [[0 * CELLSIZE + fieldOffset.x, int(GRIDSIZE.x/2) * CELLSIZE + fieldOffset.y]]
        self.dir = RIGHT

    def draw(self):
        x = int(CELLSIZE/2)

        for body in self.positions:
            # head can rotate. (animation and vfx)
            if body == self.positions[0]:
                rot = min(self.dir[0]*180, 0) + self.dir[1]*-90
                sprite = self.bodySprite # self.headSprite[0] if not self.nearApple else self.headSprite[1]

                img = pygame.transform.rotate(sprite, rot)
                rect = img.get_rect()

                rect.center = (body[0]+x, body[1]+x)

                screen.blit(img, rect)
                continue

            screen.blit(self.bodySprite, self.bodySprite.get_rect(center=(body[0]+x, body[1]+x)))


class Apple:
    def __init__(self):
        self.position = ()
        self.color = colors[THEME].appleColor
        self.random_pos()
    
    def random_pos(self):
        other = []
        for a in apples:
            if a == self: continue
            other.append(a.position)

        
        while True:
            self.position = (random.randint(0, GRIDSIZE.x-1) * CELLSIZE + fieldOffset.x, random.randint(0, GRIDSIZE.y-1) * CELLSIZE + fieldOffset.y)
            if self.position not in snake.positions and self.position not in other:
                break

    def draw(self):
        r = pygame.Rect(self.position, (CELLSIZE, CELLSIZE))
        pygame.draw.rect(screen, self.color, r)


def drawGrid():
    for y in range(0, GRIDSIZE.y):
        for x in range(0, GRIDSIZE.x):
            r = pygame.Rect((x*CELLSIZE + fieldOffset.x, y*CELLSIZE + fieldOffset.y), (CELLSIZE, CELLSIZE))

            if (x+y) % 2 == 0:
                pygame.draw.rect(screen, colors[THEME].chequered0, r)
            else:
                pygame.draw.rect(screen, colors[THEME].chequered1, r)

def draw():
    if mainMenu.isToggled == True or splash.isToggled == True:
        mainMenu.drawMenu(screen)
        splash.draw(screen)
        return

    screen.fill(colors[THEME].backColor)
    drawGrid()
    snake.draw()

    for apple in apples:
        apple.draw()

    scoreText.draw(screen)


def appleSpawn():
    global apples
    apples = []
    for _ in range(levels[LVL].appleCount):
        apples.append(Apple())

    
score = 0
snake = Snake()
mainMenu = MainMenu(levels)
apples: List[Apple] = []


def main():
    global splash, score, snake, mainMenu

    isRunning = True

    while isRunning:
        # switch tickspeed so UI is not slow.
        if mainMenu.isToggled or splash.isToggled:
            clock.tick(20)
        else:
            # the faster the tickspeed the harder the gfame
            clock.tick(levels[LVL].tickSpeed)

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False

            elif event.type == pygame.KEYDOWN:
                # movement
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    snake.turn(UP)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    snake.turn(DOWN)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    snake.turn(LEFT)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    snake.turn(RIGHT)


        # draw and update
        if mainMenu.isToggled == False and splash.isToggled == False:
            snake.move()

            # check apple collision
            for apple in apples:
                if snake.positions[0] == apple.position:
                    snake.snakeLength += 1
                    score += 1
                    scoreText.changeText(str(score))
                    apple.random_pos()
            
            # check won
            if snake.snakeLength == GRIDSIZE.x*GRIDSIZE.y:
                splash.loadInfo(f"You won! Score: {score}", "MENU", snake.reset)
            
        draw()

        mainMenu.update(screen)
        pygame.display.update()

main()