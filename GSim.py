import pygame
import xlrd
import tkinter as tk

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 1388
SCREEN_HEIGHT = 800

WINDOW_WIDTH = 460
WINDOW_HEIGHT = 460

REGION_WIDTH = 200
REGION_HEIGHT = 200

LIGHT_GREY = (140,140,140)
GREY = (130,130,130)

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)

RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)

BROWN = (  150,  75,   0)
PINK =  (  255,  125, 200)
CYAN =  (  0,   255, 255)

BACKGROUND = ( 255, 255, 220)


BLOCK_SIZE = 50

display_quantity = True
layout_elements = {}
layout_elements.update([("test",4)])
print(layout_elements)

# === CLASSES === (CamelCase names)

class Button():

    def __init__(self,size,pos,default_color,pressed_color):

        self.image_normal = pygame.Surface(size)
        self.image_normal.fill(default_color)

        self.image_pressed = pygame.Surface(size)
        self.image_pressed.fill(pressed_color)

        self.image = self.image_normal
        
        self.rect = self.image.get_rect(center=pos)
        #self.rect.center = screen_rect.center

        self.clicked = False

    def update(self):
        global display_quantity

        if self.clicked:
            self.image = self.image_normal
            display_quantity = True
        else:
            self.image = self.image_pressed
            display_quantity = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = not self.clicked
            #if self.rect.collidepoint(event.pos)
            #    self.hovered = True
            #else:
            #    self.hovered = False
        
            # self.hovered = self.rect.collidepoint(event.pos)

class Machine(pygame.sprite.Sprite):
    def __init__(self,pos,item):
        super(Machine,self).__init__()
        self.id = 0

        self.sur = pygame.Surface((50,50))
        self.color = BLACK

        self.update_color(item[0].capitalize())
        
        self.sur.fill(self.color)

        self.setup_time = item[2]
        self.status_idle = True
        self.status_setup = False
        self.status_running = False

        self.utilization = 0.0   #keep track of utilization
        self.total_runtime = 0
        self.total_setuptime = 0

        self.rect = self.sur.get_rect(center=pos)

        # self.hovered = False
        self.clicked = False

    def update_color(self , clr):
        if clr == "Blue":
            self.color = BLUE
        elif clr.capitalize() == "Red":
            self.color = RED
        elif clr.capitalize() == "Cyan":
            self.color = CYAN
        elif clr.capitalize() == "Pink":
            self.color = PINK
        elif clr.capitalize() == "Green":
            self.color = GREEN
        elif clr.capitalize() == "Brown":
            self.color = BROWN
        
    def draw(self, surface):
        surface.blit(self.sur, self.rect)

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


        self.workstations = []
        self.workstation_pos = []
        
        self.machine_list =[]

        self.links_list =[]

        self.update_machine_list()
        self.update_layout()
        self.update_links()
        
        self.close_file()
        

    def update_layout(self):
        for i in range(9):
            for j in range(8):
                if ( self.layout_sheet.cell_value(2+i, 1+j) != '' ):
                    self.workstations.append( self.layout_sheet.cell_value(2+i, 1+j).split(","))
                    self.workstation_pos.append((i,j))
  
        for i in range(8):
            if ( self.layout_sheet.cell_value(11,1+i) != '' ):
                self.raw_material.append(self.layout_sheet.cell_value(11, 1+i).split(","))
                self.raw_material_pos.append((11, 1+i))

            if ( self.layout_sheet.cell_value(1,1+i) != '' ):
                self.demand.append(self.layout_sheet.cell_value(1, 1+i).split(","))
                self.demand_pos.append((1, 1+i))

        # print (self.demand_pos)
        # print (int(self.demand[1][1])  + 3 )

        # print (self.raw_material_pos)
        # print (self.raw_material)
        # print (self.workstation_pos)
        
               

    def update_machine_list(self):
        for i in range(self.machine_list_sheet.nrows - 1):
            self.machine_list.append( [self.machine_list_sheet.cell_value(1+i, 0),
                                        self.machine_list_sheet.cell_value(1+i, 1),
                                        self.machine_list_sheet.cell_value(1+i, 2)] )
        # print (self.machine_list)
    
    # generate tuples of start point, end point

    def update_links(self):
        # print(self.workstations)
        for i in range(len(self.workstations)):
            for j in range (len(self.workstations[i][4].split("-"))):     #predecessor loop
                self.links_list.append( ( self.workstations[i][4].split('-')[j] , self.workstations[i][0]) )            
            for k in range(len(self.workstations[i][5].split("-"))):   #successor loop
                self.links_list.append( (self.workstations[i][0] , self.workstations[i][5].split('-')[k] ))


        # print (self.links_list)


    def close_file(self):
        self.wb.release_resources()
        del self.wb

class Text():
    def __init__(self,text,pos,size,bg=BACKGROUND):
        self.font = pygame.font.Font('freesansbold.ttf', size) 
        self.text = self.font.render(text, True, BLACK,bg) 
        self.rect = self.text.get_rect()  
        # set the center of the rectangular object. 
        self.rect.center = pos 

    def draw(self, surface):
        surface.blit(self.text, self.rect)

    def update(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
    
    def __del__(self):
        pass 

class Account():
    def __init__(self):
        self.balance = 0

    def add(amt):
        self.balance += amt
        return True

    def buy(amt):
        if self.balance >= amt:
            self.balance -= amt
            return True
        else:
            return False

pwbr_power = 0
pwbr_duration = 0
pwbr_scrn_refresh = 0
pwbr_elps_time = 0
pwbr_ttl_sec = 0


class Popup(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createwidgets()
    # __init__() ---------------------------------------------------------------
 
    def createwidgets(self):
        """
        Creates the numerous widgets that make up the form.
        """
         
        global pwbr_power, pwbr_duration, pwbr_scrn_refresh, pwbr_elps_time
        global pwbr_ttl_sec
         
        pwbr_power += 1
        pwbr_duration += 0.15
        pwbr_elps_time += pwbr_duration
        pwbr_scrn_refresh = 0.333
        pwbr_ttl_sec += pwbr_elps_time
 
        if pwbr_elps_time > pwbr_scrn_refresh:
            pwbr_elps_time = 0
            pwbr_duration = 0
 
        caption_pwr = "Power: " + str(pwbr_power)
        caption_dur = "Duration: " + str(pwbr_duration)
        caption_rfrsh =  "Screen Refresh: " + str(pwbr_scrn_refresh)
        caption_etime = "Elapsed time: " + str(pwbr_elps_time)
        caption_ttl = "Total sec's: " + str(pwbr_ttl_sec)
         
        self.lblpower = tk.Label(self, text=caption_pwr, fg="black")
        self.lblduration = tk.Label(self, text=caption_dur, fg="black")
        self.lblrefreshrate = tk.Label(self, text=caption_rfrsh, fg="black")
        self.lbletime = tk.Label(self, text=caption_etime, fg="black")
        self.lbltotalsec = tk.Label(self, text=caption_ttl, fg="black")
         
        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
         
        self.lblpower.grid()
        self.lblduration.grid()
        self.lblrefreshrate.grid()
        self.lbletime.grid()
        self.lbltotalsec.grid()
        self.quitButton.grid()
        self.update()
         
class Demand():
    def __init__(self,item,pos):
        self.id = item[0]
        self.buffer = item[1]
        self.selling_price = item[2]

        self.sur = pygame.Surface((52, 32))
        self.sur.fill(BACKGROUND)

        pygame.draw.ellipse(self.sur,BLACK,(0,0,52,32))
        pygame.draw.ellipse(self.sur,WHITE,(1,1,50,30))
        
        self.pos =  (pos[1]*100 + 500 , 40  )

        layout_elements[self.id]=self.pos
        self.rect = self.sur.get_rect(center=self.pos)
        
        self.text = Text("0",(self.pos[0],self.pos[1]) ,16,WHITE)
        
    def update(self):
        global display_quantity
        #check state of mode and then pass approporitate value
        if display_quantity:
            self.text = Text(str(self.buffer),(self.pos[0],self.pos[1]) ,16,WHITE)
        else:
            self.text = Text("$ "+str(self.selling_price),(self.pos[0],self.pos[1] ) ,16,WHITE)    

        pass
        
    def draw(self, surface):
        surface.blit(self.sur, self.rect)
        self.text.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass

class Links():
    def __init__(self,item):
        global layout_elements
        self.sur = pygame.Surface((1, 1))
        self.sur.fill(BACKGROUND)

        pygame.draw.aaline(self.sur,BLACK, layout_elements[item[0]], layout_elements[item[1]] )
                
        self.rect = self.sur.get_rect(center=layout_elements[item[0]])
        # print(pos)

    def update(self):
        pass
        
    def draw(self, surface):
        surface.blit(self.sur, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # pop = rm_popup("rm")
            # pop.master.title("Power Bar")
            # pop.mainloop()
            pass

class RawMaterial():
    def __init__(self,item,pos):
        global layout_elements

        self.id = item[0]
        self.buffer = item[1]
        self.cost_price = item[2]

        self.sur = pygame.Surface((52, 32))
        self.sur.fill(BACKGROUND)
    
        pygame.draw.ellipse(self.sur,BLACK,(0,0,52,32))
        pygame.draw.ellipse(self.sur,WHITE,(1,1,50,30))
        
        self.pos = (pos[1]*100 + 500 , 750  )
        
        layout_elements[self.id]= self.pos


        self.rect = self.sur.get_rect(center=self.pos)
        
        self.text = Text("0",(self.pos[0],self.pos[1]) ,16,WHITE)

    def update(self):
        global display_quantity
        #check state of mode and then pass approporitate value
        if display_quantity:
            self.text = Text(str(self.buffer),(self.pos[0],self.pos[1]) ,16,WHITE)
        else:
            self.text = Text("$ "+str(self.cost_price),(self.pos[0],self.pos[1] ) ,16,WHITE)    

        
    def draw(self, surface):
        surface.blit(self.sur, self.rect)
        self.text.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # pop = rm_popup("rm")
            # pop.master.title("Power Bar")
            # pop.mainloop()
            pass

class Workstation():
    def __init__(self,item,pos):
        global layout_elements
        #what kind of machine
        self.id = item[0]
        self.predecessor = 0
        self.successor = 0
        self.color = BLACK
        self.update_color(item[1].capitalize())

        self.sur = pygame.Surface((52, 57))
        self.sur.fill(BACKGROUND)
                  
        pygame.draw.ellipse(self.sur,BLACK,(0,25,52,32))
        pygame.draw.ellipse(self.sur,self.color,(1,26,50,30))

        pygame.draw.rect(self.sur,BLACK,(0,0,50,25))
        pygame.draw.rect(self.sur,WHITE,(1,1,48,23)) 

        self.pos = (pos[1]*100 + 600 , 100 + (pos[0])*75)
        layout_elements[self.id]=self.pos
        
        self.buffer_text = Text("0",(self.pos[0],self.pos[1] - 15) ,16,WHITE)
        self.process_time_text = Text("0",(self.pos[0],self.pos[1] + 15),16,self.color)

        self.rect = self.sur.get_rect(center= self.pos )

        # add machine object --> need to check documentation
        
        self.buffer = item[3]
        self.process_time = item[2]
        self.utilization = 0.0   #keep track of utilization
        self.total_runtime = 0
        self.total_setuptime = 0
       

    def update_color(self , clr):
        if clr == "Blue":
            self.color = BLUE
        elif clr.capitalize() == "Red":
            self.color = RED
        elif clr.capitalize() == "Cyan":
            self.color = CYAN
        elif clr.capitalize() == "Pink":
            self.color = PINK
        elif clr.capitalize() == "Green":
            self.color = GREEN
        elif clr.capitalize() == "Brown":
            self.color = BROWN


    def update(self):
        self.buffer_text = Text(self.buffer,(self.pos[0],self.pos[1] - 15) ,16,WHITE)
        pass
        
    def draw(self, surface):
        surface.blit(self.sur, self.rect)
        self.buffer_text.draw(surface)
        self.process_time_text.draw(surface)
        

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # pop = rm_popup("rm")
            # pop.master.title("Power Bar")
            # pop.mainloop()
            pass
       
class Layout():
    def __init__(self):
        self.temp = 0
        self.elements = []
        self.links_list = ''
        self.grid()
        
    def grid(self):

        for i in range(9):
            txt = Text(str(9-i),(500,100 +i*75),16)
            self.elements.append(txt)
        
        #add labels
        self.elements.append( Text("RM",(500,775),16))
        self.elements.append( Text("Demand",(500,25),16))
               
        RM_list = ["A","B","C","D","E","F","G","H"]

        for i in range(8):
            txt = Text(RM_list[i],(500 + 100 + i*100 ,775),16)
            self.elements.append(txt)

        config = Config("Config.xlsx")
                                                
        # add raw material row
        for item in range(len(config.raw_material)):
            rm = RawMaterial(config.raw_material[item],config.raw_material_pos[item])
            self.elements.append(rm)

        #add demand row
        for item in range(len(config.demand)):
            dmd = Demand(config.demand[item],config.demand_pos[item])
            self.elements.append(dmd)

        #add workstations
        for item in range(len(config.workstations)):
            ws = Workstation(config.workstations[item],config.workstation_pos[item])
            self.elements.append(ws)

        #other buttons
        btn = Button((80,30),(60, 30),GREY,LIGHT_GREY)
        btn_text = Text("Toggle",(60,30) ,16, GREY)

        self.elements.append(btn)
        self.elements.append(btn_text)
        
        setup_text = Text("Setup",(150,30) ,16)
        self.elements.append(setup_text)
        
        # add machines in the left pane

        for item in range(len(config.machine_list)):
            for no in range(int(config.machine_list[item][1])):
                machine = Machine( (40 + 150 + no*70 , 80 + item*75 )  ,config.machine_list[item])
                self.elements.append(machine)
                txt = Text(str(int(config.machine_list[item][2])),(150,80 + item*75) ,16)
                self.elements.append( txt )


        self.links_list = config.links_list




class App():
    def __init__(self):

        pygame.init()
        pygame.display.set_caption('Goldratt Simulator') 
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.screen_rect = self.screen.get_rect()

        self.clock = pygame.time.Clock()
        self.is_running = False

        self.widgets = []
        self.list = ''

        self.create_objects()
        

    def quit(self):
        pygame.quit()

    def create_objects(self):
        global layout_elements
        # self.widgets.append(layout.elements[1])
        
        layout_elements = {}
        layout = Layout() 
        
        self.list = layout.links_list

        for ele in layout.elements:
            self.widgets.append(ele)
        # print (layout_elements)
    

    def handle_event(self, event):
        for widget in self.widgets:
            widget.handle_event(event)

    def update(self):
        # self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.RESIZABLE)
        for widget in self.widgets:
            widget.update()


    def draw(self, surface):

        # lines = Lines()
        for i in range(len(self.list)):
            pygame.draw.aaline(surface,BLACK, layout_elements[ self.list[i][0] ], layout_elements[  self.list[i][1] ] )

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

            # a = pygame.display.get_window_size()

            # print (a)

        self.quit()


if __name__ == '__main__':
        
    App().mainloop()