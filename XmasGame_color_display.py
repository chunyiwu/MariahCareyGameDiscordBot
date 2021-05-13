# -*- coding: utf-8 -*-
"""
XmasGame_plotting

The bot for plotting the result in the "All I Want for Christmas is not 
hearing 'All I want for Christmas is You'" game.


Version History
[0.1] 2019-07-09
- plot history
- allowed custom colors for players

Created on Jul 6, 2019
Last updated on Jul 9, 2019

@author: Chun-Yi Wu
"""

import numpy
import csv
import time
import matplotlib.pyplot as plt

# =============================================================================
# class definitions
# =============================================================================

class Player:
    ## fields
    name_f   = 'John Doe'   # full name
    name     = 'John'       # first name
    times    = time.time()  # time stamps
    points   = 0            # points at time stamps
    color    = "#000000"    # color for plotting


    ## constructor
    def __init__(self,name_f,t0,p0):
        self.name_f = name_f
        self.name   = name_f.split(" ",1)[0]
        self.times  = [t0]
        self.points = [p0]


    ## points management
    # add a change of points
    def point_change(self,t,dpt):
        self.times.append(t)
        self.points.append(self.points[-1]+dpt)

    # remove the previous change of points
    def undo_change(self):
        self.times = self.times[:-1]
        self.points = self.points[:-1]


    ## text representation
    def to_string(self,mode):
        if mode == 1:
            return self.name + " (" + str(int(self.points[-1])) + ")"
        elif mode == 2:
            return self.name_f + " (" + str(int(self.points[-1])) + ")"



# =============================================================================
# common functions
# =============================================================================

def find_player(name):
    # INPUT:
    # name  - name of the player
    #
    # OUTPUT:
    # 1 - index of the player
    #        >=0 : the index
    #       -101 : player not found
    #       -102 : multiple players found

    # go through the list, and find the player with the same name as requested
    i_candidates = []

    for ii in numpy.arange(len(players)):
        if players[ii].name_f.upper().startswith(name.upper()):
            i_candidates.append(ii)

    if len(i_candidates) == 1:
        return i_candidates[0]
    elif len(i_candidates) == 0:
        return -101
    else:
        return -102

# =============================================================================
# Input
# =============================================================================
        
inDebugMode = True

if inDebugMode:
    fname_player = "player_debug.txt"
    fname_record = "record_debug.txt"
else:
    fname_player = "player.txt"
    fname_record = "record.txt"
    
fname_colors = "database/player_colors.txt"
mode = 2

# =============================================================================
# Read the data
# =============================================================================
            
players = []



with open(fname_colors) as f_colors:
    csv_reader = csv.reader(f_colors, delimiter=',')
    for row in csv_reader:
        if ( row[0][0] != '!' ):
            player = Player(row[0],0,0)
            player.color = row[1]
            players.append(player)
        
if ( mode == 1 ):
    iis_player = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
else:
    iis_player = [12,13,15,16,17,18,19,6,3,20,21]    
    
        
n_player = len(iis_player)

x = numpy.array([0,n_player-1])
yy = numpy.arange(0.0,n_player,1)

# =============================================================================
# Plot
# =============================================================================
    
fig = plt.figure(figsize=(4,4))

    
#for i_player in range(n_player-2):
ind = 0
for i_player in iis_player:
    y = numpy.array([1,1]) * ind
    plt.plot(x,y, players[i_player].color,lw=5,label=players[i_player].name_f)
    plt.plot(y,x, players[i_player].color,lw=5)
    ind = ind + 1

plt.plot(yy,yy,'#ffffff',marker='s',markersize=10)

plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), shadow=True, ncol=4)
plt.title('All I want for Christmas is not to hear "All I Want For Christmas Is You"\nColor display test')
plt.grid(True)