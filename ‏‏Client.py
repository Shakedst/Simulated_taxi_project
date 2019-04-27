import socket
from Tkinter import *
import tkMessageBox
from Taxi import *
import pickle
import thread
import time
from Queue import Queue
import traceback

q = Queue()

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
    print 'Start:',start,'End:',end

global prev2
prev2 = None

def update_map(x,y,prev,taxi_id):
    global prev2
    flipped_buildings = [(b[1],b[0]) for b in buildings]
    print prev2
    if prev2:      
        if prev2 not in flipped_buildings:
            map_canvas.itemconfig(map_squares[prev2[1]][prev2[0]],fill= 'white')          
        map_canvas.delete('taxi')
    if (x,y) not in flipped_buildings:
        map_canvas.itemconfig(map_squares[y][x],fill='cyan')
        prev2 = (x,y)
    map_canvas.create_text((x+0.5)*rect_w,(y+0.5)*rect_h,text=taxi_id,tags='taxi')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HOST = '192.168.1.19'
PORT = 52317
BUFFSIZE = 1024
ADDR = (HOST,PORT)
clientsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsock.connect(ADDR)

global buildings
buildings = []
def server_stuff():
    global start,end,buildings
    clientsock.send('Client')
    buildings_string = clientsock.recv(BUFFSIZE)
    buildings = pickle.loads(buildings_string)
    for b in buildings:
        row,col = b[0],b[1]
        w = Button(relief='raised',bd=1,bg='blue',command=lambda x=b[1],y=b[0]:select_builidings(x,y))
        map_canvas.create_window(rect_w*(col+0.5),rect_h*(row+0.5), height=rect_h, width=rect_w, \
          window = w, tag = 'building')
    return

def delete_buildings():
    global buildings
    send_button['state'] = 'disabled'
    q.put((map_canvas.delete, ('building',), {} ))
    for location in buildings:
        print location
        try:
            if (location[1],location[0]) == start:
                map_canvas.itemconfig(map_squares[location[0]][location[1]],fill= 'green')
            elif (location[1],location[0]) == end:
                map_canvas.itemconfig(map_squares[location[0]][location[1]],fill= 'red')
            else:
                map_canvas.itemconfig(map_squares[location[0]][location[1]],fill= 'blue')
        except:
            print traceback.format_exc()

def send_request2():
    global start,end
    has_arrived = False
    if end == (-1,-1):
        q.put (( tkMessageBox.showerror, ('Select locations','You need to select starting location and destination before sending the request'), {} ))
        return
    else:
        top_label['text'] = 'Request sent.'
        print top_label['text']
        locations = (start,end)
        locations_string = pickle.dumps(locations)
        clientsock.send('Request:'+locations_string)
        delete_buildings()
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
    thread.start_new_thread(send_request2,())

def tkloop():
    try:
        while True:
            f, a, k = q.get_nowait()
            f(*a, **k)
    except:
        pass
    root.after(100, tkloop)

bottom_frame = Frame(root)
send_button = Button(bottom_frame, text='Send request', bg='green', height=2, width=15, command = send_request)
send_button.pack(fill='y')
bottom_frame.pack(side = BOTTOM, fill='both', expand='yes')

thread.start_new_thread(server_stuff,())
tkloop()
root.mainloop()
