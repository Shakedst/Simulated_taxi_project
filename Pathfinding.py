from Tkinter import *
from math import sqrt
import time

def find_path(pos,pos2,**kwargs):
    canvas_w,canvas_h = kwargs['w'],kwargs['h']
    if 'disallowed' in kwargs.keys():
        disallowed = kwargs['disallowed']
        if pos2 in disallowed:
            disallowed.remove(pos2)
    try:
        m = float((pos2[1]-pos[1]))/(pos2[0]-pos[0])
    except ZeroDivisionError:
        m = 99999
    func = {'m': m, 'b': pos[1]-m*pos[0]}
    prevs = []
    end_options = [(pos2[0]+1,pos2[1]),(pos2[0]-1,pos2[1]),(pos2[0],pos2[1]+1),(pos2[0],pos2[1]+1)]
    while pos != pos2:
        x,y = pos[0],pos[1]
        prevs.append(pos)
        options = [(x-1,y),(x,y+1),(x+1,y),(x,y-1)]
        options = filter(lambda opt: (pos[0]<=opt[0]<=pos2[0] or pos[0]>=opt[0]>=pos2[0]) and (pos[1]<=opt[1]<=pos2[1] or pos[1]>=opt[1]>=pos2[1]), options)
        if disallowed:
            options = filter(lambda opt: opt not in disallowed+prevs,options)
        options = filter(lambda opt: canvas_w>=opt[0]>=0 and canvas_h>=opt[1]>=0,options)
        if not options:
            options = [(x-1,y),(x,y+1),(x+1,y),(x,y-1)]
            if disallowed:
                options = filter(lambda opt: opt not in disallowed+prevs,options)
            options = filter(lambda opt: canvas_w>=opt[0]>=0 and canvas_h>=opt[1]>=0,options)
            if not options:
                pos = prevs[prevs.index(pos)-1]
                continue
        closest_to_func = tuple(sorted(options, key=lambda p:p[1]-(p[0]*func['m']+func['b'])))
        closest_to_end = tuple(sorted(options, key=lambda p:sqrt((p[0]-pos2[0])**2+(p[1]-pos2[1])**2)))
        options2 = {option: closest_to_func.index(option)+closest_to_end.index(option) for option in options}
        best = min(options2,key=lambda key:options2[key])
        pos = best
    path = prevs
    path.append(pos)
    return path

