# -*- coding: utf-8 -*-
"""
XmasGameBot_DiscordV2021

The discord bot for managing the "All I Want for Christmas is not hearing
 'All I wantfor Christmas is You'" game.

@author: Chun-Yi Wu
"""

"""
Packages to install:
    pip install asyncio
    pip install discord
    pip install python-dotenv
"""


"""
NOTES:http://www.fileformat.info/info/unicode/char/search.htm for emoji Unicode
"""

# =============================================================================
# Initialization
# =============================================================================

# import the packages
import os
import asyncio
import nest_asyncio
import discord
from dotenv import load_dotenv
import numpy as np
import csv
import time
import datetime
import random
import traceback

# set up the discord environment
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True

nest_asyncio.apply()
client = discord.Client(intents=intents)

channels = []

id_teabot   = 682945654489874433
id_timerbot = 714141847035052051



# =============================================================================
# constants/parameters
# =============================================================================

# game time
game_year   = 2021      # year of the game
game_month  =   12      # month of the game
timezone    =   -6      # offset from UTC ( CST = -6)

# game settings
first_penalty = 3       # points for the first hit

# game status
phase = -1              # the phase of the game
                        # -1 - before start
                        #  0 - after start, before bonus phase
                        #  1 - after bonus phase, before the game ends
                        #  2 - game ended

# dev flag
debugMode = 1

# bot version
version_num = '2.2'
last_update = 'June 20, 2021'


# alphabet string
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# carrot messages
msg_carrot_yes = \
    ["I want to keep my box.",\
     "I have the carrot in my box.",\
     "I'm pretty sure you don't have the carrot.",\
     "you're going to have to pry my box from my cold, virtual hand.",\
     "you're going to want to switch boxes with me.",\
     "you don't want to keep your box."]
msg_carrot_no = \
    ["I want to swap the box.",\
     "I want your box.",\
     "I don't have the carrot in my box.",\
     "I'm pretty sure you have the carrot in your box.",\
     "you're going to want to keep your boxes.",\
     "you don't want to switch boxes with me."]
msg_carrot_maybe = \
    ["I'm just going to let you guess.",\
     "I'm not going to tell you anything.",\
     "you're just going to have to guess."]
        
# point change pictures
img_pnt = \
    ["pics/pnt_sub2.png",\
     "pics/pnt_sub1.png",\
     "pics/quit.png",\
     "pics/pnt_add1.png",\
     "pics/pnt_add2.png",\
     "pics/pnt_add3.png"]
        
        
# emoji variables
rxn_progress = "\U0001F4CA"
rxn_credit = "\U0001F389"
rxn_reset = "\U0001F504"
rxn_join = "\U0001F4E5"
rxn_withdraw = "\U0001F4E4"
rxn_hit = "<:mc_album:686011859207585817>"
rxn_group_hit = "<:mc_divacup:685130640450256915>"
rxn_link_hit = "<:mc_album:686011859207585817>"
rxn_link_safe = "\U0001F44C"
rxn_yes = "\U0001F1FE"
rxn_no = "\U0001F1F3"
rxn_carrot = "\U0001F955"
rxn_rpsls = "\U0001F44B"
rxn_trivia = "\U0001F4A1"
white_square = "\u25A2"
black_square = "\u25A0"


# =============================================================================
# derived constants/parameters
# =============================================================================

# time adjustment
t_adjust_disp = timezone * 3600

d = datetime.datetime.now() - datetime.datetime.utcnow()
t_adjust = t_adjust_disp - (d.days*86400+d.seconds+d.microseconds/1e6)




# =============================================================================
# class definitions
# =============================================================================

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
            # for displaying in shadow realm
            # [name] ([points], [mg_points])
            return self.name + " (" + str(int(self.points[-1])) + "," + str(int(self.points_mg)) + ")"
        
        elif ( mode == "progress" ):            
            # progress mode
            # [points bar] - [name] ([points])
            text = ""
            if ( self.points[-1] > 0 ):
                for jj in np.arange(self.points[-1]):
                    text += white_square
            else:
                for jj in np.arange(-self.points[-1]):
                    text += black_square
                
                
            text += "  - " + self.name + " (" + str(int(self.points[-1])) + ")"
            return text
        
        elif ( mode == "print" ):
            # print mode: for creating the record file
            # [name], [discord id], [time when joined], [starting points]
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
            # for displaying in shadow realm
            text = get_time_string(self.time)
            text += " | "
            for ii in np.arange(len(self.player)):
                text += self.player[ii].name + ", "
            text += " | " + str(self.points) + " | " + self.comment
            
        elif ( mode == "print" ):
            # for making record file
            text = str(self.time) + ", "
            for ii in np.arange(len(self.player)):
                text += alphabet[find_player(self.player[ii].discord_id)]
            text += ", " + str(self.points) + ", " + self.comment
            
        return text

class Link:
    # -------------------------------------------------------------------------
    # fields
    # -------------------------------------------------------------------------
    
    url = '';
    is_hit = False
    t_resolve = 0
    msg_id = 0
    
    has_resolved = False
    
    
    # -------------------------------------------------------------------------
    # constructor
    # -------------------------------------------------------------------------
    
    def __init__(self, url, is_hit, t_issue, t_resolve, msg_id, is_new):
        self.url = url
        self.is_hit = is_hit
        self.msg_id = msg_id
        self.t_issue = t_issue
        self.t_resolve = t_resolve
        
        if is_new:
            with open(fname_link, 'a') as f:
                f.write(str(len(links)) + ", " + self.to_string("print") + "\n")
        
            
            
    # -------------------------------------------------------------------------
    # text representation
    # -------------------------------------------------------------------------
    
    def to_string(self, mode):
        if ( mode == "shadow" ):
            # for displaying in shadow realm
            text = "<" + self.url +">" + \
                    " | " + get_time_string(self.t_issue) +\
                    " | " + get_time_string(self.t_resolve) +\
                    " | " + str(self.msg_id)
            
        elif ( mode == "print" ):
            # for making record file
            text = self.url + \
                ", " + str(self.t_issue) + \
                ", " + str(self.t_resolve) + \
                ", " + str(self.msg_id) + \
                ", " + str(self.is_hit)
            
        return text
    
    
    
    # -------------------------------------------------------------------------
    # game management
    # -------------------------------------------------------------------------
                
    async def resolve(self):
        # change the status
        self.has_resolved = True
        
        # decide points
        if self.is_hit:
            pt = 1
            cmt = 'risky link was a hit!'
        else:
            pt = -1
            cmt = 'risky link was safe!'
            
        if ( self.t_issue > t_bounds[iit_bonus] ):
            pt = pt * 2
                    
        # get list of players 
        msg = await chans[iichan_rsk].fetch_message(self.msg_id) 
        rxns = msg.reactions
        
        ps = []
        
        for ii in np.arange(len(rxns)):
            async for user in rxns[ii].users():
                if not user.bot:
                    ind = find_player(user.id)
                    ps.append(players[ind])
                    
        if len(ps) != 0 :
            for ii in np.arange(len(ps)):
                ps[ii].point_change(self.t_resolve, pt)
            
            h = Hit(self.t_resolve, ps, pt, cmt, True)
            hits.append(h) 
            
            sstr = "Beep bop. Reported "
            for ii in np.arange(len(ps)):
                sstr += ps[ii].name + ", "
            sstr = sstr[0:(len(sstr)-2)] + " for " + str(pt) + " point!"
            
            if ( cmt != "" ):
                sstr += "\nComment: " + cmt
            
            await chans[iichan_pnt].send(sstr+"\n\n"+progress_str(), file=discord.File(img_pnt[pt+2]))
            
        if self.is_hit:
            await msg.add_reaction(rxn_link_hit)
        else:
            await msg.add_reaction(rxn_link_safe)
            
        # add in the preview
        await msg.edit( content= \
            "**Beep beep. Risky link of the day!**\n\n" +\
            self.url + "\n\n" + \
            "Time to resolve: " + get_time_string(self.t_resolve-t_adjust_disp) + "\n\n" + \
            "React with \u2705 if you watched the video!\n" +\
            rxn_link_safe + " means this link is resolved, and the video is safe.\n"+\
            rxn_link_hit+" means this link is resolved, and the video is a trap.")
        
class MiniGameResult:
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
            with open(fname_game, 'a') as f:
                f.write(str(len(mg_results)) + ", " + self.to_string("print") + "\n")
            
        
    
    # -------------------------------------------------------------------------
    # text representation
    # -------------------------------------------------------------------------
    
    def to_string(self, mode):
        if ( mode == "shadow" ):
            # for displaying in shadow realm
            text = datetime.datetime.fromtimestamp(self.time).strftime("%Y-%m-%d %H:%M:%S")
            text += " | "
            for ii in np.arange(len(self.player)):
                text += self.player[ii].name + ", "
            text += " | " + str(self.points) + " | " + self.comment
            
        elif ( mode == "print" ):
            # for making record files
            text = str(self.time) + ", "
            for ii in np.arange(len(self.player)):
                text += alphabet[find_player(self.player[ii].discord_id)]
            text += ", " + str(self.points) + ", " + self.comment
            
        return text
    

# =============================================================================
# functions
# =============================================================================

# -----------------------------------------------------------------------------
# time related functions
# -----------------------------------------------------------------------------
            
def get_time(year, month, day, hour, minute, second, t_adjust):
    # INPUT
    # year      - year of the date
    # month     - month of the date
    # day       - day of the month
    # hour      - 24-hour hour of day
    # minute    - minute of the time
    # second    - second of the time
    # t_adjust  - adjustment time to utc

    t_str = str(year) + "/" + str(month) + "/" + str(day) \
            + " " + str(hour) + ":" + str(minute) + ":" + str(second)
    return time.mktime(time.strptime(t_str,"%Y/%m/%d %H:%M:%S")) - t_adjust

def get_current_time():
    return datetime.datetime.now().timestamp()

def duration_str(t):
    if t < 0:
        text = "-"
        t = -t
    else:
        text = ""

    t_s =          t        % 60
    t_m = np.floor(t/   60) % 60
    t_h = np.floor(t/ 3600) % 24
    t_d = np.floor(t/86400)

    text +=   str(int(t_d)) + "d " \
            + str(int(t_h)) + "h " \
            + str(int(t_m)) + "m " \
            + str(int(t_s)) + "s"
    return text

def get_time_string(t):
    return datetime.datetime.fromtimestamp(t+t_adjust_disp).strftime("%Y-%m-%d %H:%M:%S")


# -----------------------------------------------------------------------------
# bot exclusion functions
# -----------------------------------------------------------------------------
    
def check_rxn_not_by_bot(rxn,user):
    return not user.bot

    


# -----------------------------------------------------------------------------
# look up functions
# -----------------------------------------------------------------------------

def find_player(discord_id):
    ind = -1
    
    for ii in np.arange(len(players)):
        if ( discord_id == players[ii].discord_id ):
            ind = ii
    return ind

    


# -----------------------------------------------------------------------------
# game functions
# -----------------------------------------------------------------------------
    
def progress_str():
    tnow = get_current_time()
    
    points = []
    for ii in np.arange(len(players)):
        points.append(players[ii].points[-1])

    text  = "**Current standing** \n"
    if tnow < t_bounds[iit_start]:
        text += "Game status: not started yet \n"
    elif tnow < t_bounds[iit_bonus]:
        text += "Game status: ongoing (normal mode)\n"
    elif tnow < t_bounds[iit_end]:
        text += "Game status: ongoing (bonus mode)\n"
    else:
        text += "Game status: ended!\n"

    text += "Game time: " + get_time_string(tnow) + "\n"
    text += "Time since start: " + duration_str(tnow-t_bounds[iit_start]) + "\n"
    text += "Time until end: " + duration_str(t_bounds[iit_end]-tnow) + "\n"
    text += "\n"
    text += "**Points**\n"

    for ii in np.argsort(points):
        text += players[ii].to_string("progress") + "\n"
    return text






# =============================================================================
# main program
# =============================================================================

# define the time boundaries
if ( debugMode == 0 ):
    t_game_start = get_time(game_year, game_month,  1,12, 0, 0, t_adjust)
    # t_game_start = get_time(2020, 7,  7,12, 0, 0, t_adjust)
    dt = 86400
    
    t_bounds = [ \
                t_game_start -  1 * dt,
                t_game_start +  0 * dt,
                t_game_start + 20 * dt, 
                t_game_start + 23 * dt,
                t_game_start + 24 * dt,
                t_game_start + 25 * dt]

    fname_record = 'record/record.txt'
    fname_player = 'record/player.txt'
    fname_link = 'record/links_in_play.txt'
    fname_game = 'record/minigame.txt'

elif (debugMode == 1):
    print('Program started')
    t_game_start = np.ceil(get_current_time()/3600)*3600 + 3600*-1
    dt = 3600
    
    t_bounds = [t_game_start -  1 * dt,
                t_game_start +  0 * dt,
                t_game_start +  1 * dt, 
                t_game_start +  2 * dt,
                t_game_start +  3 * dt,
                t_game_start +  4 * dt]
    
    fname_record = 'record/record_debug.txt'
    fname_player = 'record/player_debug.txt'
    fname_link = 'record/links_in_play_debug.txt'
    fname_game = 'record/minigame_debug.txt'
    print('Time bounds defined')
    print(t_bounds)
    
iit_warn  = 0
iit_start = 1
iit_bonus = 2
iit_5vids = 3
iit_end   = 4
iit_quit  = 5

phases_started = [False]*6
t_start = 0

# channels
chans = [discord.TextChannel]*10

iichan_inf = 0
iichan_ann = 1
iichan_pnt = 2
iichan_cmd = 3
iichan_rsk = 4
iichan_vot = 5
iichan_adm = 6
iichan_sha = 7
iichan_gam = 8


# data storages
players = []
hits = []
links = []
mg_results = []


# write the info file
fname_info = 'record/info.txt'
with open(fname_info, 'w+') as f:
    for ii in np.arange(len(t_bounds)):
        f.write(str(t_bounds[ii])+"\n")
print('Info file generated')



# =============================================================================
# async functions
# =============================================================================
    
# -----------------------------------------------------------------------------
# set up functions
# -----------------------------------------------------------------------------
    
async def get_channels():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    for chan in guild.channels:
        if ( chan.name == "information"):
            chans[iichan_inf] = chan
        
        if ( chan.name == "announcements"):
            chans[iichan_ann] = chan
            
        if ( chan.name == "point-changes"):
            chans[iichan_pnt] = chan
            
        if ( chan.name == "commands"):
            chans[iichan_cmd] = chan
            
        if ( chan.name == "risky-click"):
            chans[iichan_rsk] = chan
            
        if ( chan.name == "voting"):
            chans[iichan_vot] = chan
            
        if ( chan.name == "admin-corner"):
            chans[iichan_adm] = chan           
        
        if ( chan.name == "shadow-realm" ):
            chans[iichan_sha] = chan      
        
        if ( chan.name == "mini-games" ):
            chans[iichan_gam] = chan
            
    return 1
            
async def reset_cmd():
    await chans[iichan_cmd].purge()
    msg = await chans[iichan_cmd].send( \
        "==== COMMAND CENTRAL =====\n" +\
        "React to this message according to what you want to do: \n" +\
        " \n" +\
        rxn_hit + " - report a hit on self\n" +\
        rxn_group_hit + " - report a hit on multiple people\n" +\
        # rxn_progress + " - progress report\n" +\
        # rxn_credit + " - credit\n" + \
        rxn_join + " - join game\n" +\
        rxn_withdraw + " - withdraw from game\n" +\
        "==========================")
    await msg.add_reaction(rxn_hit)
    await msg.add_reaction(rxn_group_hit)
    # await msg.add_reaction(rxn_progress)
    # await msg.add_reaction(rxn_credit)
    await msg.add_reaction(rxn_join)
    await msg.add_reaction(rxn_withdraw)
    return 1
    
async def reset_gam():
    await chans[iichan_gam].purge()
    msg = await chans[iichan_gam].send( \
        "======== MINI GAMES ========\n" +\
        "What would you like to play?\n" +\
        "\n" +\
        rxn_carrot + " - carrot in a box\n" +\
        rxn_rpsls + " -rock paper scissors lizard spock\n" +\
        rxn_trivia + " - random trivia\n" +\
        "============================")
    await msg.add_reaction(rxn_carrot)
    await msg.add_reaction(rxn_rpsls)
    await msg.add_reaction(rxn_trivia)
    return 1
    
async def reset_inf():
    await chans[iichan_inf].purge()
    await chans[iichan_inf].send(\
        "==========================\n" +\
        "__**Channel Summary**__\n" +\
        "<#684548674973335587> - announcement related to the game, e.g. game start, bonus period, special events :speaker:\n" +\
        "<#685131112858910750> - any point changes in the game, whether it be from natural hit or videos\n" +\
        "<#682942694946897990> - where players can use command :mute:\n" +\
        "<#682943067355217966> - the risky click game\n" +\
        "<#686024833145897011> - for when there are things to be voted on:speaker:\n" +\
        "<#719709899897962580> - for short games to play:mute:\n" +\
        "\n" +\
        "__Legend__\n" +\
        ":mute:recommend to mute it\n" +\
        ":speaker:recommend to not mute it\n" +\
        "The rest of the channels can be muted by preference", file=discord.File("pics/channels.png"))
        
    await chans[iichan_inf].send(\
        "==========================\n" +\
        "__**Rule Summary**__\n" +\
        "The game starts on 12/01 at noon, and ends on 12/25 at noon.\n" +\
        "After 12/21 at noon, the game enters the 'Mariah Carey Merry Christmas Bonus Period,' and every point changes are doubled!\n" +\
        "\n" +\
        "Every time you hear the song, you get a hit, and you report it in the <#682942694946897990> channel.\n" +\
        "\n" +\
        "__What counts as hits?__\n" +\
        "The following count as hits:\n" +\
        "- Hearing the song\n" +\
        "- Hearing covers of the song, including mashups, parodies\n" +\
        "- Someone singing the song/parodies\n" +\
        "- Humming it to yourself\n" +\
        "\n" +\
        "The following don’t count as hits:\n" +\
        "- Thinking/dreaming about the song\n" +\
        "- Hearing it again within 10 minutes\n" +\
        "\n" +\
        "__Details__\n" +\
        "For more details, refer to the rulebook and the video:\n" +\
        "Video: <https://www.youtube.com/watch?v=PZMkieVQ7sE>\n" +\
        "Document: <https://docs.google.com/document/d/155IahiH3bUtuyeviKQPhilocg8NqzyZMcRypMl9Ks64/edit?usp=sharing>", file=discord.File("pics/rule.png"))
        
    await chans[iichan_inf].send(\
        "==========================\n" +\
        "__**Risky Click Game**__\n" +\
        "Every day, a random link will be posted in the <#682943067355217966> channel, which would lead you to a video that may or may not have the song. If you would like to risk it, open the link, and react to the message containing the link with :white_check_mark: . If the video did not contain the song, you lose a point; otherwise, you gain a point.\n" +\
        "\n" +\
        "At the time of resolution, the bot will automatically change the points, so don't report this!", file=discord.File("pics/video.png"))
        
    await chans[iichan_inf].send(\
        "==========================\n" +\
        "__**Role Tags**__\n" +\
        "The following game-related tags will be given at the end of each game:\n"+\
        "- Mariah Carey Fanatics: getting more than 15 points in a game\n"+\
        "- Mariah Carey Lambs: getting more than 10 points in a game\n"+\
        "- Champion [year]: the winner of the year\n"+\
        "- Cookie Maker [year]: the loser of the year\n", file=discord.File("pics/roles.png"))
        
        
    await chans[iichan_inf].send( \
        "==========================\n" +\
        "__**Credits**__\n" +\
         "I'm a little tea-bot. Version v"+version_num+"\n "+\
         "Last updated on "+last_update+"\n" +\
         "\n" +\
         "Stole the idea from Tom Scott <https://www.youtube.com/watch?v=QR9FwcwxTG4> \n\n" +\
         "See code on GitHub <https://github.com/chunyiwu/MariahCareyGameDiscordBot> \n\n" +\
         "Developed by Chun-Yi Wu, "+\
         "with help from Andrew Vernon, Lizzie Jouett, Antonio Roman, Angel Roman, Jim Hall", file=discord.File('pics/credit.png'))
    

async def load_game():    
    global players
    global hits
    global links
    global mg_results
    
    t_start = get_current_time()
    players = []
    hits = []
    links = []
    mg_results = []
        
    await get_channels()
    
    # check which phase of the game it is
    for ii in np.arange(len(t_bounds)):
        if ( t_bounds[ii] < t_start ):
            phases_started[ii] = True
            
    
    # read in existing files
    if os.path.exists(fname_player):
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
            await sr_debug_msg("Error when reading player files: \n"+repr(ex))
            traceback.print_exc()           
                    
    else:
        await sr_debug_msg("Player file don't exist! Creating it now")
        open(fname_player,'w+')
        
        
    if os.path.exists(fname_record):   
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
                        
                    h = Hit(time, hps, points, comment, False)
                    hits.append(h)
                        
        except Exception as ex:
            await sr_debug_msg("Error when reading record files: \n"+repr(ex))
            traceback.print_exc()         
                    
    else:
        await sr_debug_msg("Hit record file don't exist! Creating it now")
        open(fname_record,'w+')
        

    if os.path.exists(fname_link):              
        try:
            with open(fname_link) as f:
                csv_reader = csv.reader(f, delimiter=',')
                for txt in csv_reader:
                    url = txt[1].strip()
                    t_issue = float(txt[2])
                    t_resolve = float(txt[3])
                    msg_id = int(txt[4])
                    if ( txt[5].strip() == "True" ):
                        is_hit = True
                    elif ( txt[5].strip() == "False" ):
                        is_hit = False
                    else:
                        print(txt[5].strip())
                        is_hit = False
                
                    link = Link(url, is_hit, t_issue, t_resolve, msg_id, False)
                    if ( t_resolve < t_start ):
                        link.has_resolved = True
                    links.append(link)
                    
        except Exception as ex:
            await sr_debug_msg("Error when reading link files: \n"+repr(ex))
            traceback.print_exc()       
                    
    else:
        await sr_debug_msg("Link file don't exist! Creating it now")
        open(fname_link,'w+')
        
        
    if os.path.exists(fname_game):   
        try:
            with open(fname_game) as f:
                csv_reader = csv.reader(f, delimiter=',')
                for txt in csv_reader:
                    time = float(txt[1])
                    ps = txt[2].strip()
                    points = int(txt[3])
                    comment = txt[4]
                    
                    hps = []
                    
                    for ii in np.arange(len(ps)):
                        hps.append(players[ord(ps[ii])-65])
                        players[ord(ps[ii])-65].mgpoint_change(points)
                        
                    mgr = MiniGameResult(time, hps, points, comment, False)
                    mg_results.append(mgr)
                        
        except Exception as ex:
            await sr_debug_msg("Error when reading record files: \n"+repr(ex))
            traceback.print_exc()         
                    
    else:
        await sr_debug_msg("Mini game reesult file don't exist! Creating it now")
        open(fname_game,'w+')
            
         
                    
    
# -----------------------------------------------------------------------------
# command functions
# -----------------------------------------------------------------------------
    
async def report_self(discord_id):
    tnow = get_current_time()
    
    if ( tnow > t_bounds[iit_end] ):
        await chans[iichan_cmd].send("Beep beep. The game ended already!")
        await cue_reset_cmd()
        return
    elif ( tnow < t_bounds[iit_start] ):
        await chans[iichan_cmd].send("Beep beep. The game hasn't started yet!")
        await cue_reset_cmd()
        return
        
    ind = find_player(discord_id)
    if ( ind == -1 ):
        await chans[iichan_cmd].send("Beep. I can't find you in the game?")
        
    elif ( not players[ind].is_in_game ):
        await chans[iichan_cmd].send("Beep. Seems like you're currently taking a break from the game? Please rejoin before reporting the hit!")
        
    else:
        await chans[iichan_cmd].send("Beep Bop. Comment within the next 60 seconds if you would like to do so, or type 'x' to skip!\n" +\
                                     "Type 'nvm' if it's a misclick!")
        
        try:
            def same_user(msg):
                return msg.author.id == discord_id
            
            msg = await client.wait_for('message', timeout=60.0, check=same_user)
            
            if ( msg.content.lower() == 'x' ):
                p = max(1,first_penalty-len(hits))
                if ( tnow > t_bounds[iit_bonus] ):
                    p = p * 2
                    
                players[ind].point_change(tnow,p)
                
                h = Hit(tnow, [players[ind]], p, "", True)
                hits.append(h)                
                
                await chans[iichan_cmd].send("Beep bop. Reported " + players[ind].name + " for " + str(p) + " point!", file=discord.File(img_pnt[p+2]))
                await chans[iichan_pnt].send("Beep bop. Reported " + players[ind].name + " for " + str(p) + " point!"+"\n\n"+progress_str(), file=discord.File(img_pnt[p+2]))
                
            elif msg.content.lower() == 'nvm' or msg.content.lower() == 'nevermind' or msg.content.lower() == 'never mind':
                await chans[iichan_cmd].send("Beep bop. Aborting the hit reporting.")
                
            else:
                p = max(1,first_penalty-len(hits))
                if ( tnow > t_bounds[iit_bonus] ):
                    p = p * 2
                    
                players[ind].point_change(tnow,p)
                
                h = Hit(tnow, [players[ind]], p, msg.content, True)
                hits.append(h)                
                
                await chans[iichan_cmd].send("Beep bop. Reported " + players[ind].name + " for " + str(p) + " point!\nComment: "+msg.content, file=discord.File(img_pnt[p+2]))
                await chans[iichan_pnt].send("Beep bop. Reported " + players[ind].name + " for " + str(p) + " point!\nComment: "+msg.content+"\n\n"+progress_str(), file=discord.File(img_pnt[p+2]))
                
        except asyncio.TimeoutError:
            p = max(1,first_penalty-len(hits))
            if ( tnow > t_bounds[iit_bonus] ):
                p = p * 2
                
            players[ind].point_change(tnow,p)
            
            h = Hit(tnow, [players[ind]], p, "", True)
            hits.append(h)            
            
            await chans[iichan_cmd].send("Beep bop. Reported " + players[ind].name + " for " + str(p) + " point! \nThe channel will reset by itself in 5 second...", file=discord.File(img_pnt[p+2]))
            await chans[iichan_pnt].send("Beep bop. Reported " + players[ind].name + " for " + str(p) + " point!"+"\n\n"+progress_str(), file=discord.File(img_pnt[p+2]))
            time.sleep(5.0)
            await reset_cmd()
            return

    await cue_reset_cmd()
    return 1

async def report_group(discord_id):
    tnow = get_current_time()
    
    if ( tnow > t_bounds[iit_end] ):
        await chans[iichan_cmd].send("Beep beep. The game ended already!")
        await cue_reset_cmd()
        return
    elif ( tnow < t_bounds[iit_start] ):
        await chans[iichan_cmd].send("Beep beep. The game hasn't started yet!")
        await cue_reset_cmd()
        return
        
    try:
        def same_user(msg):
            return msg.author.id == discord_id
        
        await chans[iichan_cmd].send("Beep bop. Tag all the players that got hit in the next 120 seconds.")
        msg = await client.wait_for('message', timeout=120.0, check=same_user)
        
        members = msg.mentions
        
    except asyncio.TimeoutError:        
        await chans[iichan_cmd].send("Beep. You took too long! Try it again, or let my dad know if the list is too long.")
        time.sleep(5.0)
        await reset_cmd()
        return
    
    
    ps = []
    
    for ii in np.arange(len(members)):
        ind = find_player(members[ii].id)
        
        if ( ind == -1 ):
            await chans[iichan_cmd].send("Beep. I can't find player "+members[ii].name+". Are they in the game? Skipping this person.")
        
        elif ( not players[ind].is_in_game ):
            await chans[iichan_cmd].send("Beep. The player "+players[ind].name+" is taking a break. They will be skipped.")
            
        else:
            ps.append(players[ind])
            
    if len(ps) == 0:    
        await chans[iichan_cmd].send("Beep. I didn't detect any players? Try it again")
        await cue_reset_cmd()
        return
            
    p = max(1,first_penalty-len(hits))
    if ( tnow > t_bounds[iit_bonus] ):
        p = p * 2
        
    await chans[iichan_cmd].send("Beep Bop. Comment within the next 60 seconds if you would like to do so, or type 'x' to skip!")
    
    try:
        def same_user(msg):
            return msg.author.id == discord_id
        
        msg = await client.wait_for('message', timeout=60.0, check=same_user)
        
        if ( msg.content.lower() == 'x' ):
           cmt = ""
           
        else:
            cmt = msg.content
            
    except asyncio.TimeoutError:
        cmt = ""
        
    for ii in np.arange(len(ps)):
        ps[ii].point_change(tnow,p)
            
    h = Hit(tnow, ps, p, cmt, True)
    hits.append(h)      
    
    sstr = "Beep bop. Reported "
    for ii in np.arange(len(ps)):
        sstr += ps[ii].name + ", "
    sstr = sstr[0:(len(sstr)-2)] + " for " + str(p) + " point!"
    
    if ( cmt != "" ):
        sstr += "\nComment: " + cmt
    
    await chans[iichan_cmd].send(sstr, file=discord.File(img_pnt[p+2]))
    await chans[iichan_pnt].send(sstr+"\n\n"+progress_str(), file=discord.File(img_pnt[p+2]))
        

    await cue_reset_cmd()
    return 1
    
# async def get_rulebook():
#     await chans[iichan_cmd].send( \
#         "Beep beep. Here are the links for the rules.\n"+\
#         " Video: https://www.youtube.com/watch?v=PZMkieVQ7sE\n"+\
#         "Document: <https://docs.google.com/document/d/1xL8KjpuLV6iIMnEVUReq1Bf9AmxSlhGobNYjMAA4mKw/edit?usp=sharing>")
#     await cue_reset_cmd()
#     return 1
    
async def get_progress():
    await chans[iichan_cmd].send(progress_str())
    await cue_reset_cmd()
    
# async def get_credit():
#     await chans[iichan_cmd].send( \
#      "I'm a little tea-bot. Version D"+version_num+"\n "+\
#      "Last updated on "+last_update+"\n" +\
#      "\n" +\
#      "Stole the idea from Tom Scott <https://www.youtube.com/watch?v=QR9FwcwxTG4> \n\n" +\
#      "Developer: Chun-Yi Wu\n\n"+\
#      "With help from (in alphabetical order):\n    Andrew Vernon, Angel Roman, Antonio Roman, Lizzie Jouett, Jim Hall", file=discord.File('pics/credit.png'))
#     await cue_reset_cmd()
#     return 1
        
async def join_game(user):
    # get the current time
    tnow = get_current_time()
    
    # check how the player is joining the game
    alreadyInGame = False
    returnToGame = False   
    
    for ii in np.arange(len(players)):
        if players[ii].discord_id == user.id:
            alreadyInGame = True
            if ( not players[ii].is_in_game ):
                returnToGame = True
                p = players[ii] 
    
    # perform action accordingly
    if alreadyInGame:
        if returnToGame:
            await chans[iichan_cmd].send("Beep beep. Welcome back to the game, " +\
                                         p.name + "! As per the rule, adding two points adjustment to your score.")
            
            p.point_change(tnow, 2)
            
            h = Hit(tnow, [p], 2, p.name + " rejoining game", True)
            hits.append(h)
            
            p.is_in_game = True
            with open(fname_player,'a') as f:
                f.write("+, " + p.name + ", " + str(p.discord_id) + ", " + str(tnow) + ", 0\n")
                f.flush()
            
        else:
            await chans[iichan_cmd].send("Beep. I think you're already in the game?")
            
    else:
        p0 = 0
        
        if user.nick is None:
            name = user.name
        else:
            name = user.nick
                
        
        if ( tnow < t_bounds[1] ):
            p = Player(name,user.id,tnow,0, True)
        else:
            if len(players) == 0:
                p = Player(name,user.id,tnow,0, True)
            else:
                for ii in np.arange(len(players)):
                    p0 += players[ii].points[-1]
    
                p0 = (int)(np.floor(p0 / len(players)))
                p = Player(user.nick,user.id,tnow,p0, True)
            
        # add the player, and record it
        players.append(p)
        
        # send message 
        if p0 == 0:
            await chans[iichan_cmd].send( \
                "Beep beep. Welcome " + p.name + " to the game!" )
        else:
            await chans[iichan_cmd].send( \
                "Beep beep. Welcome " + p.name + " to the game! You're starting with " + str(p0) + " points!" )
        
        
    await cue_reset_cmd()
    return 1

async def quit_game(discord_id):
    # get the current time
    tnow = get_current_time()
    
    # grab the player index
    ind = find_player(discord_id)
    
    # perform actions accordingly
    if ( ind < 0 ):
        # the player never joined before
        await chans[iichan_cmd].send("Beep. You are not in the game?")
        await cue_reset_cmd()
    else:
        # the player joined before
        p = players[find_player(discord_id)]
        
        if ( p.is_in_game ):
            msg = await chans[iichan_cmd].send( \
                "--------------------------\n"+\
                "Beep beep. Are you sure, "+p.name+"? You can come back later in the game, but you'll get a two-point adjustment wehen you come back.\n" +\
                "\n" +\
                rxn_yes + " - Yes\n" +\
                rxn_no + " - No\n")
                
                
            await msg.add_reaction(rxn_yes)
            await msg.add_reaction(rxn_no)
            
            # wait for the response
            try:
                rxn, user = await client.wait_for('reaction_add', timeout=60.0, check=check_rxn_not_by_bot)
                
                if ( rxn.emoji == rxn_yes ):
                    msg = await chans[iichan_cmd].send("Beep beep. Sad to see you go... but hope to see you back later!\n")
                    # the player is actively playing the game
                    p.is_in_game = False
                        
                    with open(fname_player,'a') as f:
                        f.write("-, " + p.name + ", " + str(p.discord_id) + ", " + str(tnow) + ", 0\n")
                        f.flush()
                        
                    await cue_reset_cmd()
                    return
                    
                     
                elif ( rxn.emoji == rxn_no ):
                    msg = await chans[iichan_cmd].send("Beep beep. Glad to see you decided to stay!\n")
                    await cue_reset_cmd()
                    return
                    
                    
                
            except asyncio.TimeoutError:
                await chans[iichan_gam].send('Beep. You took too long! I''m going to assume you\'re staying?')
                time.sleep(5.0)
                await reset_cmd()
                return
                
            else:
                await chans[iichan_gam].send('Beep. Something went wrong?')
                time.sleep(5.0)
                await reset_cmd()
                return
            
            
        else:
            # the player already withdrew before
            await chans[iichan_cmd].send("Beep. You already left the game?")
            
    return 1
    
    
async def cue_reset_cmd():
    msg = await chans[iichan_cmd].send("Hit "+rxn_reset+" when you're done!")
    await msg.add_reaction(rxn_reset)
    return 1
    
    
# -----------------------------------------------------------------------------
# admin functions
# -----------------------------------------------------------------------------
    
    
    
    
    
# -----------------------------------------------------------------------------
# shadow realm functions
# -----------------------------------------------------------------------------
    
async def sr_list_user():
    for ii in np.arange(len(players)):
        p = players[ii]
        if p.is_in_game:
            await chans[iichan_sha].send(str(ii) + " " + p.to_string("shadow"))
        else:
            await chans[iichan_sha].send(str(ii) + " " + p.to_string("shadow") + " *withdrew*")
    await chans[iichan_sha].send("-> "+str(len(players))+' players found.')
    return 1
     

async def sr_list_user_ext():
    for ii in np.arange(len(players)):
        p = players[ii]
        if p.is_in_game:
            await chans[iichan_sha].send(str(ii) + " " + p.to_string("shadow"))
        else:
            await chans[iichan_sha].send(str(ii) + " " + p.to_string("shadow") + " *withdrew*")
            
        for jj in np.arange(len(p.times)):
            await chans[iichan_sha].send("____" + get_time_string(p.times[jj]) + ", " + str(p.points[jj]))
    await chans[iichan_sha].send("-> "+str(len(players))+' players found.')
    return 1


async def sr_list_hit():
    for ii in np.arange(len(hits)):
        h = hits[ii]
        await chans[iichan_sha].send(str(ii) + " " + h.to_string("shadow"))
    await chans[iichan_sha].send("-> "+str(len(hits))+' hit records found.')
    return 1
        

async def sr_list_link():
    for ii in np.arange(len(links)):
        l = links[ii]
        await chans[iichan_sha].send(str(ii) + " " + l.to_string("shadow"))
    await chans[iichan_sha].send("-> "+str(len(links))+' links found.')
    return 1


async def sr_list_mgr():
    for ii in np.arange(len(mg_results)):
        mgr = mg_results[ii]
        await chans[iichan_sha].send(str(ii) + " " + mgr.to_string("shadow"))
    await chans[iichan_sha].send("-> "+str(len(mg_results))+' hit records found.')
    return 1
        

async def sr_game_status():
    for ii in np.arange(5):
        await chans[iichan_sha].send(str(ii) + " - " + get_time_string(t_bounds[ii]) + ", " + str(phases_started[ii]))
    
    
async def sr_debug_msg(msg):
    await chans[iichan_sha].send(\
        "<@592523823471919144> Debug message:\n"+msg)
    return 1
    
    
    
# -----------------------------------------------------------------------------
# mini games functions
# -----------------------------------------------------------------------------

async def gam_rpsls():
    # rock paper scissors lizaard spock
    # # constants
    # dec_roc = 0
    # dec_pap = 1
    # dec_sci = 2
    # dec_liz = 3
    # dec_spk = 4
    
    #  emojis
    rxn_roc = "\u270A"
    rxn_pap = "\U0001f590"
    rxn_sci = "\u270C"
    rxn_liz = "\U0001f90f"
    rxn_spk = "\U0001f596"
    
    rxns = [rxn_roc, rxn_pap, rxn_sci, rxn_liz, rxn_spk]
    
    # result table (-1=lose, 0=draw, +1=win)
    result_table = np.zeros((5,5))
    result_table[0,1] = +1; result_table[1,0] = -1
    result_table[0,2] = -1; result_table[2,0] = +1
    result_table[0,3] = -1; result_table[3,0] = +1
    result_table[0,4] = +1; result_table[4,0] = -1
    result_table[1,2] = +1; result_table[2,1] = -1
    result_table[1,3] = +1; result_table[3,1] = -1
    result_table[1,4] = -1; result_table[4,1] = +1
    result_table[2,3] = -1; result_table[3,2] = +1
    result_table[2,4] = +1; result_table[4,2] = -1
    result_table[3,4] = -1; result_table[4,3] = +1
    
    
    # decide what the bot is going to play
    bot_gesture = int(np.floor(random.random()*5))
    
    # send the message to the channel
    msg = await chans[iichan_gam].send( \
        "Rock Paper Scissors Lizard Spock!", \
        file = discord.File('pics/rpsls.png'))
    
    await msg.add_reaction(rxn_roc)
    await msg.add_reaction(rxn_pap)
    await msg.add_reaction(rxn_sci)
    await msg.add_reaction(rxn_liz)
    await msg.add_reaction(rxn_spk)
    
    # get response from player
    try:
        rxn, user = await client.wait_for('reaction_add', timeout=60.0, check=check_rxn_not_by_bot)
        tnow = get_current_time()
        
        
        
        if rxn.emoji == rxn_roc:
            pla_gesture = 0
        elif rxn.emoji == rxn_pap:
            pla_gesture = 1
        elif rxn.emoji == rxn_sci:
            pla_gesture = 2
        elif rxn.emoji == rxn_liz:
            pla_gesture = 3
        elif rxn.emoji == rxn_spk:
            pla_gesture = 4
        else:
            await chans[iichan_gam].send("Um... that's not one of the options")
            await cue_reset_gam()
            return
            
        # print(rxn.emoji)
        # print(pla_gesture)
        
        result = result_table[bot_gesture][pla_gesture]
        
        await chans[iichan_gam].send(rxns[bot_gesture])
        
        if result == -1:
            await chans[iichan_gam].send("You lost!")
            ii_pl = find_player(user.id)
            if ii_pl < 0:
                await cue_reset_gam()
                return
            pl = players[ii_pl]
            mgr = MiniGameResult(tnow, [pl], -100, "lost RSPLP", True)
            pl.mgpoint_change(-100)
        elif result == 0:
            await chans[iichan_gam].send("It's a tie!")
            ii_pl = find_player(user.id)
            if ii_pl < 0:
                await cue_reset_gam()
                return
            pl = players[ii_pl]
            mgr = MiniGameResult(tnow, [pl], 0, "tied in RSPLP", True)
            pl.mgpoint_change(0)
        elif result == +1:
            await chans[iichan_gam].send("You won!")
            ii_pl = find_player(user.id)
            if ii_pl < 0:
                await cue_reset_gam()
                return
            pl = players[ii_pl]
            mgr = MiniGameResult(tnow, [pl], 100, "win RSPLP", True)
            pl.mgpoint_change(100)
            
        
        # if ( rxn.emoji == rxn_yes ):
        #     box_switched = True
             
        # elif ( rxn.emoji == rxn_no ):
        #     box_switched = False
            
        # else:
            
        
        # if ( (box_switched and bot_has_carrot) or (not box_switched and not bot_has_carrot) ):
        #     await chans[iichan_gam].send("Congratulations! You got the carrot!")
        #     ii_pl = find_player(user.id)
        #     if ii_pl < 0 :
        #         await cue_reset_gam()
        #         return
        #     pl = players[ii_pl]
        #     mgr = MiniGameResult(tnow,[pl],120,"won carrot",True)
        #     pl.mgpoint_change(120)
        # else:
        #     await chans[iichan_gam].send("Oopsie! I have the carrot \U0001F955! Better luck next time!")
        #     ii_pl = find_player(user.id)
        #     if ii_pl < 0 :
        #         await cue_reset_gam()
        #         return
        #     pl = players[ii_pl]
        #     mgr = MiniGameResult(tnow,[pl],-120,"lost carrot",True)
        #     pl.mgpoint_change(-120)
            
        mg_results.append(mgr)
        
        await cue_reset_gam()
        return
        
    except asyncio.TimeoutError:
        await chans[iichan_gam].send('You took too long! Call me again if you wanna play!')
        time.sleep(5.0)
        await reset_gam()
        return
        
    else:
        await chans[iichan_gam].send('Something went wrong?')
        time.sleep(5.0)
        await reset_gam()
        return
    
    
    
async def gam_carrot():
    # decide if the bot has the carrot
    bot_has_carrot = ( random.random() < 0.5 )
    
    
    # send the message to the channel
    await chans[iichan_gam].send( \
        "Welcome to \"Carrot in a Box\"!\n"+\
        "You have a box, I have a box. There is a carrot in one of these boxes.\n" +\
        "The aim of the game is to end up with the carrot.\n", file=discord.File('pics/carrot.png'))
    time.sleep(1.0)
    await chans[iichan_gam].send( \
        "You want the carrot, I want the carrot, but there is only one carrot. Let's play: Carrot in a Box.")
    time.sleep(1.0)
        
    # send the message about what's in the bot's box
    txt = 'I just looked inside my box, and '
    rand = random.random()
    if bot_has_carrot:
        if rand < 0.45:
            txt += msg_carrot_yes[random.randint(0,len(msg_carrot_yes)-1)]
        elif rand < 0.90:
            txt += msg_carrot_no[random.randint(0,len(msg_carrot_no)-1)]
        else:
            txt += msg_carrot_maybe[random.randint(0,len(msg_carrot_maybe)-1)]
    else:
        if rand < 0.45:
            txt += msg_carrot_no[random.randint(0,len(msg_carrot_no)-1)]
        elif rand < 0.90:
            txt += msg_carrot_yes[random.randint(0,len(msg_carrot_yes)-1)]
        else:
            txt += msg_carrot_maybe[random.randint(0,len(msg_carrot_maybe)-1)]
        
    await chans[iichan_gam].send(txt)
    time.sleep(1.0)
                
    # cue the switch message
    msg = await chans[iichan_gam].send( \
            "--------------------------\n"+\
            "Do you want to switch boxes with me?\n" +\
            "\n" +\
            rxn_yes + " - Yes\n" +\
            rxn_no + " - No\n")          
    await msg.add_reaction(rxn_yes)
    await msg.add_reaction(rxn_no)
    
    # wait for the response
    try:
        rxn, user = await client.wait_for('reaction_add', timeout=60.0, check=check_rxn_not_by_bot)
        tnow = get_current_time()
        
        if ( rxn.emoji == rxn_yes ):
            box_switched = True
             
        elif ( rxn.emoji == rxn_no ):
            box_switched = False
            
        else:
            await chans[iichan_gam].send("Um... that's not one of the options")
            await cue_reset_gam()
            return
            
        
        if ( (box_switched and bot_has_carrot) or (not box_switched and not bot_has_carrot) ):
            await chans[iichan_gam].send("Congratulations! You got the carrot!")
            ii_pl = find_player(user.id)
            if ii_pl < 0 :
                await cue_reset_gam()
                return
            pl = players[ii_pl]
            mgr = MiniGameResult(tnow,[pl],90,"won carrot",True)
            pl.mgpoint_change(90)
        else:
            await chans[iichan_gam].send("Oopsie! I have the carrot \U0001F955! Better luck next time!")
            ii_pl = find_player(user.id)
            if ii_pl < 0 :
                await cue_reset_gam()
                return
            pl = players[ii_pl]
            mgr = MiniGameResult(tnow,[pl],-90,"lost carrot",True)
            pl.mgpoint_change(-90)
            
        mg_results.append(mgr)
        
        await cue_reset_gam()
        return
        
    except asyncio.TimeoutError:
        await chans[iichan_gam].send('You took too long! I''m keeping both of the box now!')
        time.sleep(5.0)
        await reset_gam()
        return
        
    else:
        await chans[iichan_gam].send('Something went wrong?')
        time.sleep(5.0)
        await reset_gam()
        return
        
    
async def init_link():
    # decide if the video is going to be a hit or safe
    is_hit = random.random() < 0.5
    
    # read the appropriate file
    urls = []
    
    if is_hit:
        with open("database/links_hit.txt") as f:
            for ind, line in enumerate(f):    
                urls.append(line)
    else:
        with open("database/links_safe.txt") as f:
            for ind, line in enumerate(f):    
                urls.append(line)
    
    i_link = random.randint(0,len(urls)-1)
    url = urls[i_link]
    url = url[0:len(url)-1]
    
    t_issue = get_current_time()
    if debugMode == 0:
        # t_resolve = np.ceil((t_issue-43200)/86400)*86400+43200+t_adjust_disp
        tnow = datetime.datetime.now()
        t_resolve = get_time(tnow.year, tnow.month, tnow.day+1, 12,0,0,t_adjust)
        print(t_resolve)
    elif debugMode == 1:
        t_resolve = np.ceil(t_issue/3600)*3600
    
    msg = await chans[iichan_rsk].send( \
            "**Beep beep. Risky link of the day!**\n\n" +\
            "<" + url + ">\n\n" + \
            "Time to resolve: " + get_time_string(t_resolve-t_adjust_disp) + "\n\n" + \
            "React with \u2705 if you watched the video!\n" +\
            rxn_link_safe + " means this link is resolved, and the video is safe.\n"+\
            rxn_link_hit+" means this link is resolved, and the video is a trap."   )
    await msg.add_reaction("\u2705")
        
    link = Link(url, is_hit, t_issue, t_resolve, msg.id, True)
    links.append(link)
    

async def give_trivia():
    trivia = []
    with open("database/trivia.txt", encoding='utf-8') as f:
        for ind, line in enumerate(f):
            trivia.append(line)
    
    await chans[iichan_gam].send(\
        "Beep bop. Did you know....\n" +\
        trivia[random.randint(0,len(trivia)-1)] )
    await cue_reset_gam()
    
    
    
async def cue_reset_gam():
    msg = await chans[iichan_gam].send("Hit "+rxn_reset+" when you're done!")
    await msg.add_reaction(rxn_reset)
    
    
    
    
    
    
# -----------------------------------------------------------------------------
# scheduler functions
# -----------------------------------------------------------------------------
 
async def changeofday():
    time.sleep(1.0)
    tnow = get_current_time()
        
    # to do:
    
    # - detect if the game is onto the next phase
    if ( tnow > t_bounds[iit_warn] and not phases_started[iit_warn] ):
        phases_started[iit_warn] = True
        await phase_warn_of_start()
        
    elif ( tnow > t_bounds[iit_start] and not phases_started[iit_start] ):
        phases_started[iit_start] = True
        await phase_game_start()
        
    elif ( tnow > t_bounds[iit_bonus] and not phases_started[iit_bonus] ):
        phases_started[iit_bonus] = True
        await phase_game_bonus()
        
    elif ( tnow > t_bounds[iit_5vids] and not phases_started[iit_5vids] ):
        phases_started[iit_5vids] = True
        await phase_bot_5vids()
        
    elif ( tnow > t_bounds[iit_end] and not phases_started[iit_end] ):
        phases_started[iit_end] = True
        await phase_game_end()
        
    elif ( tnow > t_bounds[iit_quit] and not phases_started[iit_quit] ):
        phases_started[iit_quit] = True
        await phase_bot_quit()
        
        
    # - resolve videos, if applicable
    for ii in np.arange(len(links)):
        if ( tnow > links[ii].t_resolve and not links[ii].has_resolved ):
            await links[ii].resolve()
    
    # - put out new videos 
    if tnow < t_bounds[iit_start]:
        print('game hasnt started yet, so no video yet')
    elif tnow < t_bounds[iit_5vids]:
        await init_link()
        
    elif ( tnow < t_bounds[iit_end] ):
        await init_link()
        await init_link()
        await init_link()
        await init_link()
        await init_link()
            
    
async def phase_warn_of_start():
    await chans[iichan_ann].send("Beep beep. Game starts in 24 hours! Remember to join the game if you haven't!", file=discord.File('pics/warn.png'))
    
async def phase_game_start():
    await chans[iichan_ann].send("Beep beep. The game has started!", file=discord.File('pics/start.png'))
    
async def phase_game_bonus():
    await chans[iichan_ann].send("Beep beep. Mariah Carey Merry Christmas Bonus Period starts now!", file=discord.File('pics/bonus.png'))
    
async def phase_bot_5vids():
    await chans[iichan_ann].send("Beep beep. Last chance to catch up! Five risky links are out today!", file=discord.File('pics/5vids.png'))
    
async def phase_game_end():
    # - resolve all unresolved videos, if applicable
    for ii in np.arange(len(links)):
        if ( not links[ii].has_resolved ):
            await links[ii].resolve()
            
    await chans[iichan_ann].send("Beep beep. The game has ended!", file=discord.File('pics/end.jpg'))
    
    # final result    
    text = "__**Final result**__\n" + progress_str() + "\n"
    
    # determine winners and losers
    points = []
    for ii in np.arange(len(players)):
        points.append(max(0,players[ii].points[-1]))

    p_max = max(points)
    p_min = min(points)
    strL = ""
    strW = ""
    for ii in np.arange(len(players)):
        if players[ii].points[-1] == p_max:
            strL += ", " + players[ii].name
        elif players[ii].points[-1] == p_min:
            strW += ", " + players[ii].name

    text += strL[3:] + " lost, and " + strW[3:] + " won!\n"
    text += "Difference in points: " + str(int(p_max-p_min)) + "\n\n"
    text += "Congratulations to the winner(s)!\n"
    await chans[iichan_ann].send(text)
    
    # get stats on the game
    # most video clicks
    clicks = [0]*len(players)
    for ii in np.arange(len(links)):
        link = links[ii]
        msg = await chans[iichan_rsk].fetch_message(link.msg_id)
        rxns = msg.reactions
        
        ps = []
        
        for ii in np.arange(len(rxns)):
            async for user in rxns[ii].users():
                if not user.bot:
                    ind = find_player(user.id)
                    ps.append(players[ind])
        
        for jj in np.arange(len(ps)):
            clicks[find_player(ps[jj].discord_id)] += 1
            
    cmax = max(clicks)
    strCmax = ""
    for ii in np.arange(len(players)):
        if clicks[ii] == cmax:
            strCmax += ", " + players[ii].name
                
    # mini game 
    mgpoints = []
    for ii in np.arange(len(players)):
        mgpoints.append(players[ii].points_mg)
    

    mmax = max(mgpoints)
    mmin = min(mgpoints)
    strMmin = ""
    strMmax = ""
    for ii in np.arange(len(players)):
        if players[ii].points_mg == mmax:
            strMmax += ", " + players[ii].name
        elif players[ii].points_mg == mmin:
            strMmin += ", " + players[ii].name
    
    await chans[iichan_ann].send(\
        "\n__**Some other stats for the game**__\n"+\
        "*Most links clicked*: " + strCmax[3:] + " ("+str(cmax)+")\n" +\
        "*Mini game losers*: " + strMmin[3:] + " ("+str(mmin)+")\n" +\
        "*Mini game winners*: " + strMmax[3:] + " ("+str(mmax)+")\n")
    
async def phase_bot_quit():
    await chans[iichan_ann].send("Beep beep. I'm going to bed now. See you next year!", file=discord.File('pics/quit.png'))
    quit()

    
    
    
    
# =============================================================================
# bot interaction functions
# =============================================================================
             
@client.event
async def on_connect():
    print('bot connected to discord')
    
    
@client.event
async def on_ready():
    print('on_ready triggered')
    await get_channels()
    
    await load_game()
    
    await init_link()
        
    await chans[iichan_sha].send("Bot back online.")
        
    await reset_cmd()
    await reset_gam()

@client.event
async def on_message(msg): 
    # ignore any reaction by bot
    if msg.author.id == id_teabot:
        return
            
    if msg.channel == chans[iichan_sha]:
        if msg.content.lower() == 'list command':
            await chans[iichan_sha].send(\
                "list player\n" +\
                "list player ext\n" +\
                "list hit\n" +\
                "list link\n" +\
                "list minigame\n"
                "game phase\n" +\
                "show progress\n" +\
                "reset command\n" +\
                "reset minigames\n" +\
                "reset info\n"+\
                "reload game\n" +\
                "purge rsk\n"+\
                "purge ann\n"+\
                "purge pnt\n"+\
                "purge sha\n"+\
                "resolve link #\n" +\
                "debug make link\n"+\
                "debug resolve all links\n" +\
                "howdy\n"+\
                "")
        
        if msg.content.lower() == "list player":
            await sr_list_user()
            
        if msg.content.lower() == "list player ext":
            await sr_list_user_ext()
            
        if msg.content.lower() == "list hit":
            await sr_list_hit()
            
        if msg.content.lower() == "list link":
            await sr_list_link()
            
        if msg.content.lower() == "list minigame":
            await sr_list_mgr()
            
        if msg.content.lower() == 'game phase':
            await sr_game_status()
            
        if msg.content.lower() == 'show progress':
            await chans[iichan_sha].send(progress_str())
            
            
        if msg.content.lower() == 'reset command':
            await reset_cmd()
            
        if msg.content.lower() == 'reset minigames':
            await reset_gam()
            
        if msg.content.lower() == 'reset info':
            await reset_inf()
            
        if msg.content.lower() == 'reload game':
            await load_game()
                  
            await sr_list_user()
            await sr_list_hit()
            await sr_list_link()
         
            
        if msg.content.lower() == 'purge rsk':
            await chans[iichan_rsk].purge()
            
        if msg.content.lower() == 'purge ann':
            await chans[iichan_ann].purge()
            
        if msg.content.lower() == 'purge pnt':
            await chans[iichan_pnt].purge()
            
        if msg.content.lower() == 'purge sha':
            await chans[iichan_sha].purge()
            
            
        if msg.content.lower().startswith('resolve link '):
            ind = int(msg.content[13:])
            link = links[ind]
            await link.resolve()
            
        if msg.content.lower() == 'debug make link':
            await init_link()
             
        if msg.content.lower() == 'debug resolve all links':
            for ii in np.arange(len(links)):
                if links[ii].has_resolved:
                    await links[ii].resolve()
            
            
        if msg.content.lower() == 'howdy':
            await chans[iichan_sha].send('howdy pardner')
            
            
            
        if ( "middayalert" in msg.content ):
            await changeofday()
            
        if ( "hourlyalert" in msg.content and debugMode == 1 ):
            await changeofday()
            
            

@client.event
async def on_reaction_add(rxn, user):
    
    # ignore any reaction by bot
    if user.bot:
        return
    
    
    if rxn.message.channel == chans[iichan_cmd]:
        await chans[iichan_cmd].send("==========================")
        
        if isinstance(rxn.emoji, str):
            if ( rxn.emoji == rxn_progress ):
                await chans[iichan_sha].send(user.name+"; progress")
                await get_progress()
                
            # elif ( rxn.emoji == rxn_credit ):
            #     await chans[iichan_sha].send(user.name+"; credit")
            #     await get_credit()
                
            elif ( rxn.emoji == rxn_reset ):
                await chans[iichan_sha].send(user.name+"; reset command")
                await reset_cmd()
                
            elif ( rxn.emoji == rxn_join ):
                await chans[iichan_sha].send(user.name+"; join")
                await join_game(user)
                
            elif ( rxn.emoji == rxn_withdraw ):
                await chans[iichan_sha].send(user.name+"; quit")
                await quit_game(user.id)
                
            else:
                print(rxn.emoji)
                
        else:
            if ( rxn.emoji.name == 'mc_album' ):
                await chans[iichan_sha].send(user.name+"; report self")
                await report_self(user.id)
                
            elif ( rxn.emoji.name == 'mc_divacup' ):
                await chans[iichan_sha].send(user.name+"; report multiple")
                await report_group(user.id)
                
            else:
                print(rxn.emoji)
            
        
    if rxn.message.channel == chans[iichan_gam]:
        if isinstance(rxn.emoji, str):
            if ( rxn.emoji == rxn_carrot ):
                await chans[iichan_sha].send(user.name+"; carrot")
                await gam_carrot()
                
            if ( rxn.emoji == rxn_rpsls ):
                await chans[iichan_sha].send(user.name+"; rspls")
                await gam_rpsls()
            
            elif rxn.emoji == rxn_trivia:
                await chans[iichan_sha].send(user.name+"; trivia")
                await give_trivia()
            
                
            elif ( rxn.emoji == rxn_reset ):
                await chans[iichan_sha].send(user.name+"; reset game")
                await reset_gam()
                
      
    

print('client.run() called')
client.run(TOKEN)
    
# =============================================================================
# BOT GRAMMAR!
# =============================================================================
# beep - error
# beep bop - point related things
# beep beep - announcement
# =============================================================================
