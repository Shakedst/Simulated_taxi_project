from Tkinter import *
import os
from openpyxl import *
import string
from Pathfinding import find_path
import time
import thread

#Time runs in a factor of speedup for instance: if speedup=10, things happen 10 times more quickly
speedup = 60.0

class Taxi:
    def __init__(self):
        self.status = 'available'
        self.battery = 100 #percentage
        self.x = 15
        self.y = 3
        self.path = None
        self.prev = None
    
    def move_to(self, destination):
        if (self.x,self.y) == destination:
            self.path = None
            self.status = 'available'
            return
        if not self.path:
            flipped_buildings = [(b[1],b[0]) for b in buildings]
            self.path = find_path((self.x,self.y),destination, disallowed = flipped_buildings, h=canvas_h, w=canvas_w)
        print len(self.path)
        if destination!=(15,10):
            self.status = 'on the way'
        while self.path:
            self.prev = (self.x,self.y)
            self.x,self.y = self.path[0]
            del self.path[0]
            self.battery-=1/3.0
            time.sleep(30.0/speedup)
        if self.battery <= 20.0:
            self.go_charge()
        self.status = 'available'
    
    def go_charge(self):
        self.status = 'charging'
        self.move_to((15,10)) 
        self.status = 'charging'
        time.sleep(15*60.0/speedup)
        self.battery = 100


my_map = [['.' for x in range(30)] for y in range(20)]
map_squares = [['.' for x in range(30)] for y in range(20)]
taxies = []

root = Tk()
map_frame = Frame(root)
canvas_w = 600
canvas_h = 400
map_canvas = Canvas(map_frame,width=canvas_w,height=canvas_h)
rect_w = canvas_w/30.0
rect_h = canvas_h/20.0

#Creating a canvas with 30x20 squares, can access each square with canvas[x][y]
for col in range(20):
    for row in range(30):
        map_squares[col][row] = map_canvas.create_rectangle(rect_w*row,rect_h*col,(row+1)*rect_w,(col+1)*rect_h,fill='white')

#map_canvas.create_rectangle(0,0,rect_w,-rect_h,fill='black')
map_canvas.pack()
map_frame.pack()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

buildings = []
#Read the excel file with the map to import all buildings
cols = list(string.uppercase)+['AA','AB','AC','AD']
wb = load_workbook(filename = 'map_excel.xlsx')
ws = wb.active
for row in range(1,21):
    for col in cols:
        if ws[col+str(row)].fill.fgColor.rgb!='00000000':
            if col in ['AA','AB','AC','AD']:
                col = 1+ord('Z')-ord('A')+ord(col[1])-ord('A')
            else:
                col = ord(col)-ord('A')
            col2 = 30-col #number of columns minus the columns, table got flipped
            buildings.append((row-1,col2-1))
            try:
                my_map[row-1][col2-1] = 'building'
                map_canvas.itemconfig(map_squares[row-1][col2-1],fill= 'blue')
            except:
                print 'Error',row-1,col,col2

my_map[10][15] = 'charging station'
map_canvas.itemconfig(map_squares[11][15],fill= 'white') #Bug from excel, charging station misplaced
map_canvas.itemconfig(map_squares[10][15],fill= 'yellow')

print buildings
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

default_map = my_map[:]

state_colors = {'available' : 'green',
                'charging' : 'orange',
                'disabled' : 'red',
                'on the way' : 'cyan',
}

def update_map():
    while True:
        for i,taxi in enumerate(taxies): 
            if taxi.prev:               
                if my_map[taxi.prev[1]][taxi.prev[0]] == 'charging station':
                    map_canvas.itemconfig(map_squares[taxi.prev[1]][taxi.prev[0]],fill= 'yellow')
                else:
                    map_canvas.itemconfig(map_squares[taxi.prev[1]][taxi.prev[0]],fill= 'white')
                map_canvas.delete('taxi'+str(i))
            print taxi.status
            my_map[taxi.y][taxi.x] = 'taxi '+ taxi.status
            map_canvas.itemconfig(map_squares[taxi.y][taxi.x],fill= state_colors[taxi.status])
            map_canvas.create_text((taxi.x+0.5)*rect_w,(taxi.y+0.5)*rect_h,text=i+1,tags='taxi'+str(i))
            print taxi.battery
        time.sleep(0.5)
        
taxies.append(Taxi())

def move_taxi0_text_lmao():
    taxies[0].move_to((0,19))


thread.start_new_thread(move_taxi0_text_lmao,())
thread.start_new_thread(update_map,())
mainloop()