"""
Simple 2d world where the player can interact with the items in the world.
"""

__author__ = "Daniel McKeown, 45919505"
__date__ = ""
__version__ = "1.1.0"
__copyright__ = "The University of Queensland, 2019"

import math
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import time

from typing import Tuple, List

import pymunk

from game.block import Block, MysteryBlock
from game.entity import Entity, BoundaryWall
from game.mob import Mob, CloudMob, Fireball
from game.item import DroppedItem, Coin
from game.view import GameView, ViewRenderer
from game.world import World
from game.util import get_collision_direction

from level import load_world, WorldBuilder
from player import Player

BLOCK_SIZE = 2 ** 4
MAX_WINDOW_SIZE = (1080, math.inf)

GOAL_SIZES = {
    "flag": (0.2, 9),
    "tunnel": (2, 2)
}

BLOCKS = {
    '#': 'brick',
    '%': 'brick_base',
    '?': 'mystery_empty',
    '$': 'mystery_coin',
    '^': 'cube',
    'b': 'bouncyboi',
    'I': 'flagpole',
    '=': 'tunnel',
    'S': 'switch'
}

ITEMS = {
    'C': 'coin',
    '*': 'star'
}

MOBS = {
    '&': "cloud",
    '@': "mushroom"
}





def read_config_file():
    """ Reads the configuration file provided by the player in the dialog window and configures the game as appropriate to
        the specifications of the config file

        Returns: config (dict): Nested dictionary of the player's desired configuration
    """
    filename = filedialog.askopenfilename()
        
    config_file = open(filename, 'r')

    config = {}

    heading = None

    for line in config_file:

        line = line.strip()

        if line.startswith('=') and line.endswith('='):

            heading = line[1:-1]

            config[heading] = {}

        elif line.count(':') == 1 and heading is not None:

            name, value = line.split(':')

            config[heading][name.strip()] = value.strip()


    config_file.close()
        
    return config


    
    

    


def create_block(world: World, block_id: str, x: int, y: int, *args):
    """Create a new block instance and add it to the world based on the block_id.

    Parameters:
        world (World): The world where the block should be added to.
        block_id (str): The block identifier of the block to create.
        x (int): The x coordinate of the block.
        y (int): The y coordinate of the block.
    """
    block_id = BLOCKS[block_id]
    if block_id == "mystery_empty":
        block = MysteryBlock()
    elif block_id == "mystery_coin":
        block = MysteryBlock(drop="coin", drop_range=(3, 6))
    elif block_id == 'bouncyboi':
        block = BounceBlock()
    elif block_id == 'switch':
        block = Switch()
    elif block_id == 'flagpole':
        block = GoalsFlag()
    else:
        block = Block(block_id)

    world.add_block(block, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_item(world: World, item_id: str, x: int, y: int, *args):
    """Create a new item instance and add it to the world based on the item_id.

    Parameters:
        world (World): The world where the item should be added to.
        item_id (str): The item identifier of the item to create.
        x (int): The x coordinate of the item.
        y (int): The y coordinate of the item.
    """
    item_id = ITEMS[item_id]
    if item_id == "coin":
        item = Coin()
    elif item_id == 'star':
        item = Star()
    else:
        item = DroppedItem(item_id)

    world.add_item(item, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_mob(world: World, mob_id: str, x: int, y: int, *args):
    """Create a new mob instance and add it to the world based on the mob_id.

    Parameters:
        world (World): The world where the mob should be added to.
        mob_id (str): The mob identifier of the mob to create.
        x (int): The x coordinate of the mob.
        y (int): The y coordinate of the mob.
    """
    mob_id = MOBS[mob_id]
    if mob_id == "cloud":
        mob = CloudMob()
    elif mob_id == "fireball":
        mob = Fireball()
    elif mob_id == 'mushroom':
        mob = MushroomMob()
    
    else:
        mob = Mob(mob_id, size=(1, 1))

    world.add_mob(mob, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_unknown(world: World, entity_id: str, x: int, y: int, *args):
    """Create an unknown entity."""
    world.add_thing(Entity(), x * BLOCK_SIZE, y * BLOCK_SIZE,
                    size=(BLOCK_SIZE, BLOCK_SIZE))


BLOCK_IMAGES = {
    "brick": "brick",
    "brick_base": "brick_base",
    "cube": "cube",
    'bouncyboi' : 'bounce_block',
    'flagpole' : 'flag',
    'tunnel' : 'tunnel',
    'switch' : 'switch',
    'switchpressed' : 'switch_pressed'
}

ITEM_IMAGES = {
    "coin": "coin_item",
    'star': 'star'
}

MOB_IMAGES = {
    "cloud": "floaty",
    "fireball": "fireball_down",
    'mushroom': 'mushroom'
    
}

PHYSICAL_THING_CATEGORIES = {
    "wall": 2 ** 1,
    "block": 2 ** 2,
    "player": 2 ** 3,
    "item": 2 ** 4,
    "mob": 2 ** 5
}



class Switch(Block):
    """ A switch block that is inactivated for 10 seconds when pressed and then returns to non-pressed state
        removes all bricks in the surrounding area during this 10 second period
    """

    _id = 'switch'

    def __init__(self):
        """ Construct a new switch block that is currently active

        """
        super().__init__()
        self._active = True
        self.start = time.time()
        

    def get_position(self):
        """ Identifies the X, Y position of the switch block in the world

        Returns:
            tuple(str): The X, Y position of the block
        """
        x, y = self.get_shape().bb.center()
        return x, y

    def on_hit(self, event, data):
        """ Callback collision with player event handler, sets the block to be inactive if collided via the top
            of the block and removes the blocks surrounding the switch
        """

        world, player = data

        if get_collision_direction(player, self) != 'A':
            return


        x, y = self.get_position()
        
        

        thing_categories = PHYSICAL_THING_CATEGORIES
        self._thing_categories = thing_categories

        self._space = pymunk.Space()

        


        if self._active:
            self._active = False
            self.start = time.time()


                

    def is_active(self):
        """(bool): Returns true if the block has not yet been pressed, else false

        """
        return self._active

    def check_time(self):
        """ Checks the time since the switch has been pressed and changes the block to be active
            after 10 seconds
        """
        if self._active == False:
            if time.time() - self.start >= 10:
                self._active = True

    def step(self, time_delta, game_data):
        """ Repeating step function that continously updates and checks for the passage of 10 seconds
            for the switch
        """
        self.check_time()


        

class MarioViewRenderer(ViewRenderer):
    """A customised view renderer for a game of mario."""

    @ViewRenderer.draw.register(Player)
    def _draw_player(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:

        
        if shape.body.velocity.x >= 0:
            image = self.load_image("mario_right")
        else:
            image = self.load_image("mario_left")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="player")]


    @ViewRenderer.draw.register(MysteryBlock)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.is_active():
            image = self.load_image("coin")
        else:
            image = self.load_image("coin_used")


        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]
    
    @ViewRenderer.draw.register(Switch)
    def _draw_switch(self, instance: Switch, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.is_active():
            image = self.load_image('switch')
        else:
            image = self.load_image('switch_pressed')
            
            

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]


class MarioApp:
    """High-level app class for Mario, a 2d platformer"""

    _world: World
    

    def __init__(self, master):
        """Construct a new game of a MarioApp game.

        Parameters:
            master (tk.Tk): tkinter root widget
        """

        self._master = master
        self._master.title('Mario')
        master.update_idletasks()
        config = read_config_file()
        self._config = config
        self._player = Player(max_health=20)


        gravity_amount = config['=World=']['gravity']
        self.current_level = config['=World=']['start']
        player_name = self._config['=Player=']['character']
        self._shape = pymunk.Shape
        self.x = self._config['=Player=']['x']
        self.y = self._config['=Player=']['y']


        world_builder = WorldBuilder(BLOCK_SIZE, gravity=(0, int(gravity_amount)), fallback=create_unknown)
        world_builder.register_builders(BLOCKS.keys(), create_block)
        world_builder.register_builders(ITEMS.keys(), create_item)
        world_builder.register_builders(MOBS.keys(), create_mob)
        self._builder = world_builder


        self.reset_world(self.current_level)

        self._player_invincible = False

        self._renderer = MarioViewRenderer(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES)

        size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
        self.size = size
        self._view = GameView(master, size, self._renderer)
        self._view.pack()

        self.bind()

        menubar = tk.Menu(self._master)
        self._master.config(menu = menubar)

        filemenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label = 'File', menu = filemenu)
        filemenu.add_command(label = 'Load Level',
                             command = self.load_level)
        filemenu.add_command(label = 'Reset Level',
                             command = self.reset_level)
        filemenu.add_command(label = 'Highscores',
                             command = self.highscores)
        filemenu.add_command(label = 'Exit', command = self.quit)

        
        StatusDisplay.__init__(self, master)
        StatusDisplay.background(self)
        
        StatusDisplay.healthbar_colour(self)
        StatusDisplay.score(self)

        
        # Wait for window to update before continuing
        master.update_idletasks()
        self.step()


    def get_player(self):
        """(str): Returns the player added to the game

        """
        return self._player

    def player_invincible(self):
        """ Checks if the player is invincible and if so will begin a timer for the star item

        """
        self._start_invincible = time.time()

        if self._player_invincible == True:
            self._start_invincible = time.time()

    def check_invincible(self):
        """ Checks if 10 seconds has passed since the player was made invincible, if so, the player
            is no longer invincible and the healthbar is updated to reflect the loss of the star item
            i.e. goes back from yellow to the colour it was before
        """
        if self._player_invincible == True:
            if time.time() - self._start_invincible >= 10:
                self._player_invincible = False
                StatusDisplay.clear_frame(self)
                StatusDisplay.healthbar_colour(self)
            
    def reset_world(self, new_level):
        """ Resets the current world with the level file specified

        Paramaters: new_level (str): The string name of the txt level file to open
        """
        self._world = load_world(self._builder, new_level)
        self._world.add_player(self._player, BLOCK_SIZE, BLOCK_SIZE)
        
        self._builder.clear()
        self._player.reset_score()

        self._setup_collision_handlers()

    def load_level(self):
        """ Loads the level specified by the player when the dialog box opens

        """
        self.current_level = filedialog.askopenfilename()
        self.reset_world(self.current_level)

    def reset_level(self):
        """ Resets the current level to restart itself and resets the player's health and score as if the player
            just opened the game
        """
        self.reset_world(self.current_level)
        self._player._health = self._player.get_max_health()
        
        StatusDisplay.new_score(self)
        StatusDisplay.score(self)
        
        StatusDisplay.clear_frame(self)
        StatusDisplay.healthbar_colour(self)
    
    def quit(self):
        """ Exits the progam
        """
        self._master.destroy()

    def retry(self):
        """ When the player runs out of health, this dialog box checks if the player wants to reset the level or
            quit the program
        """
        if self._player.get_health() == 0.0:
            query = messagebox.askquestion('You Died', 'Would you like to retry the level?')
            
            if query == 'yes':
                MarioApp.reset_level(self)
                
            elif query == 'no':
                MarioApp.quit(self)

    def highscores(self):
        """ Reads the highscores of the game and presents them in a tk.Toplevel window labeled appropriately

        """
        scores = tk.Toplevel()
        scores.title('Highscores')

        top_10 = open('highscores.txt', 'r')
        top = top_10.read()
        
        score_list = tk.Message(scores, text=top)
        score_list.pack()

        button = tk.Button(scores, text='Close', command=scores.destroy)
        button.pack()
            

    def bind(self):
        """Bind all the keyboard events to their event handlers."""
        
        self._master.bind('<w>', self._jump)
        self._master.bind('<Up>', self._jump)
        self._master.bind('<space>', self._jump)
        
        self._master.bind('<d>', self._move)
        self._master.bind('<Right>', self._move)
        
        self._master.bind('<a>', self._move)
        self._master.bind('<Left>', self._move)

        self._master.bind('<s>', self._duck)
        self._master.bind('<Down>', self._duck)
        
        

    def redraw(self):
        """Redraw all the entities in the game canvas."""
        
        self._view.delete(tk.ALL)

        self._view.draw_entities(self._world.get_all_things())
        

    def scroll(self):
        """Scroll the view along with the player in the center unless
        they are near the left or right boundaries
        """
        x_position = self._player.get_position()[0]
        half_screen = self._master.winfo_width() / 2
        world_size = self._world.get_pixel_size()[0] - half_screen

        # Left side
        if x_position <= half_screen:
            self._view.set_offset((0, 0))

        # Between left and right sides
        elif half_screen <= x_position <= world_size:
            self._view.set_offset((half_screen - x_position, 0))

        # Right side
        elif x_position >= world_size:
            self._view.set_offset((half_screen - world_size, 0))

    def step(self):
        """Step the world physics and redraw the canvas."""
        
        data = (self._world, self._player)
        self._world.step(data)

        self.scroll()
        self.redraw()
        
        self.check_invincible()

        self._master.after(10, self.step)

    def _move(self, dx, dy=0):
        """ Moves the player in the direction bound to the key by changing their velocity

            Parameters: dx (tuple): The game data arising from a keypress
                        dy (int): The default Y value of the move function, set to standard value as not utilised in function
        """
        if dx.keysym == 'd':
            self._player.set_velocity((500, 10))

        if dx.keysym == 'Right':
            self._player.set_velocity((75, 10))
            
        if dx.keysym == 'a':
            self._player.set_velocity((-75, 10))

        if dx.keysym == 'Left':
            self._player.set_velocity((-75, 10))

        self.is_ducking = False
                 
    def _jump(self, event):
        """ Checks if the player is already jumping, and if not the player jumps by alteration of their Y velocity

            Paramters: event (tuple): The keypress event data of the keys bound to jump, unused in this function
        """
        if self._player.is_jumping() == False:
            self._player.set_velocity((0,-210))
            self._player.set_jumping(True)
            
        self.is_ducking = False

    def _duck(self, event):
        """ Sets the player as ducking to True and quickens their fall, required for entry into tunnels

            Parameters: event (tuple): The keypress event data of the keys bound to duck, unused in the function

        """
        self._player.set_velocity((0, 150))
        self.is_ducking = True

    def _setup_collision_handlers(self):
        self._world.add_collision_handler("player", "item", on_begin=self._handle_player_collide_item)
        self._world.add_collision_handler("player", "block", on_begin=self._handle_player_collide_block,
                                          on_separate=self._handle_player_separate_block)
        self._world.add_collision_handler("player", "mob", on_begin=self._handle_player_collide_mob)
        self._world.add_collision_handler("mob", "block", on_begin=self._handle_mob_collide_block)
        self._world.add_collision_handler("mob", "mob", on_begin=self._handle_mob_collide_mob)
        self._world.add_collision_handler("mob", "item", on_begin=self._handle_mob_collide_item)

    def _handle_mob_collide_block(self, mob: Mob, block: Block, data,
                                  arbiter: pymunk.Arbiter) -> bool:
        if mob.get_id() == "fireball":
            if block.get_id() == "brick":
                self._world.remove_block(block)
                
            self._world.remove_mob(mob)

        if get_collision_direction(mob, block) == 'L':
                mob.set_tempo(-35)

        if get_collision_direction(mob, block) == 'R':
                mob.set_tempo(35)
      
        return True

    def _handle_mob_collide_item(self, mob: Mob, block: Block, data,
                                 arbiter: pymunk.Arbiter) -> bool:
        return False

    def _handle_mob_collide_mob(self, mob1: Mob, mob2: Mob, data,
                                arbiter: pymunk.Arbiter) -> bool:
        
        if mob1.get_id() == "fireball" or mob2.get_id() == "fireball":
            self._world.remove_mob(mob1)
            self._world.remove_mob(mob2)

        if mob1.get_id() == 'mushroom' or mob2.get_id() == 'mushroom':

            if get_collision_direction(mob1, mob2) == 'L':
                mob1.set_tempo(-35)

            if get_collision_direction(mob1, mob2) == 'R':
                mob1.set_tempo(35)
                
            if get_collision_direction(mob2, mob1) == 'L':
                mob2.set_tempo(-35)

            if get_collision_direction(mob2, mob1) == 'R':
                mob2.set_tempo(35)

        return False

    def _handle_player_collide_item(self, player: Player, dropped_item: DroppedItem,
                                    data, arbiter: pymunk.Arbiter) -> bool:
        """Callback to handle collision between the player and a (dropped) item. If the player has sufficient space in
        their to pick up the item, the item will be removed from the game world.

        Parameters:
            player (Player): The player that was involved in the collision
            dropped_item (DroppedItem): The (dropped) item that the player collided with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      (see http://www.pymunk.org/en/latest/pymunk.html#pymunk.Arbiter)
                                      NOTE: you probably won't need this
        Return:
             bool: False (always ignore this type of collision)
                   (more generally, collision callbacks return True iff the collision should be considered valid; i.e.
                   returning False makes the world ignore the collision)
        """

        dropped_item.collect(self._player)
        self._world.remove_item(dropped_item)
        
        StatusDisplay.new_score(self)
        StatusDisplay.score(self)

        if dropped_item.get_id() == 'star':
            Star.collect(self, player)
            MarioApp.player_invincible(self)
            
            StatusDisplay.clear_frame(self)
            StatusDisplay.healthbar_colour(self)


        return False

    def _handle_player_collide_block(self, player: Player, block: Block, data,
                                     arbiter: pymunk.Arbiter) -> bool:
        """Callback to handle collision between the player and a block in the world

        Parameters:
            player (Player): The player that was involved in the collision
            block (Block): The block in the world the player collides with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      
        Return:
             bool: True (always process this type of collision)

        """ 

        block.on_hit(arbiter, (self._world, player))
        
        if get_collision_direction(self._player, block) == 'A':
            self._player.set_jumping(False)

        if block.get_id() == 'flagpole':
            if get_collision_direction(self._player, block) == 'A':
                self._player._health = self._player.get_max_health()
                

            highscores = open(r'Highscores.txt', 'a')
            name = simpledialog.askstring('Input', 'What is your name?')
            
            entry = name + ('  Score: '+ str(self._player.get_score()) + ' ')
            highscores.write(entry + '\n')
            highscores.close
            
            self.current_level = 'level2.txt'
            self.reset_world(self.current_level)
            

        if block.get_id() == 'tunnel':          
                if self.is_ducking == True:
                    if get_collision_direction(self._player, block) == 'A':                
                        self.reset_world('level2.txt')

        return True

    def _handle_player_collide_mob(self, player: Player, mob: Mob, data,
                                   arbiter: pymunk.Arbiter) -> bool:
        mob.on_hit(arbiter, (self._world, player))

        """Callback to handle collision between the player and a mob in the world

        Parameters:
            player (Player): The player that was involved in the collision
            mob (Mob): The mob in the world the player collides with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      
        Return:
             bool: True (always process this type of collision)

        """ 

        
        if mob.get_id() == 'fireball':
            if self._player_invincible == False:
                self._player.change_health(-3)

        if mob.get_id() == 'mushroom':

            if self._player_invincible == True:
                self._world.remove_mob(mob)
                
            if get_collision_direction(self._player, mob) == 'L':
                if self._player_invincible == False:
                    self._player.change_health(-1)
                    self._player.set_velocity((-100, 0))
                    mob.set_tempo(-35)

            elif get_collision_direction(self._player, mob) == 'R':
                if self._player_invincible == False:
                    self._player.change_health(-1)
                    self._player.set_velocity((100, 0))
                    mob.set_tempo(-35)

            elif get_collision_direction(self._player, mob) == 'A':
                self._player.set_velocity((0, -100))
                self._world.remove_mob(mob)
        
        print(self._player.get_health())

        StatusDisplay.clear_frame(self)
        StatusDisplay.healthbar_colour(self)

        MarioApp.retry(self)
            
        return True

    def _handle_player_separate_block(self, player: Player, block: Block, data,
                                      arbiter: pymunk.Arbiter) -> bool:
        return True





class StatusDisplay(tk.Frame):

    def __init__(self, master):
        """ Construct the variables required for the StatusDisplay (width and the master frame)

            Parameters:
                master (tk.Tk): tkinter root widget
        """
        
        self._remaining_width = 154
        
        self._master = master


    def background(self):
        """ Construction of the black background of the healthbar

        """
        master = self._master
        
        self._health_bar = tk.Frame(master, bg='black', height=20, width=1080)
        self._health_bar.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X)
        

    def healthbar_colour(self):
        """ Construction of the coloured label of the healthbar that changes according to remaining health
            in both colour and remaining width

        """

        if self._player.get_health() >= 10.0:
            self._colour = 'forest green'
      
        elif self._player.get_health() >= 5.0:
            self._colour = 'dark orange'
         
        elif self._player.get_health() >= 4.0:
            self._colour = 'red3'

        elif self._player.get_health() == 0.0:
            self._colour = 'black'

        if self._player.get_health() == 20.0:
            self._remaining_width = 154

        if self._player.get_health() <= 16.0:
            self._remaining_width = 122
            
        if self._player.get_health() <= 12.0:
            self._remaining_width = 91
            
        if self._player.get_health() <= 8.0:
            self._remaining_width = 60
            
        if self._player.get_health() <= 4.0:
            self._remaining_width = 30
            
        if self._player.get_health() == 0.0:
            self._remaining_width = 0

        if self._player_invincible == True:
            self._colour = 'gold'

        self._health_amount = tk.Label(self._health_bar, bg=self._colour, height=1, width=self._remaining_width)
        self._health_amount.pack(side=tk.LEFT, anchor=tk.W)

    def clear_frame(self):
        """ Clearing of the coloured healthbar label so it can be reinserted dependent on updated conditions
        """
        
        label2 = self._health_amount  
        label2.destroy()

    def score(self):
        """ Construction of the score label to keep track of the player's score below their health
        """
        
        master = self._master
        
        self.player_score = self._player.get_score()
        self.score = tk.Label(master, text='Score: ' + str(self.player_score))
        self.score.pack(side=tk.TOP, anchor=tk.S)

    def new_score(self):
        """ Clearing of the score label and reimplentation after the score updates
        """

        new_score = self.score
        new_score.destroy()

    
class MushroomMob(Mob):
    """ The mushroom mob that walks along the ground with its direction reversed whenever it collides with
        a player, block or other mob.

        The player will take damage when colliding with it from the sides and destroy it when colliding from above
    """

    _id = 'mushroom'
    
    def __init__(self):
        
    
        super().__init__(self._id, size=(16, 16), weight=100, tempo=45)


class BounceBlock(Block):
    """ The bounce block which launches the player into the air when they collide with this block from above

    """
    _id = 'bouncyboi'

    def __init__(self):
        """ Constructs a new bounce block
        """
        super().__init__()

    def on_hit(self, event, data):
        """ Callback collision with player event handler

        """
        world, player = data
        block = Block(BounceBlock)

        if get_collision_direction(player, self) != 'A':
            return
        else:
            player.set_velocity((0, -200))


class Star(DroppedItem):
    """ A dropped star item that can be picked up to make the player invincible for 10 seconds indicated by a yellow
        healthbar and cause any mobs that collide with the player during this time to be destroyed
    """

    _id = 'star'
    
    def __init__(self):
        """ Constructs a new star item

        """
        super().__init__()

    def collect(self, player):
        """ Collects the star item and sets the player to be invincible until turned off by step function in MarioApp

        """ 
        self._player_invincible = True
        

class GoalsFlag(Block):
    """ A flag block which upon collision asks the player for their name to record their current score and advances the
        game to the next level
    """

    _id = 'flagpole'
    _cell_size = (0.2, 9)

    def __init__(self):
        """ Constructs a new flagpole block at the designated position

        """
        super().__init__()


class GoalsTunnel(Block):
    """ A tunnel block which upon collision from above while holding a down key to indicate crouching will take the player
        to the next level or bonus room depending on what is defined in configuration
    """

    _id = 'tunnel'
    _cell_size = (2, 2)
    
    def __init__(self):
        """ Constructs a new tunnel block in the level

        """
        super().__init__()

    
def main():
    """ The initialisation of the root window that runs the MarioApp GUI and allows launch

    """
    root = tk.Tk()
    root.title('Mario')

    app = MarioApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
