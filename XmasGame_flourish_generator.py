# -*- coding: utf-8 -*-
"""
XmasGame_flourish_generator

Generate the files for flourish animated bar chart.

@author: Chun-Yi Wu
"""

import numpy as np
import csv
import time
import datetime
import re



# define file names
record_dir = "record/" #"old_files/2020/" #
fname_player = record_dir + 'player.txt'
fname_record = record_dir + 'record.txt'
fname_info   = record_dir + 'info.txt'

# storage 
t_bounds = []
players = []
hits = []

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


timezone = 0

# time adjustment
t_adjust_disp = timezone * 3600

d = datetime.datetime.now() - datetime.datetime.utcnow()
t_adjust = t_adjust_disp - (d.days*86400+d.seconds+d.microseconds/1e6)


# define classes
class Player:
    # -------------------------------------------------------------------------
    # fields
    # -------------------------------------------------------------------------
    
    name   = 'John Doe'     # name
    discord_id = 0
    times    = time.time()  # time stamps
    points   = 0            # points at time stamps
    points_mg = 0           # minigame points (not a series)
    is_in_game = False      # if the player is in game


    # -------------------------------------------------------------------------
    # constructor
    # -------------------------------------------------------------------------
    
    def __init__(self, name, discord_id, t0, p0, is_new):
        self.name = name
        self.times  = [t0]
        self.points = [p0]
        self.discord_id = discord_id
        self.is_in_game = True
        
        if is_new:
            with open(fname_player,'a') as f:
                f.write(alphabet[len(players)] + ", " + self.to_string("print")+'\n')
                f.flush()
            
        


    # -------------------------------------------------------------------------
    # points management
    # -------------------------------------------------------------------------
    
    def point_change(self,t,dpt):
        self.times.append(t)
        self.points.append(self.points[-1]+dpt)
    
    def mgpoint_change(self,dpt):
        self.points_mg += dpt


    # -------------------------------------------------------------------------
    # text representation
    # -------------------------------------------------------------------------
    
    def to_string(self, mode):
        if ( mode == "shadow" ):
            return self.name + " (" + str(int(self.points[-1])) + "," + str(int(self.points_mg)) + ")"
        
        elif ( mode == "progress" ):            
            text = ""
            for jj in np.arange(self.points[-1]):
                text += "\u25A2"
            text += "  - " + self.name + " (" + str(int(self.points[-1])) + ")"
            return text
        
        elif ( mode == "print" ):       
            return self.name + ", " + str(self.discord_id) + ", " + str(self.times[0]) + ", " + str(self.points[0])
        
        else:
            return self.name

class Hit:
    # -------------------------------------------------------------------------
    # fields
    # -------------------------------------------------------------------------
    
    player = []
    points = 0
    time = 0
    comment = ""
    
    
    # -------------------------------------------------------------------------
    # constructor
    # -------------------------------------------------------------------------
    
    def __init__(self,time,player,points,comment, is_new):
        self.time = time
        self.player = player
        self.points = points
        self.comment = comment
        
        if is_new:
            with open(fname_record, 'a') as f:
                f.write(str(len(hits)) + ", " + self.to_string("print") + "\n")
            
        
    
    # -------------------------------------------------------------------------
    # text representation
    # -------------------------------------------------------------------------
    
    def to_string(self, mode):
        if ( mode == "shadow" ):
            text = datetime.datetime.fromtimestamp(self.time).strftime("%Y-%m-%d %H:%M:%S")
            text += " | "
            for ii in np.arange(len(self.player)):
                text += self.player[ii].name + ", "
            text += " | " + str(self.points) + " | " + self.comment
            
        elif ( mode == "print" ):
            text = str(self.time) + ", "
            for ii in np.arange(len(self.player)):
                text += alphabet[find_player(self.player[ii].discord_id)]
            text += ", " + str(self.points) + ", " + self.comment
            
        return text




# define functions            
def find_player(discord_id):
    ind = -1
    
    for ii in np.arange(len(players)):
        if ( discord_id == players[ii].discord_id ):
            ind = ii
    return ind


def get_time_string(t):
    return datetime.datetime.fromtimestamp(t+t_adjust_disp).strftime("%m/%d %H:%M")


def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)




# load info file
try:
    with open(fname_info) as f:
        csv_reader = csv.reader(f, delimiter=',')
        for txt in csv_reader:
            t_bounds.append(float(txt[0]))
  
except Exception as ex:
    print("Can't find the info file?")  
    print(ex)

# load player file
try:
    with open(fname_player) as f:
        csv_reader = csv.reader(f, delimiter=',')
        for txt in csv_reader:
            label = txt[0]
            name = txt[1]
            discord_id = int(txt[2])
            t0 = float(txt[3])
            p0 = int(txt[4])
            
                    
            if ( label == '+' ):
                players[find_player(discord_id)].is_in_game = True
            elif ( label == '-' ):
                players[find_player(discord_id)].is_in_game = False
            else:
                players.append(Player(name, discord_id, t0, p0, False))
                
except Exception as ex:
    print("Can't find the player file?")
    print(ex)

# load record file
try:
    with open(fname_record, 'r', encoding='ascii', errors='ignore') as f:
        csv_reader = csv.reader(f, delimiter=',')
        for txt in csv_reader:
            time = float(txt[1])
            ps = txt[2].strip()
            points = int(txt[3])
            comment = txt[4]
            
            hps = []
            
            for ii in np.arange(len(ps)):
                hps.append(players[ord(ps[ii])-65])
                players[ord(ps[ii])-65].point_change(time,points)
                
            h = Hit(time, hps, points, deEmojify(comment), False)
            hits.append(h)
                
except Exception as ex:
    print("Can't find the record file?") 
    print(ex)    
            

## set up storage
nn_p = len(players)

t0 = t_bounds[1]+1
tf = t_bounds[4]+601
nn_t = int((tf-t0)/600+1)

ts = np.linspace(t0, tf, (nn_t))

ii_hit = 0
nn_hit = len(hits)

print('nn_p = ', str(nn_p))
print('nn_t = ', str(nn_t))
print('nn_hit = ', str(nn_hit))

table = np.ndarray(shape=(nn_t,nn_p))
table[:][:] = 0

for ii0_t in range(0,nn_t-1):
    ii_t = ii0_t + 1
    table[ii_t][0:nn_p] = table[ii0_t][0:nn_p]
    
    if ( ii_hit < nn_hit ):
        if ( hits[ii_hit].time < ts[ii_t] ):
            
            # passed the time, change scores
            for ii_ph in np.arange(len(hits[ii_hit].player)):            
                ii_p = find_player(hits[ii_hit].player[ii_ph].discord_id)
                table[ii_t][ii_p] += hits[ii_hit].points
                                
            ii_hit += 1
        
    
fname_flourish = 'flourish.csv'
with open(fname_flourish, 'w+', newline='') as f:
    # header
    f.write('name, category')
    
    for ii_t in range(0,nn_t):
        # totalHours = int((ts[ii_t]-t0)/3600) + 12.01
        # dd = int(np.ceil(totalHours/24))
        # hh = int(np.mod(totalHours,24))
        # print(str(totalHours)+' = '+str(dd)+"/"+str(hh))
        
        #f.write(', 12/' + str(dd) +  ' ' + "{:02d}".format(hh) + ':00' )
        print(get_time_string(ts[ii_t]))
        f.write(', ' + get_time_string(ts[ii_t]))

    f.write('\n')
    
    
    # print data
    for ii_p in range(0,nn_p):
        f.write(players[ii_p].name)
        f.write(', ')
        f.write(players[ii_p].name)

        
        for ii_t in range(0,nn_t):
            f.write(', ' + str(table[ii_t][ii_p]) )

        f.write('\n')
        
        
fname_comment = 'comment.csv'
with open(fname_comment, 'w+') as f:
    for ii_hit in range(0, nn_hit):
        print(len(hits[ii_hit].comment))
        if ( len(hits[ii_hit].comment) > 1 ):
            time = 600*np.floor(hits[ii_hit].time/600)
            f.write(get_time_string(time) + ', ' + get_time_string(time+3600*24) + ', ')
            for ii_p in range(0, len(hits[ii_hit].player)):
                if ( ii_p > 0 ):
                    f.write('/')
                f.write(hits[ii_hit].player[ii_p].name)
                
            f.write(': ' + hits[ii_hit].comment) 
            f.write('\n')

input('hit enter to continue')
