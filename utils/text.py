from utils import Button

import pygame
pygame.init()

class Text:
    """
    Displays the text when the 'draw(surface)' method is called.
    """
    def __init__(self, position = (0, 0), color = (255, 255, 255), fontSize = 32, text = "", active=True):
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, fontSize)
        self.position = position

        self.isActive = active

        self.txt_surface = self.font.render(self.text, True, self.color) #change
        self.rect = self.txt_surface.get_rect(center=(self.position[0], self.position[1]))

    def draw(self, surface):
        if not self.isActive: return

        surface.blit(self.txt_surface, self.rect) #blit a image
    
    def changeText(self, newText: str):
        self.text = newText
        self.txt_surface = self.font.render(self.text, True, self.color) #change
        self.rect = self.txt_surface.get_rect(center=(self.position[0], self.position[1]))
    
    def SetActive(self, activate):
        self.isActive = activate


class SplashText:
    def __init__(self, sWidth, sHeight, fontSize=40):
        self.sDim = (sWidth, sHeight)
        w, h = int(sWidth/2), int(sHeight/2)

        self.bgColor = (0, 0, 0)
        self.textColor = (255, 0, 0)

        self.text = Text((w, h), color=self.textColor, active=False, fontSize=fontSize)
        self.closeButton = Button("okButton", (w, sHeight-50), (15, 6), text="MENU", onClicked=self.accept, active=False)

        self.isToggled = False
        self.acceptFunction = None

    def draw(self, _screen):
        if(self.isToggled):
            pygame.draw.rect(_screen, self.bgColor, (0, 0, self.sDim[0], self.sDim[1]))

            self.text.draw(_screen)
            self.closeButton.draw(_screen)
            self.closeButton.handleEvents()

    def accept(self, _b):
        # close popup 
        if self.acceptFunction != None: self.acceptFunction()

        self.text.SetActive(False)
        self.closeButton.SetActive(False)
        
        self.isToggled = False

    def loadInfo(self, msg: str, bText: str, f = None):
        self.text.color = self.textColor

        if f != None: self.acceptFunction = f

        self.closeButton.changeText(bText)
        self.closeButton.SetActive(True)

        self.text.changeText(msg)
        self.text.SetActive(True)
        self.isToggled = True

"""
def blit_text(self, surface, text, pos, font):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, True, self.color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.
"""