from Pathfinding import find_path
import time
import pickle

speedup = 30.0

class Taxi:
    taxi_id = 1

    def __init__(self, x=15, y=9):
        self.status = 'available' #Status options: available, charging, on the way, disabled
        self.battery = 100 #percentage
        self.x = x
        self.y = y
        self.path = None
        self.prev = None
        self.client = None
        self.taxi_id = Taxi.taxi_id
        Taxi.taxi_id += 1
        print 'Taxi',self.taxi_id,'created'
    
    def move_to(self, destination, obstacles, **kwargs):
        if (self.x,self.y) == destination:
            self.path = None
            self.status = 'available'
            return
        if not self.path:
            self.path = find_path((self.x,self.y),destination, disallowed = obstacles, h=19, w=29)
        if destination!=(15,10):
            self.status = 'on the way'
        while self.path:
            #TODO - THINK ABOUT THIS SHIT BETTER PLZ
            #if self.status == 'cancelled':
            if self.status == 'disabled':
                self.status = 'available'
                return
            self.prev = (self.x,self.y)
            self.x,self.y = self.path[0]
            del self.path[0]
            self.battery-=1/3.0
            time.sleep(30.0/speedup)
        if 'dest2' in kwargs:
            self.move_to(kwargs['dest2'], obstacles)
        elif self.battery <= 20.0:
            self.go_charge(obstacles)
        self.status = 'available'
    
    def go_charge(self, obstacles):
        #TODO: FIX THIS SHIT IGNORES BUILDINGS
        self.status = 'charging'
        self.move_to((15,10), obstacles) 
        self.status = 'charging'
        self.prev = None
        time.sleep(15*60.0/speedup)
        self.battery = 100
    
    def stop(self):
        #self.status = 'cancelled'
        self.status = 'disabled'
