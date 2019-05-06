import os
from openpyxl import *
import string
from Pathfinding import find_path
import time
import thread
import socket
import pickle
from Taxi import *
from Request import *

#Time runs in a factor of speedup for instance: if speedup=10, things happen 10 times more quickly
#speedup is imported from Taxi.py

my_map = [['.' for x in range(30)] for y in range(20)]
taxies = []

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
            except:
                print 'Error',row-1,col,col2

def go_charge2(taxi):
    taxi.go_charge(flipped_buildings)

def move_to2(taxi,destination,dst2=None, req=None):
        taxi.move_to(destination, flipped_buildings)
        if dst2:
            if req:
                req.status = 'On the way to destination'
            taxi.move_to(dst2, flipped_buildings)
            if req:
                req.status = 'Done'
        if taxi.battery <= 20.0:
            taxi.go_charge(flipped_buildings)


my_map[10][15] = 'charging station'
buildings.remove((11,15))
my_map[11][15] = '.' #Wrong mark in excel
flipped_buildings = [(b[1],b[0]) for b in buildings]

def update_map():
    while True:
        for taxi in taxies: 
            my_map[taxi.y][taxi.x] = 'taxi '+ taxi.status
        time.sleep(0.1)

def calc_distance(pos1,pos2):
    return ((pos2[0]-pos1[0])**2+(pos2[1]-pos1[1])**2)**0.5

requests = []
handled_requests = []

def handle_requests():
    global clients
    while True:
        available_taxies = filter(lambda taxi:taxi.status=='available',taxies)
        if available_taxies:
            for i in range(len(available_taxies)):
                if requests:
                    request = requests.pop(0)
                    c_id, start, end = request.client_id, request.start, request.end
                    closest_taxi = min(available_taxies, key=lambda taxi:calc_distance((taxi.x,taxi.y),start))
                    thread.start_new_thread(move_to2,(closest_taxi, start, end, request))
                    closest_taxi.client = c_id
                    request.status = 'On the way to client'
                    request.taxi = closest_taxi
                    handled_requests.append(request)
                    print 'Sent taxi',taxies.index(closest_taxi),'to pick up from',start,'and go to',end
                    print requests
        if requests:
            for request in requests:
                request.status = 'Waiting for taxi'
                c_id = request.client_id
                print c_id, 'waiting for taxi'
                clients[c_id].send('No taxi available at the moment')
        time.sleep(0.5)
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Creating and binding the server
BUFFSIZE = 1024*5
HOST = '192.168.1.18'
PORT = 52317
ADDR = (HOST,PORT)
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
server.bind(ADDR) 
print 'server bound on:',ADDR

def wait_for_connection(server):
    server.listen(2)
    print 'waiting for connection...\n'
    clientsock,addr = server.accept()
    print 'connected from:',addr
    thread.start_new_thread(handler, (clientsock, addr))
    thread.start_new_thread(wait_for_connection, (server,))
    return

def handler(clientsock, addr):
    data = clientsock.recv(BUFFSIZE)    
    if data == 'Admin':
        thread.start_new_thread(admin_handler, (clientsock, addr))
    elif data == 'Client':
        thread.start_new_thread(client_handler, (clientsock, addr))
    else:
        print 'Unkown client type, closing connection'
        clientsock.close()
    return

taxies = [Taxi(20,7),Taxi(),Taxi(1,9)]

def move_taxi0_test_lmao():
    #print 'I told taxi0 to move to 0,19'
    move_to2(taxies[0], (0,19))
    #move_to2(taxies[0], (15,1))
 
def move_taxi1_test_lmao():
    #print 'I told taxi1 to move to 5,8'
    move_to2(taxies[1], (5,8))
 
def charge_taxi2_test_lmao():
    #print 'I told taxi2 to go charge'
    go_charge2(taxies[2])

def stop_test():
    time.sleep(10.0)
    print 'Told taxi0 to stop'
    taxies[0].stop()

global admins,admin_id
admins = {}
admin_id = 0
def admin_handler(clientsock, addr):
    global admins,admin_id
    admins[admin_id] = clientsock
    admin_id += 1
    buildings_string = pickle.dumps(buildings)
    clientsock.send(buildings_string)
    while True:
        data_dic = {'taxies': taxies, 'requests': requests, 'handled_requests': handled_requests}
        data = pickle.dumps(data_dic)
        try:
            clientsock.send(data)
        except:
            print 'Admin disconnected'
            clientsock.close()
            break
        time.sleep(0.5)

global clients,client_id
clients = {}
client_id = 0
def client_handler(clientsock,addr):
    global clients,client_id
    curr_id = client_id
    client_id += 1
    clients[curr_id] = clientsock
    buildings_string = pickle.dumps(buildings)
    clientsock.send(buildings_string)
    while True:
        data = clientsock.recv(BUFFSIZE)
        if 'Request:' not in data:
            continue
        else:
            data = data.replace('Request:','')
            start,end = pickle.loads(data)
            request = Request(curr_id, start, end)
            requests.append(request)
            print 'Added request, requests now:',requests
            break
        time.sleep(0.5)
    while True:
        if request in handled_requests: 
            taxi = request.taxi
            if taxi.path:
                taxi_info_tuple = (taxi.x, taxi.y, len(taxi.path), taxi.prev, taxi.taxi_id)
                #TODO - maybe pass taxi's path and then paint it in orange in client
                taxi_string = pickle.dumps(taxi_info_tuple)
                clientsock.send('Your taxi:'+taxi_string)
            if (taxi.x,taxi.y) == end:
                clientsock.send('Arrived to destination')
        time.sleep(0.5)
        

thread.start_new_thread(handle_requests,())
thread.start_new_thread(wait_for_connection, (server,))
thread.start_new_thread(move_taxi0_test_lmao,())
thread.start_new_thread(move_taxi1_test_lmao,())
thread.start_new_thread(charge_taxi2_test_lmao,())
#thread.start_new_thread(stop_test,())

while True:
    pass
