"""
Simple 2d world where the player can interact with the items in the world.
"""
from PIL.Image import FLIP_LEFT_RIGHT

__author__ = "Sajjad Brohi"
__date__ = "21-Oct-2019"
__version__ = "1.1.0"
__copyright__ = "The University of Queensland, 2019"

import math
import tkinter as tk
from tkinter.filedialog import askopenfilename

from typing import Tuple, List

import pymunk
import operator
from PIL import Image, ImageTk

from game.block import Block, MysteryBlock
from game.entity import Entity, BoundaryWall
from game.mob import Mob, CloudMob, Fireball
from game.item import DroppedItem, Coin
from game.view import GameView, ViewRenderer
from game.world import World

from level import load_world, WorldBuilder
from player import Player

from game.util import get_collision_direction

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
    'b': 'bounce_block',
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
    '@': "mushroom",
}


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
    elif block_id == "bounce_block":
        block = BounceBlock()
    elif block_id == "flagpole":
        block = Flagpole()
    elif block_id == "tunnel":
        block = Tunnel()
    elif block_id == "switch":
        block = Switches()
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
    elif item_id == "star":
        item = StarItem()
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
    elif mob_id == "mushroom":
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
    "bounce_block": "bounce_block",
    "flagpole": "flag",
    "tunnel": "tunnel",
    "switch": "switch"
}

ITEM_IMAGES = {
    "coin": "coin_item",
    "star": "star"
}
#
MOB_IMAGES = {
    "cloud": "floaty",
    "fireball": "fireball_down",
    "mushroom": "mushroom"
}


class MarioViewRenderer(ViewRenderer):
    """A customised view renderer for a game of mario."""

    def __init__(self, block_images, item_images, mob_images):
        """Constructor"""
        super().__init__(block_images, item_images, mob_images)
        self._load_sprite_sheet = SpriteSheetLoader()
        self._timer = 1
        self._cycle = 1
        self._timer2 = 1
        self._cycle2 = 1
        self._timer3 = 1
        self._cycle3 = 1
        self._sprite_images = self._load_sprite_sheet.images_dic()

    @ViewRenderer.draw.register(Player)
    def _draw_player(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Draws the player onto the canvas"""

        # Checks if the player is jumping and then loads image
        if shape.body.velocity.y < -10 or shape.body.velocity.y > 10:
            if instance.get_name() == 'Mario':
                image = self._sprite_images['character']["jumping1"]
            else:
                image = self._sprite_images['character']["jumping2"]

        # Checks if the player is running right and then loads image
        elif shape.body.velocity.x >= 10:
            if instance.get_name() == 'Mario':
                self._timer += 1
                if self._timer > 10:
                    self._cycle += 1
                    self._timer = 1
                if self._cycle > 3:
                    self._cycle = 1
                image = self._sprite_images['character'][f"running{self._cycle}"]

            else:
                self._timer += 1
                if self._timer > 10:
                    self._cycle += 1
                    self._timer = 1
                self._cycle = 4
                if self._cycle > 6:
                    self._cycle = 4
                image = self._sprite_images['character'][f"running{self._cycle}"]

        # Checks if the player is running left and then loads image
        elif shape.body.velocity.x <= -10:
            if instance.get_name() == 'Mario':
                self._timer += 1
                if self._timer > 10:
                    self._cycle += 1
                    self._timer = 1
                if self._cycle > 3:
                    self._cycle = 1
                image = self._sprite_images['character'][f"back_running{self._cycle}"]

            else:
                self._timer += 1
                if self._timer > 10:
                    self._cycle += 1
                    self._timer = 1
                self._cycle = 4
                if self._cycle > 6:
                    self._cycle = 4
                image = self._sprite_images['character'][f"back_running{self._cycle}"]

        # Checks if the player is staying still and then loads image
        else:
            if shape.body.velocity.x >= 0:
                if instance.get_name() == 'Mario':
                    image = self.load_image("mario_right")
                else:
                    image = self.load_image("luigi_right")
            else:
                if instance.get_name() == 'Mario':
                    image = self.load_image("mario_left")
                else:
                    image = self.load_image("luigi_left")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="player")]

    @ViewRenderer.draw.register(MysteryBlock)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Draws the mystery block on canvas"""
        if instance.is_active():
            image = self.load_image("coin")
        else:
            image = self.load_image("coin_used")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(Coin)
    def _draw_coin_block(self, instance: Coin, shape: pymunk.Shape,
                         view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Draws the coin block on the canvas"""
        self._timer2 += 1
        if self._timer2 > 25:
            self._cycle2 += 1
            self._timer2 = 1
        if self._cycle2 > 4:
            self._cycle2 = 1
        image = self._sprite_images['coin'][f"coin{self._cycle2}"]

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    @ViewRenderer.draw.register(Mob)
    def _draw_mob(self, instance: Mob, shape: pymunk.Shape,
                  view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        """Draws the mobs on the canvas"""
        image = self.load_image("fireball_down")
        if instance.get_id() == 'mushroom':
            self._timer3 += 1
            if self._timer3 > 10:
                self._cycle3 += 1
                self._timer3 = 1
            if self._cycle3 > 2:
                self._cycle3 = 1
            image = self._sprite_images['mushroom_mob'][f"walking{self._cycle3}"]
        elif instance.get_id() == 'cloud':
            image = self.load_image("floaty")
        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]


class SpriteSheetLoader(object):
    """Loads up the spritesheet into a dictionary"""

    def __init__(self):
        """Constructor"""
        self._character_images = {}
        self._coin_images = {}
        self._mob_images = {}
        self._images = {}
        self.character_images()
        self.coin_images()
        self.mob_images()
        self._images_dic = self._images

    def character_images(self):
        """Converts the character images from the spritesheet"""

        sheet = Image.open("spritesheets/characters.png")
        count = 1
        x = 80
        y = 34
        # Converts forward running pictures
        while count < 7:
            if count == 4:
                x = 80
                y = 99
            x += 17
            cropped_sheet = sheet.crop((x, y, x + 15, y + 15))
            converted_image = ImageTk.PhotoImage(cropped_sheet)
            self._character_images[f'running{count}'] = converted_image
            count += 1

        count = 1
        x = 80
        y = 34
        # Converts backward running pictures
        while count < 7:
            if count == 4:
                x = 80
                y = 99
            x += 17
            cropped_sheet = sheet.crop((x, y, x + 15, y + 15))
            cropped_sheet = cropped_sheet.transpose(method=FLIP_LEFT_RIGHT)
            converted_image = ImageTk.PhotoImage(cropped_sheet)
            self._character_images[f'back_running{count}'] = converted_image
            count += 1

        x = 148
        y = 34
        count = 1
        # Converts jumping pictures
        while count < 3:
            x += 17
            cropped_sheet = sheet.crop((x, y, x + 15, y + 15))
            converted_image = ImageTk.PhotoImage(cropped_sheet)
            self._character_images[f'jumping{count}'] = converted_image
            x = 148
            y = 99
            count += 1

        self._images['character'] = self._character_images

    def coin_images(self):
        """Converts coin images from spritesheet"""
        sheet = Image.open("spritesheets/items.png")

        count = 1
        x = -15
        y = 112
        while count < 5:
            x += 15
            cropped_sheet = sheet.crop((x, y, x + 15, y + 15))
            converted_image = ImageTk.PhotoImage(cropped_sheet)
            self._character_images[f'coin{count}'] = converted_image
            count += 1

        self._images['coin'] = self._character_images

    def mob_images(self):
        """Converts mob images from spritesheet"""
        sheet = Image.open("spritesheets/enemies.png")

        count = 1
        x = -15
        y = 15
        while count < 3:
            x += 15
            cropped_sheet = sheet.crop((x, y, x + 15, y + 15))
            converted_image = ImageTk.PhotoImage(cropped_sheet)
            self._mob_images[f'walking{count}'] = converted_image
            count += 1

        self._images['mushroom_mob'] = self._mob_images

    def images_dic(self):
        return self._images_dic


class StarItem(DroppedItem):
    """A dropped item that can be picked up to give invincibility for 10 seconds"""
    _id = "star"

    def __init__(self):
        """Constructor"""
        super().__init__()

    def collect(self, player: Player):
        """Checks if item is picked up or not"""
        player.set_invincible(True)
        player._invincibility_health = player.get_health()


class MushroomMob(Mob):
    """An enemy in the game that inflicts 1 damage to the player"""
    _id = "mushroom"

    def __init__(self):
        """Constructor"""
        super().__init__(self._id, size=(16, 16), tempo=20)

    def on_hit(self, event: pymunk.Arbiter, data):
        """The code to perform after collision with anything"""
        world, player = data
        current_x, current_y = player.get_velocity()
        collision = get_collision_direction(player, self)
        if collision == 'A':
            player.set_velocity((current_x, -150))
            world.remove_mob(self)
        elif collision == 'L':
            player.change_health(-1)  # Change to -1
            player.set_velocity((-100, current_y))
            self.change_tempo()
        elif collision == 'R':
            player.change_health(-1)
            player.set_velocity((100, current_y))
            self.change_tempo()

    def change_tempo(self):
        """Change direction of mob after collision with anything"""
        if self.get_tempo() > 0:
            self.set_tempo(-20)
        elif self.get_tempo() < 0:
            self.set_tempo(20)


class Switches(Block):
    """A block that disappears brick blocks within a certain radius when pressed"""
    _id = "switch"

    def __init__(self):
        """Constructor"""
        super().__init__()

    def on_hit(self, event, data):
        """Callback collision with player event handler."""
        position = self.get_position()
        mario_app = data
        mario_app.change_block_position(position)
        collision = get_collision_direction(mario_app.get_player(), self)
        if collision == 'A':
            mario_app.set_switch_status(True)


class Flagpole(Block):
    """A block that takes the player to the next level"""
    _id = "flagpole"
    _cell_size = GOAL_SIZES["flag"]

    def __init__(self):
        """Constructor"""
        super().__init__()

    def on_hit(self, event, data):
        """Callback collision with player event handler."""
        mario_app = data
        collision = get_collision_direction(mario_app.get_player(), self)
        if collision == 'A':
            add_health = mario_app.get_player().get_max_health() - mario_app.get_player().get_health()
            mario_app.get_player().change_health(add_health)

        mario_app.player_name()


class Tunnel(Block):
    """A block that takes the player to the next level"""
    _id = "tunnel"
    _cell_size = GOAL_SIZES["tunnel"]

    def __init__(self):
        """Constructor"""
        super().__init__()

    def on_hit(self, event, data):
        """Callback collision with player event handler."""
        mario_app = data
        collision = get_collision_direction(mario_app.get_player(), self)
        if collision == 'A':
            mario_app.set_tunnel_status(True)


class BounceBlock(Block):
    """A block that bounces the player into the air when stepped on"""
    _id = "bounce_block"

    def __init__(self):
        """Constructor"""
        super().__init__()

    def on_hit(self, event, data):
        """Callback collision with player event handler."""
        world, player = data
        if get_collision_direction(player, self) != "A":
            return
        player.set_velocity((0, -250))


class StatusDisplay(tk.Frame):
    """Display at the bottom of the game of the player's health and score"""

    def __init__(self, master):
        """Constructor"""
        super().__init__(master)
        self._top_frame = tk.Frame(self, bg='black', height=20)
        self._top_frame.pack(fill=tk.X)
        self._bottom_frame = tk.Frame(self._top_frame, bg='green', height=20)
        self._bottom_frame.pack(anchor=tk.W)
        self._label = tk.Label(self, text=f"Score: 0", bg='white')
        self._label.pack(fill=tk.BOTH, expand=True)

    def player_score(self, score):
        """Changes the player's score"""
        self._label.config(text=f"Score: {score}")


class PlayerName(object):
    """Takes player's name and saves it to the high scores file"""

    def __init__(self, master, parent):
        """Constructor"""
        master_window = self.master = tk.Toplevel(master)
        self._parent = parent
        self._level = tk.Label(master_window, text="Input your name to save your score: ")
        self._level.pack()
        self._entry = tk.Entry(master_window)
        self._entry.pack()
        self._button = tk.Button(master_window, text='Save', command=self.save_name)
        self._button.pack()

    def save_name(self):
        """Saves the file after receiving player name"""
        high_scores = self._parent.get_high_scores()
        current_score = self._parent.current_score()
        self._parent.add_high_score(self._entry.get(), current_score)
        current_level = self._parent.current_level()

        # Write the score to the file
        write_file = open(f'high_scores_{current_level}', 'w')
        for i in high_scores:
            write_file.write(f"{i}:{high_scores[i]}\n")
        write_file.close()

        self._parent.reset_world(self._parent.get_file()[f"=={self._parent.current_level()}=="]['goal'])
        self.master.destroy()


class HighScore(object):
    """A popup to display the highest scorers of the current level"""

    def __init__(self, master, parent):
        """Constructor"""
        master_window = self.master = tk.Toplevel(master)
        self._parent = parent
        high_scores = {}

        # Converts high score from string to integer
        for i in self._parent.get_high_scores():
            high_scores[i] = int(self._parent.get_high_scores()[i])

        # Orders the names by descending order
        ordered_high_scores = dict(sorted(high_scores.items(), key=operator.itemgetter(1), reverse=True))
        copy_high_scores = ordered_high_scores.copy()

        # Pops out any name after index 9
        for index, name in enumerate(copy_high_scores):
            if index > 9:
                ordered_high_scores.pop(name)

        hs_items = ordered_high_scores.items()
        self._level = tk.Label(master_window, text="\n".join("{!r}: {!r}".format(key, val) for key, val in hs_items))
        self._level.pack()
        self._button = tk.Button(master_window, text='Okay', command=self.resume_play)
        self._button.pack()

    def resume_play(self):
        """Destroys the popup"""
        self.master.destroy()


class Popup(object):
    """Popup to either load a level or restart current level"""

    def __init__(self, master, parent):
        """Constructor"""
        master_window = self.master = tk.Toplevel(master)
        self._parent = parent
        self._level = tk.Label(master_window, text="Input a level filename")
        self._level.pack()
        self._entry = tk.Entry(master_window)
        self._entry.pack()
        self._button = tk.Button(master_window, text='Load', command=self.load_level)
        self._button.pack()

    def load_level(self):
        """Loads level and destroys popup"""
        self._parent.reset_world(self._entry.get())
        self._parent.get_player().change_health(5)
        self.master.destroy()


class GameLostPopup(object):
    """Popup displayed after player loses all health. Gives option to quit or restart level."""

    def __init__(self, master, parent):
        """Constructor"""
        master_window = self.master = tk.Toplevel(master)
        self._parent = parent
        self._level = tk.Label(master_window, text="You lost the game! Exit or Restart?")
        self._level.pack()
        self._button = tk.Button(master_window, text='Restart', command=self.restart_level)
        self._button.pack()
        self._button = tk.Button(master_window, text='Exit', command=parent.exit)
        self._button.pack()

    def restart_level(self):
        """Restarts level"""
        self._parent.reset_level()
        self.master.destroy()


class GameEnd(object):
    """Popup after the player reaches the last level"""
    def __init__(self, master, parent):
        """Constructor"""
        master_window = self.master = tk.Toplevel(master)
        self._parent = parent
        self._level = tk.Label(master_window, text="You finished the game!")
        self._level.pack()
        self._button = tk.Button(master_window, text='Close', command=parent.exit)
        self._button.pack()


class MarioApp:
    """High-level app class for Mario, a 2d platformer"""

    _world: World

    def __init__(self, master: tk.Tk):
        """Construct a new game of a MarioApp game.

        Parameters:
            master (tk.Tk): tkinter root widget
        """

        self._master = master
        master.title("Mario")
        self._file = file_data

        # All the following if/else statements in this constructor check whether that particular property
        # is given in the config file or not. If it isn't given then it proceeds with the default values
        if 'gravity' in self._file:
            down_gravity = int(self._file["gravity"])
            world_builder = WorldBuilder(BLOCK_SIZE, gravity=(0, down_gravity), fallback=create_unknown)
        else:
            world_builder = WorldBuilder(BLOCK_SIZE, gravity=(0, 300), fallback=create_unknown)

        world_builder.register_builders(BLOCKS.keys(), create_block)
        world_builder.register_builders(ITEMS.keys(), create_item)
        world_builder.register_builders(MOBS.keys(), create_mob)
        self._builder = world_builder

        if 'health' in self._file:
            self._max_health = int(self._file['health'])
        else:
            self._max_health = 5

        if 'character' in self._file and self._file['character'] == 'luigi':
            self._player = Player(name='Luigi', max_health=self._max_health)
        else:
            self._player = Player(max_health=self._max_health)

        if 'start' in self._file:
            self._current_level = self._file['start']
        else:
            self._current_level = "level1.txt"
        self._high_scores = {}
        self.reset_world(self._current_level)
        self._renderer = MarioViewRenderer(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES)

        # Menu-bar
        menubar = tk.Menu(master)
        master.config(menu=menubar)

        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Load Level", command=self.popup)
        filemenu.add_command(label="Reset Level", command=self.reset_level)
        filemenu.add_command(label="High Scores", command=self.high_score_popup)
        filemenu.add_command(label="Exit", command=self.exit)

        # Status Display of the game
        self._status_display = StatusDisplay(self._master)
        self._status_display.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

        size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
        self._map_size = size[0]

        # Canvas and binding Keys
        self._view = GameView(master, size, self._renderer)
        self._view.pack()

        self._view.focus_set()
        self._view.bind('<w>', self.bind)
        self._view.bind('<Up>', self.bind)
        self._view.bind('<space>', self.bind)
        self._view.bind('<a>', self.bind)
        self._view.bind('<Left>', self.bind)
        self._view.bind('<s>', self.bind)
        self._view.bind('<Down>', self.bind)
        self._view.bind('<d>', self.bind)
        self._view.bind('<Right>', self.bind)

        # Game status' and timer
        self._game_status = False
        self._tunnel_status = False
        self._switch_status = False
        self._invincibility_time = 0
        self._ten_second_timer = 0
        self._block_position = None
        self._loop_check = True
        self._items_in_range = []

        # Wait for window to update before continuing
        master.update_idletasks()
        self.step()

    def update_high_scores(self):
        """Updates the highest score by reading from the level file"""
        self._high_scores = {}
        try:
            read_file = open(f'high_scores_{self._current_level}', 'r')
            for line in read_file:
                line = line.strip()
                name, score = line.split(':')
                self._high_scores[name] = score
        except FileNotFoundError:
            print("No such file exists")

    def get_high_scores(self):
        """Retrieves the highest scores"""
        return self._high_scores

    def add_high_score(self, name, score):
        """Add's highest score to the current level"""
        self._high_scores[name] = score

    def current_score(self):
        """Retrieves current score of the player"""
        return self._player.get_score()

    def block_position(self):
        """Retrieves the block position"""
        return self._block_position

    def change_block_position(self, change):
        """Changes the block position"""
        self._block_position = change

    def get_player(self):
        """Retrieves the player instance"""
        return self._player

    def get_file(self):
        """Retrieves the config file"""
        return self._file

    def tunnel_status(self):
        """Checks if the player is colliding with the tunnel from above"""
        return self._tunnel_status

    def set_tunnel_status(self, change):
        """Sets the tunnel status"""
        self._tunnel_status = change

    def switch_status(self):
        """Retrieves the switch status"""
        return self._switch_status

    def set_switch_status(self, change):
        """Sets the switch status"""
        self._switch_status = change

    def current_level(self):
        """Retrieves the current level"""
        return self._current_level

    def change_level(self, level):
        """Changes the level to the new level"""
        self._current_level = level

    def health(self):
        """Keeps track of the health of the player and updates status bar accordingly"""
        health = self._player.get_health() / self._player.get_max_health()
        if not self._player.get_invincible_value():
            if health > 0.80:
                self._status_display._bottom_frame.config(width=self._map_size, bg='green')
            elif 0.60 < health <= 0.80:
                self._status_display._bottom_frame.config(width=self._map_size * health, bg='green')
            elif 0.40 < health <= 0.60:
                self._status_display._bottom_frame.config(width=self._map_size * health, bg='green')
            elif 0.20 < health <= 0.40:
                self._status_display._bottom_frame.config(width=self._map_size * health, bg='orange')
            elif 0.00 < health <= 0.20:
                self._status_display._bottom_frame.config(width=self._map_size * health, bg='red')
            elif health == 0.00:
                self._status_display._bottom_frame.config(width=self._map_size * 0.00)
                self.game_lost_popup()
                self._game_status = True

    def score(self):
        """Displays the player score"""
        self._status_display.player_score(self.current_score())

    def player_name(self):
        """Calls the class of PlayerName"""
        PlayerName(self._master, self)

    def game_lost_popup(self):
        """Calls GameLostPopup if the player loses all health"""
        if self._game_status:
            pass
        else:
            GameLostPopup(self._master, self)

    def popup(self):
        """Calls Popup class"""
        self._game_status = True
        Popup(self._master, self)

    def high_score_popup(self):
        """Calls HighScore class"""
        HighScore(self._master, self)

    def reset_level(self):
        self._player.change_health(5)
        self.reset_world(self._current_level)

    def exit(self):
        """Close the application."""
        self._master.destroy()

    def reset_world(self, new_level):
        """Recreates the world"""
        if new_level == 'END':
            self._game_status = True
            GameEnd(self._master, self)
        else:
            self._game_status = False
            self._world = load_world(self._builder, new_level)

            # Recreates world based on whether coordinates and/or mass are given in the config file or not
            if "x" in self._file and "y" in self._file:
                self._world.add_player(self._player, int(self._file['x']), int(self._file['y']))
            elif "mass" in self._file:
                self._world.add_player(self._player, BLOCK_SIZE, BLOCK_SIZE, mass=int(self._file['mass']))
            else:
                self._world.add_player(self._player, BLOCK_SIZE, BLOCK_SIZE)

            self._builder.clear()
            self._setup_collision_handlers()
            self.change_level(new_level)
            self.update_high_scores()

    def bind(self, event):
        """Bind all the keyboard events to their event handlers."""
        current_x, current_y = self._player.get_velocity()
        event = str(event.keysym)

        if event == 'Up' or event == 'w' or event == 'space':
            self._jump()
        elif event == 'a' or event == 'Left':
            self._move(-60, current_y)
        elif event == 'd' or event == 'Right':
            self._move(60, current_y)
        else:
            self._duck()

    def redraw(self):
        """Redraw all the entities in the game canvas."""
        self._view.delete(tk.ALL)
        self.health()
        self.score()
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

    def check_items_in_range(self):
        """Checks the items in range of the block"""
        if self._loop_check:
            x, y = self._block_position
            self._items_in_range = self._world.get_things_in_range(x, y, 50)
            for i in self._items_in_range:
                if i.get_id() == 'brick' or i.get_id == 'switch':
                    self._world.remove_block(i)
            self._loop_check = False

    def switch(self):
        """Called once the switch is activated"""
        self._ten_second_timer += 1
        self.check_items_in_range()
        if self._ten_second_timer > 450:
            for i in self._items_in_range:
                if i.get_id() == 'brick' or i.get_id == 'switch':
                    x, y = i.get_position()
                    self._world.add_block(i, x, y)
            self._ten_second_timer = 0
            self.set_switch_status(False)

    def invincibility(self):
        """Called once the player is invincible"""
        self._invincibility_time += 1
        self._status_display._bottom_frame.config(bg='yellow')

        # If the invincibility time expires then it resets everything that was changed
        if self._invincibility_time > self._player.get_invincibility_time():
            self._player.set_invincible(False)
            old_health = self._player.health_in_invincibility()
            current_health = self._player.get_health()
            change = old_health - current_health
            self._player.change_health(change)
            self._status_display._bottom_frame.config(bg='green')

    def step(self):
        """Step the world physics and redraw the canvas."""
        data = (self._world, self._player)
        if self._player.get_invincible_value():
            self.invincibility()

        if self._switch_status:
            self.switch()

        if self._game_status:
            pass
        else:
            self._world.step(data)
            self.scroll()
            self.redraw()

        self._master.after(10, self.step)

    def _move(self, dx, dy):
        """Moves the player either left or right"""
        max_velocity = int(self._file["max_velocity"])
        negative_max = -max_velocity
        if dx < 0:
            if dx > negative_max:
                self._player.set_velocity((dx, dy))
        elif dx > 0:
            if dx < max_velocity:
                self._player.set_velocity((dx, dy))

    def _jump(self):
        """Gives velocity to the player in the y-direction"""
        current_x, current_y = self._player.get_velocity()
        # xav = get_collision_direction(self._player, self._world.get_block(current_x, current_y))
        if self._player.is_jumping() is False:
            self._player.set_velocity((current_x, -200))
        self._player.set_jumping(True)

    def _duck(self):
        """Goes through the tunnel if pressed on top of the tunnel"""
        if self._tunnel_status:
            self.reset_world(self._file[f"=={self._current_level}=="]['tunnel'])
            self._tunnel_status = False

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
        elif mob.get_id() == "mushroom":
            collision = get_collision_direction(mob, block)
            if collision == "R" or collision == "L":
                if mob.get_tempo() > 0:
                    mob.set_tempo(-20)
                elif mob.get_tempo() < 0:
                    mob.set_tempo(20)

        return True

    def _handle_mob_collide_item(self, mob: Mob, block: Block, data,
                                 arbiter: pymunk.Arbiter) -> bool:
        return False

    def _handle_mob_collide_mob(self, mob1: Mob, mob2: Mob, data,
                                arbiter: pymunk.Arbiter) -> bool:
        if mob1.get_id() == "fireball" or mob2.get_id() == "fireball":
            self._world.remove_mob(mob1)
            self._world.remove_mob(mob2)

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

        return False

    def _handle_player_collide_block(self, player: Player, block: Block, data,
                                     arbiter: pymunk.Arbiter) -> bool:
        if block.get_id() == "flagpole" or block.get_id() == "tunnel" or block.get_id() == "switch":
            block.on_hit(arbiter, self)
        else:
            block.on_hit(arbiter, (self._world, player))
        if self._switch_status:
            if block.get_id() == "switch":
                return False
        self._player.set_jumping(False)
        return True

    def _handle_player_collide_mob(self, player: Player, mob: Mob, data,
                                   arbiter: pymunk.Arbiter) -> bool:
        mob.on_hit(arbiter, (self._world, player))
        if self._player.get_invincible_value():
            self._world.remove_mob(mob)
        return True

    def _handle_player_separate_block(self, player: Player, block: Block, data,
                                      arbiter: pymunk.Arbiter) -> bool:
        self._tunnel_status = False
        return True


def config_file(filename):
    """Opens and parses the config file"""

    file_data = {}
    fd = open(filename, 'r')
    previous_line = ''
    before_previous_line = ''
    level_text = False
    next_level = False
    non_level = True

    # Goes through a loop across every line in the file
    for line in fd:
        line = line.strip()

        # Puts every non-level data into the file_data
        if non_level:
            if line != '' and line.endswith('==') is False:
                setting, _, specification = line.split()
                file_data[setting] = specification

        # Checks if there is a tunnel in the level and adds that to the file_data
        if next_level:
            if line != '':
                setting, _, specification = line.split()
                add_dict = {setting: specification}
                file_data[before_previous_line].update(add_dict)

        # Checks if there is a goal in the level and adds that to the file_data
        if level_text:
            setting, _, specification = line.split()
            add_dict = {setting: specification}
            file_data[previous_line] = add_dict
            before_previous_line = previous_line
            next_level = True
        else:
            next_level = False

        # Checks if the file ends with 'txt==' then activates the following bool so that the above if statements pass
        if line.endswith('txt=='):
            non_level = False
            level_text = True
            file_data[line] = {}
        else:
            level_text = False
        previous_line = line
    fd.close()

    return file_data


if __name__ == '__main__':
    path = tk.Tk()
    path.withdraw()
    path.update()
    file_path = askopenfilename()
    file_data = config_file(file_path)

    root = tk.Toplevel()
    app = MarioApp(root)
    root.mainloop()
