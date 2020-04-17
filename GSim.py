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

FRAME_RATE = 60
SIM_SPEEED = 0  # 0-30
TICKS = int(0)     #increment this whenever the simulation is running, gives second, use it to calculate the day of the week and the time.
SIM_RUN = False    # use this for start and freeze sim


SCREEN_WIDTH = 1388
SCREEN_HEIGHT = 800

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

BACKGROUND = ( 255, 255, 230)



display_quantity = True
layout_elements = {}


workstation_objects = []
all_objects = [] #list of all workstations, demand and raw materials
machines =[]    # list of all machine objects

RM_list = ["A","B","C","D","E","F","G","H"]

# print(layout_elements)


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
        if self.clicked:
            self.image = self.image_normal
        else:
            self.image = self.image_pressed

        self.special_operation()
        
    def special_operation(self):
        pass 

        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def handle_event(self, event):
        pass


class Toggle_button(Button):

    def special_operation(self):
        global display_quantity
        display_quantity = self.clicked
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = not self.clicked

class Inc_spd_button(Button):

    def special_operation(self):
        global SIM_SPEEED
        if self.clicked and SIM_SPEEED < 31:
            SIM_SPEEED += 3

        # print(SIM_SPEEED)
        self.clicked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True

class Dec_spd_button(Button):

    def special_operation(self):
        global SIM_SPEEED
        if self.clicked and SIM_SPEEED > 1:
            SIM_SPEEED -= 3

        # print(SIM_SPEEED)
        self.clicked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True



class Sim_control():
    def __init__(self,size,pos,run_color,stopped_color):
        self.run_color = run_color
        self.stopped_color = stopped_color
        self.color = self.stopped_color

        self.pos = pos
        self.sur = pygame.Surface(size)
        self.sur.fill(self.color)

        self.rect = self.sur.get_rect(center=pos)

        self.status = "STOPPED"

        # self.PACE_text = Text(self.grid_loc,(100,100) ,20,WHITE)
        self.status_text = Text(self.status,(100,100),20,WHITE)
        # self.hovered = False
        self.clicked = False

    def update(self):
        global SIM_RUN

        if self.clicked:
            self.status = "RUNNING"
            self.color = self.run_color
            SIM_RUN = True

        else:
            self.status = "STOPPED"
            self.color = self.stopped_color
            SIM_RUN = False

        self.sur.fill(self.color)
        # self.gird_loc_text = Text(self.grid_loc,(self.pos[0],self.pos[1] - 5) ,16,self.color)
        self.status_text = Text(self.status,(self.pos[0],self.pos[1]),26,self.color)
        
    def draw(self, surface):
        surface.blit(self.sur, self.rect)
        # self.gird_loc_text.draw(surface)
        self.status_text.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = not self.clicked
       
class Display_time(Button):
    def __init__(self,size,pos):

        self.pos = pos

        self.sur = pygame.Surface(size)
        self.sur.fill(LIGHT_GREY)

        self.rect = self.sur.get_rect(center=pos)

        self.day = 1
        self.time = "0 : 00"
        self.day_text = Text("Day : " + str(self.day) ,(100,25),20,WHITE)
        self.time_text = Text(self.time,(100,75),20,WHITE)

    def update(self):
        self.compute_time()
        self.day_text = Text("Day : " + str(self.day),  (self.pos[0],self.pos[1]-20) ,18,LIGHT_GREY)
        self.time_text = Text(self.time,(self.pos[0],self.pos[1] + 20),18,LIGHT_GREY)
        
    def draw(self, surface):
        # print("Draw function called?")
        surface.blit(self.sur, self.rect)
        self.day_text.draw(surface)
        self.time_text.draw(surface)

    def compute_time(self):
        global TICKS
        # print("Tick" , TICKS)
        a = TICKS
        self.time = ""
        self.day =  int( a / (8*60))
        a = a%(8*60)
        self.time = self.time + str( int(a/60)) + " : " +  str( int(a%60))
        


class Machine():
    def __init__(self,pos,item):
        # super(Machine,self).__init__()
        self.id = item[0]   #check if this is required

        self.sur = pygame.Surface((50,50))
        self.color = BLACK
        self.update_color(item[0].capitalize())
        self.sur.fill(self.color)

        self.workstation = None
        
        self.setup_time = int(item[2])
        self.status_idle = True
        self.status_setup = False
        self.status_setup_over = False
        self.status_running = False

        self.utilization = 0.0   #keep track of utilization

        self.runtime =  0     #track time since start of run
        self.setuptime = 0     # track time since start of setup

        self.total_runtime = 0
        self.total_setuptime = 0

        self.rect = self.sur.get_rect(center=pos)
        
        self.pane_pos = pos
        self.pos = self.pane_pos

        self.grid_loc = "--"
        self.status = "Idle"
        self.gird_loc_text = Text(self.grid_loc,(self.pos[0],self.pos[1] - 5) ,16,self.color)
        self.status_text = Text(self.status,(self.pos[0],self.pos[1] + 10),14,self.color)


        # self.hovered = False
        self.clicked = False

    def update_color(self , clr):
        if clr.capitalize() == "Blue":
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
        
        if self.clicked:
            self.sur.fill(LIGHT_GREY)
        else:
            self.sur.fill(self.color)

        if self.status_idle:
            self.status ="Idle"
        if self.status_running:
            self.status = "Run"
        if self.status_setup_over:
            self.status = "Hold"     
        if self.status_setup:
            self.status = "Setup"
            
        
        self.gird_loc_text = Text(self.grid_loc,(self.pos[0],self.pos[1] - 5) ,16,self.color)
        self.status_text = Text(self.status,(self.pos[0],self.pos[1] + 10),14,self.color)
        
    def draw(self, surface):
        surface.blit(self.sur, self.rect)
        self.gird_loc_text.draw(surface)
        self.status_text.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True

        if self.clicked:

            if event.type == pygame.MOUSEBUTTONUP:
                self.clicked = False
                self.pos = self.pane_pos
                self.add_machine_to_ws(event.pos)  #add machine to workstation
                # print(event.pos,"next line")

            if event.type == pygame.MOUSEMOTION:        
                self.pos = event.pos
    
    def set_status(self):
        # print("inside set_status")
        self.update_timer()
        # print(self.setuptime , self.runtime)
        if self.status_setup and  self.setuptime >= self.setup_time :
            set_mc_status_setup_over(self)
            # set_mc_status_running(self)
        if self.workstation != None:
            if self.status_running and self.runtime >= self.workstation.run_time:
                self.workstation.buffer +=1  #add function to update the next

                set_mc_status_setup_over(self)


    def update_timer(self):        
        if self.status_setup:
            self.setuptime += 1
            self.runtime = 0
        if self.status_running:
            self.setuptime = 0
            self.runtime += 1
        if self.status_idle or self.status_setup_over:
            self.setuptime = 0
            self.runtime =0  

    def add_machine_to_ws(self,pos):
        global workstation_objects
        for item in workstation_objects:
            if (pos[0] > item.rect.left) and (pos[0] < item.rect.right) and (pos[1] > item.rect.top) and (pos[1] < item.rect.bottom):
                # print("inside",pos)
                self.check_machine_add(item)
                break

    def check_machine_add(self,ws):
        if self.color == ws.color:
            # if current status is running, convert
            if not self in ws.machines:
                if (self.workstation != ws and self.workstation != None):
                    if self.status_running:
                        self.workstation.prev[0].buffer +=1
                    self.workstation.machines.remove(self)
                    # print("Machine removed form original ws")
                    

                self.workstation = ws

                ws.machines.append(self)
                self.grid_loc = ws.grid_loc
                set_mc_status_setup(self)


                print(ws.grid_loc)
                # print("Machine added")

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

        print(self.workstations)
        # print (self.links_list)


    def close_file(self):
        self.wb.release_resources()
        del self.wb

class Text():
    def __init__(self,text,pos,size,bg=BACKGROUND):
        self.font = pygame.font.SysFont('calibri', size) 
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
        # tk.Frame.__init__(self, master)
        # self.grid()
        # self.createwidgets()
    # __init__() ---------------------------------------------------------------
        pass

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
        self.prev = []
        
        self.buffer = int(item[1])
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
    
    def set_status(self):
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
        self.next = []
        self.id = item[0]
        self.buffer = int(item[1])
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
    
    def set_status(self):
        pass
        
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
        global RM_list
        self.details = item
        #what kind of machine
        self.id = item[0]
        self.next = []
        self.prev = []
        self.color = BLACK
        self.update_color(item[1].capitalize())
        self.run_time = int(item[2])
        self.grid_loc = RM_list[pos[1]] + str(9 - pos[0])
        
        self.status_no_machine = True
        self.status_not_running = False
        self.status_running = False

        # print(self.grid_loc)

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
        
        self.buffer = int(item[3])
        self.under_process = 0
        self.machines = []
        self.produced = 0
        self.prod_limit = 9999

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
        self.set_ws_status()
        
        pygame.draw.ellipse(self.sur,BLACK,(0,25,52,32))
        pygame.draw.ellipse(self.sur,self.color,(1,26,50,30)) 

        self.buffer_text = Text( str(self.buffer),(self.pos[0],self.pos[1] - 15) ,16,WHITE)
        if self.status_running:
            pygame.draw.line(self.sur,BLACK,(22,27),(49,44))
            pygame.draw.line(self.sur,BLACK,(8,31),(42,52))
            pygame.draw.line(self.sur,BLACK,(1,40),(29,56))
            pygame.draw.line(self.sur,BLACK,(29,27),(2,44))
            pygame.draw.line(self.sur,BLACK,(43,31),(8,52))
            pygame.draw.line(self.sur,BLACK,(49,40),(21,55))
            self.process_time_text = Text(str(self.run_time),(self.pos[0],self.pos[1] + 15),16,self.color)
        elif self.status_no_machine:
            self.process_time_text = Text(str(self.run_time),(self.pos[0],self.pos[1] + 15),16,self.color)
        elif self.status_not_running:
            self.process_time_text = Text("+"+str(self.run_time),(self.pos[0],self.pos[1] + 15),16,self.color)


    def set_status(self):
        self.update_mc_ws_status()          

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

    def set_ws_status(self):
        if len(self.machines)>0:   #atleast 1 machine added to workstation
            running = False
            for mc in self.machines:
                if mc.status_running:
                    running = True
                    break
            if running:
                self.set_ws_running()
            else:
                self.set_ws_not_running()
        else:
            self.set_ws_no_machine()

    def update_mc_ws_status(self):
        # if sufficient buffer in the dependecies and under limit
            # start production
        if len(self.machines)>0:   #atleast 1 machine added to workstation    
            if self.produced <= self.prod_limit:  # check for production limit
                for mc in self.machines:
                    # print(mc.id,mc.status_idle,mc.status_setup,mc.status_setup_over,mc.status_running)
                    if mc.status_setup_over and self.check_up_buffer():
                        set_mc_status_running(mc)
                        self.update_up_buffer()
                        # print(self.id, self.prev[0].id)
                    # print(mc.id,mc.status_idle,mc.status_setup,mc.status_setup_over,mc.status_running)
            else:
                for mc in self.machines:
                    set_mc_status_setup_over(mc)

     
    # check for items in the upstream buffers
    def check_up_buffer(self):
        buffer = True
        for ws in self.prev:
            if ws.buffer < 1:
                buffer  = False      
        return buffer

    def update_up_buffer(self):
        print (self.prev)
        for ws in self.prev:
            ws.buffer -= 1

        # self.under_process += 1 

    def set_machine_status(self):
        if self.status_idle:
            for mc in self.machines:
                self.set_mc_status_idle(mc)
        elif self.status_setup:
            for mc in self.machines:
                self.set_mc_status_setup(mc)
                #reduce the buffers
                self.update_up_buffer()
        elif self.status_running:
            for mc in self.machines:
                self.set_mc_status_running(mc)
                
    def set_ws_no_machine(self):
        self.status_no_machine = True
        self.status_not_running = False
        self.status_running = False

    def set_ws_not_running(self):
        self.status_no_machine = False
        self.status_not_running = True
        self.status_running = False

    def set_ws_running(self):
        self.status_no_machine = False
        self.status_not_running = False
        self.status_running = True

class Layout():
    def __init__(self):
        self.temp = 0
        self.elements = []
        self.links_list = ''
        self.grid()
        
    def grid(self):
        global RM_list
        global workstation_objects
        global all_objects
        global machines

        config = Config("Config.xlsx")
        self.add_machine_pane(config)
        self.add_factory(config)
        self.interface_buttons()
        self.time_accounts()
    
    def update(self):
        # self.interface_buttons()
        pass

    def interface_buttons(self):
        
        btn = Toggle_button((80,30),(75, 30),GREY,LIGHT_GREY)    #Toggle buttons
        btn_text = Text("Toggle",(75,30) ,16, LIGHT_GREY)
        self.elements.append(btn)
        self.elements.append(btn_text)

        inc_spd_btn = Inc_spd_button((30,30),(110, 325),GREY,LIGHT_GREY)    #sim speed inc buttons
        inc_spd_text = Text("+",(110,325) ,24, LIGHT_GREY)
        self.elements.append(inc_spd_btn)
        self.elements.append(inc_spd_text)
        
        dec_spd_btn = Dec_spd_button((30,30),(40, 325),GREY,LIGHT_GREY)    #sim speed dec buttons
        dec_spd_text = Text("-",(40,325) ,24, LIGHT_GREY)
        self.elements.append(dec_spd_btn)
        self.elements.append(dec_spd_text)
     
        main_control = Sim_control((120,80),(75,400),GREEN,RED)
        self.elements.append(main_control)

        # main_control2 = Sim_control((120,80),(75,600),GREEN,RED)
        # self.elements.append(main_control2)

    def time_accounts(self):
        main_control1 = Display_time((120,80),(75,500))
        self.elements.append(main_control1)
        pass

    def add_factory(self,config):
                #add labels
        self.elements.append( Text("RM",(500,775),16))
        self.elements.append( Text("Demand",(500,25),16))

            # add raw material row
        for item in range(len(config.raw_material)):
            rm = RawMaterial(config.raw_material[item],config.raw_material_pos[item])
            self.elements.append(rm)
            all_objects.append(rm)

        #add demand row
        for item in range(len(config.demand)):
            dmd = Demand(config.demand[item],config.demand_pos[item])
            self.elements.append(dmd)
            all_objects.append(dmd)

        #add workstations
        for item in range(len(config.workstations)):
            ws = Workstation(config.workstations[item],config.workstation_pos[item])
            self.elements.append(ws)
            workstation_objects.append(ws)
            all_objects.append(ws)
    
    def add_machine_pane(self,config):
        for i in range(9):
            txt = Text(str(9-i),(500,100 +i*75),16)
            self.elements.append(txt)
               
        for i in range(8):
            txt = Text(RM_list[i],(500 + 100 + i*100 ,775),16)
            self.elements.append(txt)    
        
        setup_text = Text("Setup",(150,30) ,16)
        self.elements.append(setup_text)

        # add machines in the left pane
        for item in range(len(config.machine_list)):
            for no in range(int(config.machine_list[item][1])):
                machine = Machine( (40 + 150 + no*70 , 80 + item*75 )  ,config.machine_list[item])
                self.elements.append(machine)
                machines.append(machine)
                txt = Text(str(int(config.machine_list[item][2])),(150,80 + item*75) ,16)
                self.elements.append( txt )


        self.links_list = config.links_list

    def draw(self, surface):
        pass

    def handle_event(self, event):
        pass

def set_mc_status_idle(mc):
    mc.status_idle = True
    mc.status_running = False
    mc.status_setup = False
    mc.status_setup_over = False
    mc.update_timer()
    
def set_mc_status_setup(mc):
    mc.status_idle = False
    mc.status_running = False
    mc.status_setup = True
    mc.status_setup_over = False
    mc.update_timer()

def set_mc_status_setup_over(mc):
    mc.status_idle = False
    mc.status_running = False
    mc.status_setup = False
    mc.status_setup_over = True
    mc.update_timer()

def set_mc_status_running(mc):
    mc.status_idle = False
    mc.status_running = True
    mc.status_setup = False
    mc.status_setup_over = False
    mc.update_timer()

class App():
    def __init__(self):

        pygame.init()
        pygame.display.set_caption('Goldratt Simulator') 
        # pygame.freetype.set_default_resolution(30)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.screen_rect = self.screen.get_rect()

        self.clock = pygame.time.Clock()
        self.is_running = False

        self.widgets = []
        self.list = ''

        self.create_objects()

        self.loopno = 0
        

    def quit(self):
        pygame.quit()

    def create_objects(self):
        global layout_elements
        global workstation_objects
        global all_objects
        # self.widgets.append(layout.elements[1])
        
        layout_elements = {}
        layout = Layout() 
        
        self.widgets.append(layout)

        self.list = layout.links_list

        for ele in layout.elements:
            self.widgets.append(ele)
    
        # update downstream(successor) and upsteam(predecessor)
        for item in workstation_objects:
            for xws in all_objects:
                for ws in item.details[4].split("-"):
                    # print("upstream loop")
                    # print (ws, xws.id)
                    if str(ws) == str(xws.id):
                        if item not in xws.next:
                            xws.next.append(item)
                        if xws not in item.prev:
                            item.prev.append(xws)
                        # print("some operaiton")
                for ws in item.details[5].split("-"):
                    # print("downsteam loop")
                    if str(ws) == str(xws.id):
                        if xws not in item.next:
                            item.next.append(xws)
                        if item not in xws.prev:
                            xws.prev.append(item)
                        # print("some operaiton 3")
            
            # print(item.next[0].buffer)


    def handle_event(self, event):
        for widget in self.widgets:
            widget.handle_event(event)

    def update(self):
        global all_objects
        global machines
        global SIM_RUN
       
        # self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.RESIZABLE)
        for widget in self.widgets:
            widget.update()

        if SIM_RUN:
            self.update_statuses()
            
     
    
    def update_statuses(self):
        global TICKS

        self.loopno += 1
        

        if self.loopno >= int(FRAME_RATE / ( 1 + SIM_SPEEED)):
            TICKS += 1
            self.loopno = 0
            for ele in all_objects:
                ele.set_status()
            for mc in machines:
                mc.set_status()
                # print("tick")



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

            self.update()

            # --- draws ---

            self.screen.fill(BACKGROUND)

            self.draw(self.screen)

            pygame.display.update()

            self.clock.tick(FRAME_RATE)   #FPS

            # a = pygame.display.get_window_size()

            # print (a)

            # print("tick")

        self.quit()


if __name__ == '__main__':
        
    App().mainloop()