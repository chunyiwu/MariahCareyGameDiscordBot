# Mariah Carey Game Bot

This is a bot written to manage the "All I Want for Christmas is not hearing
'All I wantfor Christmas is You'" game. 

Version 2.3, Last updated on November 4, 2022

Code available on [GitHub](https://github.com/chunyiwu/MariahCareyGameDiscordBot)

Developed by Chun-Yi Wu, with help from:
* Andrew Thompson: *Bg, Bd, R, L, T*
* Lizzie Jouett: *Bg, Bd, R, L, T*
* Antonio Roman: *Bd, R, L, V*
* Angel Roman: *Bd, L, I*
* Jim Hall: *L*

__Legend__
* *Bg* - GroupMe Beta Tester
* *Bd* - Discord Best Tester
* *R* - Rule Developers
* *L* - Link Contributors
* *T* - Trivia Contributors
* *V* - Video Contributors
* *I* - Image Contributors

# Instruction 
To set up the environment to run this bot, do the following steps:

**Step 1: Set up Discord Developer Portal**

- Go to the Discord Developer Portal, and follow the instructions from 
    [this website](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/)
- Grab the bot token from the DDP


**Step 2: Set up Python environment**

- If python is not already on the machine, install python from 
    [Python](https://www.python.org/downloads/)
    
- Install the following packages using the installer applicable for the OS:

    * `asyncio`
    * `discord`
    * `python-dotenv`
    * `numpy`
    
- Create a file named ".env", and enter the following:

    ```
    # .env
    DISCORD_TOKEN = [token]    
    DISCORD_GUILD = [server name]
    ```

**Step 3: Set up the Discord server**
The server should have the following channels:
* information
* announcements
* point-changes
* commands
* risky-click
* voting
* admin-corner
* shadow-realm
* mini-games
* chit-chat

In addition, invite the Automatebot <https://automatebot.app/board> to the server, and set up an alert everyday at noon to send the message "middayalert" to #shadow-realm. This is what drives the time-related triggers for the bot.

**Step 4: Run the code!**

- Exectue the code using the command applicable for the OS.
  (On Google Cloud, use "nohup python3 XmasGameBot_Discord.py y &")

# Update logs 
* **v3.0** (Nov 4, 2022)
    * Fixed the bug for showing result
    * Added more links to the risky click game

* **v2.2** (Jun 20, 2021)
    * Added Rock Paper Scissors Lizard Spock as a minigame
    * Adjusted points for the minigame so that the score risk is the same for different games
    
* **v2.1.2** (Jun 18, 2021)
    * Removed undesired shadow realm commands
    * Shows the progress when reporting a point change
    * Added the ability to abort a self report
    * Added showing progress in the shadow realm for debug purpose
    * Made changes to the info channel in accordance to the rule changes
    
* **v2.1.1** (Jun 14, 2021)
    * Initial commit to GitHub
    * The preview now shows up after the risky link is resolved
    * Rearranged the directory for decluttering
    * Updated the trivia and link database
    
* **v2.1** (Jan 04, 2021)
    * Counting everyone who has 0 or negative points as 0 at the final result
    * Adjusted the game time to end on 12/25 instead of 12/26
    * The game progress is now always shown with a score update
    * Removed the progress and credit reaction from the reaction commands
    * Bug fixed: The last 5 videos are not resovled before the end of game
        
* **v2.0** (Oct 02, 2020)
    * Discord bot is ready for actual game
    
* **v1.9** (May 26, 2020)
    * Converted to running on Discord instead of GroupMe

* **v1.0.1** (Nov 03, 2019)
    * Added penalty for using the unhit
    
* **v1.0** (Oct 01, 2019)
    * Finished a full scale testing
    
* **v0.6.2** (Jul 15, 2019)
    * Added the command to remove points, can only be used by Chun
    * Added new starting picture
    
* **v0.6.1** (Jul 13, 2019)
    * The links now have risk level associated with them, according to if they are traps, related videos, or un-related random vidoes
    * Allow more than one world domination phrases for thr trivia.
    
* **v0.6** (Jul 11, 2019)
    * The bot will now have a 5% chance of trying to take over the world when being asked to provide a trivia or a link
    * Updated the pictures 
    * Now an exception catch-all 

* **v0.5.4** (Jul 09, 2019)
    * Added the daily update + risky link

* **v0.5.3** (Jul 06, 2019)
    * Modified how youtube links are handled to reflect the new file format

* **v0.5.2** (Dec 29, 2018)
    * Separate the credit to a different command
    * Allow user to specify which misc to see

* **v0.5.1** (Dec 28, 2018)
    * Bug fixes

* **v0.5** (Dec 26, 2018)
    * Re-organized the trivia and links from misc to allow changes mid-game
    * Added game status to the progress
    * Allows reporting hits to multiple people
    * Allows user to undo the last point update
    * Make the misc options come out at different probability
    * Added detailed help for each command

* **v0.4** (Dec 23, 2018)
    * Added safe guard for repeated joining
    * Allows user to identify player with just the beginning of the name, and added safeguard for ambiguity
    * Added the "lucky" command for fun
    * Progress also shows time since start of game, remaining time in game
    * Fixed bug where people joining before the game starts will get the average of the score

* **v0.3** (Dec 22, 2018)
    * Rewrote the way commands are handled to allow more options
    * Allows user to join the game through command, rather through manual entry
    * Allows user to give points to other player, in case the other player didn't report a hit

# Future Updates 
* **Minigame:** Memes
* **Minigame:** Trivia quiz
* **Admin:** Adding automated voting generation
    
