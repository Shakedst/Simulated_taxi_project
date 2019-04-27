from Tkinter import *
import socket
import pickle
import thread
import time
from Taxi import Taxi

map_squares = [['.' for x in range(30)] for y in range(20)]
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

map_canvas.pack()
map_frame.pack(side = LEFT)

state_colors = {'available' : 'green',
                'charging' : 'orange',
                'disabled' : 'red',
                'on the way' : 'cyan',
}

def update_map(buildings,taxies):
    flipped_buildings = [(b[1],b[0]) for b in buildings]
    for i,taxi in enumerate(taxies): 
        if taxi.prev:               
            if (taxi.prev[1],taxi.prev[0]) == (10,15):
                map_canvas.itemconfig(map_squares[taxi.prev[1]][taxi.prev[0]],fill= 'yellow')
            elif taxi.prev in flipped_buildings:
                map_canvas.itemconfig(map_squares[taxi.prev[1]][taxi.prev[0]],fill= 'blue')
            elif not any((taxi2.x,taxi2.y)==taxi.prev for taxi2 in taxies):
                map_canvas.itemconfig(map_squares[taxi.prev[1]][taxi.prev[0]],fill= 'white')
            map_canvas.delete('taxi'+str(taxi.taxi_id))
        map_canvas.itemconfig(map_squares[taxi.y][taxi.x],fill= state_colors[taxi.status])
        map_canvas.create_text((taxi.x+0.5)*rect_w,(taxi.y+0.5)*rect_h,text=taxi.taxi_id,tags='taxi'+str(taxi.taxi_id))

taxies_state_frame = Frame(root)
info = 'id: {}\nx: {}, y: {} \nbattery: {} \nstatus: {}'.format('','','','','')
#Label(taxies_state_frame, text=info, height=5, width=20, relief='solid').pack(side=TOP, fill="x")
total_info = 'Total available: \nTotal on the way: \nTotal charging: '
total = Label(taxies_state_frame, text=total_info, height=5, width=20, relief='solid')
total.pack(side=BOTTOM, fill="x")
taxies_state_frame.pack(side=RIGHT, expand="YES", fill="both")

def update_taxies_states(taxies,taxies_state_frame,total):
    taxies_labels = filter(lambda x:'Total' not in x['text'],taxies_state_frame.winfo_children())
    if len(taxies_labels) == len(taxies):
        for i,taxi in enumerate(taxies):
            info = 'id: {}\nx: {}, y: {} \nbattery: {:.2f} \nstatus: {}'.format(taxi.taxi_id, taxi.x, taxi.y, taxi.battery, taxi.status)
            taxies_labels[i]['text'] = info
    else:
        for i in range(len(taxies)-len(taxies_labels)):
            taxi = taxies[-1-i]
            info = 'id: {}\nx: {}, y: {} \nbattery: {:.2f} \nstatus: {}'.format(taxi.taxi_id, taxi.x, taxi.y, taxi.battery, taxi.status)
            Label(taxies_state_frame, text=info, height=5, width=20, relief='solid').pack(side=TOP, fill="x")
    info_dict = {'available':0, 'on the way':0, 'charging':0, 'disabled':0}
    for taxi in taxies:
        info_dict[taxi.status]+=1
    total_info = 'Total available: {0}\nTotal on the way: {1}\nTotal charging: {2}\nTotal disabled: {3}'.format(*info_dict.values())
    total['text'] = total_info
    
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
HOST = '192.168.1.19'
PORT = 52317
BUFFSIZE = 1024*5
ADDR = (HOST,PORT)
clientsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsock.connect(ADDR)

def server_stuff():
    clientsock.send('Admin')
    buildings_string = clientsock.recv(BUFFSIZE)
    buildings = pickle.loads(buildings_string)
    for b in buildings:
        row,col = b[0],b[1]
        map_canvas.itemconfig(map_squares[row][col],fill= 'blue')
    map_canvas.itemconfig(map_squares[10][15],fill= 'yellow')
    while True:
        data = clientsock.recv(BUFFSIZE)
        try:
            #TODO - Understand why this shit sometimes doesnt work
            taxies_string, requests_string = data.split(',,,,,')
        except:
            print data
            continue
        #taxies_string = clientsock.recv(BUFFSIZE)
        taxies = pickle.loads(str(taxies_string))
        requests = pickle.loads(str(requests_string))
        for taxi in taxies:
            print 'ID',taxi.taxi_id,'x:',taxi.x,'y:',taxi.y,'prev:',taxi.prev,'status:',taxi.status
        print
        if requests:
            #TODO - Recolor buildings who dont have a client waiting anymore
            for req in requests:
                map_canvas.itemconfig(map_squares[req[1][1]][req[1][0]],fill = 'IndianRed1')
        update_taxies_states(taxies,taxies_state_frame,total)
        update_map(buildings, taxies)
            

thread.start_new_thread(server_stuff,())
root.mainloop()