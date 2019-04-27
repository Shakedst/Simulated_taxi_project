import socket
from Tkinter import *
import tkMessageBox
from Taxi import *
import pickle
import thread
import time

root = Tk()

global start,end
start = (-1,-1)
end = (-1,-1)
top_label = Label(root,text='Press the starting location from the blue squares on the map',font='Helvetica 16')
top_label.pack(side=TOP)

map_squares = [['.' for x in range(30)] for y in range(20)]
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
map_frame.pack(side = TOP)

def select_builidings(x,y):
    global start,end
    if start == (-1,-1):
        start = (x,y)
        top_label['text'] = 'Press the wanted destination'
    elif end == (-1,-1):
        end = (x,y)
        top_label['text'] = 'Press the send button to send the request'
    else:
        result = tkMessageBox.askquestion('Change destination','Do you want to change your destination to (%i,%i)' %(x,y))
        if result == 'yes':
            end = (x,y)
    print start,end

def update_map(x,y,prev,taxi_id):
    if prev:               
        if (x,y)!=prev:
            map_canvas.itemconfig(map_squares[prev[1]][prev[0]],fill= 'white')
        map_canvas.delete('taxi')
    map_canvas.itemconfig(map_squares[y][x],fill='cyan')
    map_canvas.create_text((x+0.5)*rect_w,(y+0.5)*rect_h,text=taxi_id,tags='taxi')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HOST = '192.168.1.18'
PORT = 52317
BUFFSIZE = 1024
ADDR = (HOST,PORT)
clientsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsock.connect(ADDR)

windows = {}
def server_stuff():
    global start,end
    clientsock.send('Client')
    buildings_string = clientsock.recv(BUFFSIZE)
    buildings = pickle.loads(buildings_string)
    for b in buildings:
        row,col = b[0],b[1]
        windows[b] = Button(relief='raised',bd=1,bg='blue',command=lambda x=b[1],y=b[0]:select_builidings(x,y))
        map_canvas.create_window(rect_w*(col+0.5),rect_h*(row+0.5), height=rect_h, width=rect_w, \
          window = windows[b], tag = 'building')
    return

def delete_buildings():
    #map_canvas.pack_forget()
    #map_canvas.delete('building')
    #top_label.pack_forget()
    for location in windows:
        print location, windows[location]
        #map_canvas.itemconfig(windows[location], state = HIDDEN)
        #map_canvas.destroy()
        '''
        if location == start:
            map_canvas.itemconfig(map_squares[location[1]][location[0]],fill= 'green')
        elif location == end:
            map_canvas.itemconfig(map_squares[location[1]][location[0]],fill= 'red')
        else:
            map_canvas.itemconfig(map_squares[location[1]][location[0]],fill= 'blue')
        '''


def send_request2():
    global start,end
    has_arrived = False
    if end == (-1,-1):
        tkMessageBox.showerror('You need to select starting location and destination before sending the request')
        root.update()
        return
    else:
        top_label['text'] = 'Request sent.'
        print top_label['text']
        locations = (start,end)
        locations_string = pickle.dumps(locations)
        clientsock.send('Request:'+locations_string)
        while True:
            data = clientsock.recv(BUFFSIZE)
            if data == 'No taxi available at the moment':
                top_label['text'] = data
                continue
            elif 'Your taxi:' in data:
                taxi_string = data.replace('Your taxi:','')
                x,y,length,prev,taxi_id = pickle.loads(taxi_string)
                if (x,y) == start:
                    has_arrived = True
                if length >= 1:
                    print x,y,length
                    taxi_time = length*30.0/speedup #In seconds
                    time_str = time.strftime('%H:%M:%S', time.gmtime(taxi_time))
                    if not has_arrived:
                        print 'Time until taxi arrival:',time_str
                        top_label['text'] = 'Time until taxi arrival: '+time_str
                    else:
                        print 'Time until arrival to destination:',time_str
                        top_label['text'] = 'Time until arrival to destination: '+time_str
                    update_map(x,y,prev,taxi_id)
            else:
                continue

def send_request():
    #Show error works here but doesn't work inside of the thread, need to fix inherent problems
    #tkMessageBox.showerror('Error','You need to select starting location and destination before sending the request')
    thread.start_new_thread(send_request2,())

bottom_frame = Frame(root)
send_button = Button(bottom_frame, text='Send request', bg='green', height=2, width=15, command = send_request)
send_button.pack(fill='y')
bottom_frame.pack(side = BOTTOM, fill='both', expand='yes')

thread.start_new_thread(server_stuff,())
root.mainloop()
