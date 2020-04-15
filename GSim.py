import pygame
import random
import math
import xlrd

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

WINDOW_WIDTH = 460
WINDOW_HEIGHT = 460

REGION_WIDTH = 200
REGION_HEIGHT = 200


BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)

RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
BACKGROUND = ( 255, 255, 220)

BLOCK_SIZE = 50

# === CLASSES === (CamelCase names)

class Button():

    def __init__(self, pos):

        self.image_normal = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image_normal.fill(GREEN)

        self.image_hovered = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image_hovered.fill(RED)

        self.image = self.image_normal
        
        self.rect = self.image.get_rect(topleft=pos)
        #self.rect.center = screen_rect.center

        self.hovered = False
        self.clicked = False

    def update(self):

        if self.hovered:
            self.image = self.image_normal
        else:
            self.image = self.image_hovered
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            #if self.rect.collidepoint(event.pos)
            #    self.hovered = True
            #else:
            #    self.hovered = False
        
            self.hovered = self.rect.collidepoint(event.pos)


class Machine(pygame.sprite.Sprite):
    def __init__(self,pos):
        super(Machine,self).__init__()
        self.id = 0
        self.predecessor = 0
        self.successor = 0
        self.surf = pygame.Surface((20,20))
        self.color = "None"
        self.surf.fill((0,0,0))
        self.setup_time = 10
        self.status_idle = True
        self.status_setup = False
        self.status_running = False

        self.rect = self.surf.get_rect(topleft=pos)

        # self.hovered = False
        self.clicked = False


        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            #if self.rect.collidepoint(event.pos)
            #    self.hovered = True
            #else:
            #    self.hovered = False
        
            self.hovered = self.rect.collidepoint(event.pos)



class Config():
    def __init__(self,filename):
        self.file = filename

        self.wb = xlrd.open_workbook(filename,on_demand = True)
        self.machine_list_sheet = self.wb.sheet_by_name('Machines')
        self.layout_sheet = self.wb.sheet_by_name('Layout')

        self.demand = []
        self.demand_pos = []
        
        self.raw_material = []
        self.raw_material_pos = []


        self.machines_on_layout = []
        self.machine_pos = []
        self.machine_list =[]

        self.update_machine_list()
        self.update_layout()
        self.close_file()
        

    def update_layout(self):
        for i in range(9):
            for j in range(7):
                if ( self.layout_sheet.cell_value(2+i, 1+j) != '' ):
                    self.machines_on_layout.append( [self.layout_sheet.cell_value(2+i, 1+j)])
                    self.machine_pos.append([i,j])
  
        for i in range(7):
            self.raw_material.append([self.layout_sheet.cell_value(11, 1+i)])
            self.raw_material_pos.append([self.layout_sheet.cell_value(11, 1+i)])


        # print (self.machines_on_layout)
        # print (self.machine_pos)
        
               

    def update_machine_list(self):
        for i in range(self.machine_list_sheet.nrows - 1):
            self.machine_list.append( [ self.machine_list_sheet.cell_value(1+i, 0),
                                        self.machine_list_sheet.cell_value(1+i, 1),
                                        self.machine_list_sheet.cell_value(1+i, 2) ])
        # print (self.machine_list)
        

    def close_file(self):
        self.wb.release_resources()
        del self.wb

    





class App():
    def __init__(self):

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.RESIZABLE)
        self.screen_rect = self.screen.get_rect()

        self.clock = pygame.time.Clock()
        self.is_running = False

        self.widgets = []

        self.create_objects()


    def quit(self):
        pygame.quit()

    def create_objects(self):

        size = BLOCK_SIZE + 5
        
        for row in range(5):
            for col in range(5):
                btn = Button((size*col, size*row))
                self.widgets.append(btn)

    # --- functions ---

    def handle_event(self, event):
        for widget in self.widgets:
            widget.handle_event(event)

    def update(self):
        for widget in self.widgets:
            widget.update()



    def draw(self, surface):

        for widget in self.widgets:
            widget.draw(surface)

        #pygame.display.update()

    # --- mainloop --- (don't change it)

    def mainloop(self):

        self.is_running = True

        while self.is_running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False

                # --- objects events ---

                self.handle_event(event)

            # --- updates ---

            self.update()

            # --- draws ---

            self.screen.fill(BACKGROUND)

            self.draw(self.screen)

            pygame.display.update()

            self.clock.tick(25)   #FPS


        self.quit()


if __name__ == '__main__':
    config = Config("Config.xlsx")

    

    # App().mainloop()