#!/usr/bin/env python
"""
Simple, arcade space-shooter with pixel graphics made of basic Sprites. Written on Python 3.6 with Arcade 2.0.8 module.

To save best scores shelve module is used, and scores are saved in a distinct file in the config_files directory. I also
used pyautogui to get screen resolution.
"""
__author__ = "Rafał Trąbski"
__copyright__ = "Copyright 2019"
__credits__ = []
__license__ = "Share Alike Attribution-NonCommercial-ShareAlike 4.0"
__version__ = "1.0.0"
__maintainer__ = "Rafał Trąbski"
__email__ = "rafal.trabski@mises.pl"
__status__ = "Development"

import os
import math
import string
import random
import shelve
import arcade
import pyautogui

from functools import partial
from simple_arcade_menu import SharedVariable, Cursor, Menu, SubMenu, Button, Slider

# constants:
TITLE = "Red Invaders"
# TODO: adjustment o window size to the different screen sizes [ ]
SCREEN_WIDTH = pyautogui.size()[0]  # int(2048*0.9)
SCREEN_HEIGHT = pyautogui.size()[1]  # int(1280*0.9)
SPRITES_SCALE = int(SCREEN_WIDTH / SCREEN_HEIGHT) * 1.5
FPS = 45  # frames per second used by arcade.window module to refresh the screen
MARGIN, SCORE_STRIPE = 40 * SPRITES_SCALE, 40
BACKGROUND_SPEED = 0.3
STARS_DENSITY = 1
RED, WHITE, YELLOW, BLUE = arcade.color.RED, arcade.color.WHITE, arcade.color.YELLOW_ORANGE, arcade.color.ELECTRIC_BLUE
STARS_COLORS = (WHITE, WHITE, WHITE, WHITE, BLUE, BLUE, YELLOW, YELLOW, RED)
STAR_SIZES = (1, 1, 1, 1, 2, 2, 3)
BACKGROUND_COLOR, GREEN = arcade.color.BLACK, arcade.color.BRIGHT_GREEN
PATH = os.path.dirname(os.path.abspath(__file__))
GRAPHICS_PATH = PATH + "/graphics/"
SOUNDS_PATH = PATH + "/sounds/"
CONFIG_PATH = PATH + "/config_files/"
SCORES_FILE = "best_scores.data"
SPACESHIP_SPEED = 15
SPACESHIP_STRAFE = 10
LASER_GUN_SINGLE = "laser_single"
LASER_GUN_LEFT = "laser_left"
LASER_GUN_RIGHT = "laser_right"
TURRETS, TURRET_SMALL = "turrets", "turret_small"
UPWARD = 0.0
DOWNWARD = 180.0
EXPLOSION = "explosion_sound"
HIT_SOUND = "hit"
ROCKET_SOUND = "rocket"
POWERUP_SOUND = "powerup"
POWERUP_TIME = 1800
POWERUP_CHANCE = 0
POWERUP_ROCKETS_1, POWERUP_ROCKETS_2, POWERUP_ROCKETS_3 = "powerup_rockets_1", "powerup_rockets_2", "powerup_rockets_3"
POWERUP_LASER_DUAL, POWERUP_LASER_STRONG, POWERUP_SHIELD = "powerup_laser_dual", "powerup_laser_fast", "powerup_shield"
TEXTURE, HEALTH, SHIELD, ROCKETS, SPEED, WEAPON = "texture", "health", "shield", "rockets", "speed", "weapon"
PLAYER, HOSTILES, POWERUPS, LEVELS, RATINGS, SCORES = "player", "hostiles", "powerups", "levels", "ratings", "scores"
LASERS, DAMAGES, SOUNDS, TYPES, ROF, KINETIC = "lasers", "damages", "sounds", "types", "rof", "kinetics"
MAIN_MENU, INSTRUCTIONS_SUBMENU, OPTIONS_SUBMENU = "main", "show_instructions_menu", "options"
MIN_DISTANCE, MAX_DISTANCE = "preferred_min_distance", "preferred_max_distance"

# game-data containers to be filled from external files
player, hostiles, powerups, levels, weapons, game = None, None, None, None, None, None


def get_image_path(filename: str):
    """
    Produce TESTS_PATH to the image, which name is provided as parameter.

    :param filename: str -- name of the image file to be loaded without extension
    :return: str -- absolute TESTS_PATH of image
    """
    return GRAPHICS_PATH + filename + ".png"


def get_sound_path(filename: str):
    """
    Produce TESTS_PATH to the sound file, which name is provided as parameter.

    :param filename: str -- name of the sound file
    :return: str -- absolute TESTS_PATH of sound file
    """
    return SOUNDS_PATH + filename


def load_config_files(path: str = CONFIG_PATH):
    """
    Find, open and unpack data from config txt files into the internal data structures. Config files are: levels.txt,
    hostiles.txt, player.txt. ALl files should be located in the 'config_files' directory. Each config file must be
    structured accordingly to the rules - see 'README.txt' in config directory,
    Data retrieved from files is processed to the lists and dicts, which are later used by object constructors in the
    classes and by methods of the Game class.
    Argument 'TESTS_PATH' is required in case of unit testing - alternative TESTS_PATH to testing config files could be passed.
    :return: dicts of lists and dicts -- various game-data in order: player, hostiles, powerups, levels, weapons
    """
    os.chdir(path)
    player_data, hostiles_data, powerups_data, levels_data, weapons_data = {}, {}, {}, {}, {}
    player_, hostiles_, powerups_, levels_, weapons_ = "player.txt", "hostiles.txt", "powerups.txt", "levels.txt", \
                                                       "weapons.txt"
    # TODO: more robust file reading and converting system [x][ ][ ]
    with open(player_, "r") as pl, open(hostiles_, "r") as h, open(powerups_, "r") as pu, open(levels_, "r") as L, \
            open(weapons_, "r") as w:
        for file in [pl, h, pu, L, w]:
            file_unpacked = []
            for line in file:
                if line.startswith("#") or len(line) == 0:
                    continue
                else:
                    file_unpacked.append(line.strip("\n"))
            # after unpacking data, fill dicts for player, hostiles, powerups and levels with retrieved values
            if file == pl:
                for elem in file_unpacked:
                    cat = elem.split(" = ")[0]
                    if elem.startswith(TEXTURE):
                        player_data[TEXTURE] = []
                        for texture in elem.split(" = ")[1].split("; "):
                            player_data[TEXTURE].append(texture)
                    elif cat in [HEALTH, WEAPON]:
                        player_data[elem.split(" = ")[0]] = elem.split(" = ")[1]
                    elif cat == SPEED:
                        player_data[SPEED] = float(elem.split(" = ")[1])
                    elif cat in [ROCKETS, SHIELD]:
                        player_data[elem.split(" = ")[0]] = int(elem.split(" = ")[1])
            elif file == h:
                for elem in file_unpacked:
                    data = elem.split(" = ")
                    if data[0] == HOSTILES:
                        hostiles_data[HOSTILES] = []
                        for enemy in data[1].split("; "):
                            hostiles_data[HOSTILES].append(enemy)
                    elif data[0] in [RATINGS, HEALTH, ROCKETS, SCORES, SHIELD]:
                        hostiles_data[data[0]] = {}
                        for enemy in data[1].split("; "):
                            hostiles_data[data[0]][enemy.split(": ")[0]] = int(enemy.split(": ")[1])
                    elif data[0] in [SPEED, MIN_DISTANCE, MAX_DISTANCE]:
                        hostiles_data[data[0]] = {}
                        for enemy in data[1].split("; "):
                            hostiles_data[data[0]][enemy.split(": ")[0]] = float(enemy.split(": ")[1])
                    elif data[0] == WEAPON:
                        hostiles_data[WEAPON] = {}
                        for enemy in data[1].split("; "):
                            model = enemy.split(": ")
                            guns_count = int(model[1].split(", ")[0])
                            guns_type = model[1].split(", ")[1]
                            hostiles_data[WEAPON][model[0]] = [guns_count, guns_type]
                    elif data[0] == TURRETS:
                        hostiles_data[TURRETS] = {}
                        for enemy in data[1].split("; "):
                            turrets = []
                            ship = enemy.split(": ")
                            for turret in ship[1].split("|"):
                                data = turret.split(", ")
                                model = data[0]
                                gun = data[1]
                                offset_x = int(data[2])
                                offset_y = int(data[3])
                                rof = int(data[4])
                                rot = int(data[5])
                                turrets.append((model, gun, offset_x, offset_y, rof, rot))
                            hostiles_data[TURRETS][ship[0]] = turrets
            elif file == pu:
                for elem in file_unpacked:
                    data = elem.strip("[").strip("]").split(" = ")
                    if data[0] == POWERUPS:
                        powerups_data = [x for x in data[1].split("; ")]
            elif file == L:
                # TODO: levels logic and then levels config unpacking [ ], test it [ ]
                continue
            elif file == w:
                # TODO: weapons unpacking from data [x], test it [x][x]
                for elem in file_unpacked:
                    cat, data = elem.split(" = ")[0], elem.split(" = ")[1]
                    if cat in [SPEED, DAMAGES, ROF]:
                        weapons_data[cat] = {}
                        for weapon in data.split("; "):
                            weapons_data[cat][weapon.split(": ")[0]] = int(weapon.split(": ")[1])
                    elif cat == SOUNDS:
                        weapons_data[cat] = {}
                        for weapon in data.split("; "):
                            weapons_data[cat][weapon.split(": ")[0]] = weapon.split(": ")[1].strip(".wav")
                    elif cat in [KINETIC, LASERS, ROCKETS]:
                        weapons_data[cat] = []
                        for weapon in data.split("; "):
                            weapons_data[cat].append(weapon)
                continue
    return player_data, hostiles_data, powerups_data, levels_data, weapons_data


def load_sounds():
    """
    Load all required game sounds as arcade.sound objects and save references to them as global variables to be used
    during the game. Sounds are detected automatically, so do not put to the 'sounds' directory any files without
    .wav extension.
    """
    if os.path.isdir(SOUNDS_PATH):
        for soundfile in os.listdir(SOUNDS_PATH):
            if soundfile.endswith('wav'):
                file_name = os.path.basename(PATH + '/' + soundfile)
                globals()[os.path.splitext(file_name)[0]] = arcade.load_sound(get_sound_path(file_name))


def play_sound(sound: str):
    """
    Play sound with arcade.sound module. Sounds are global arcade.sound objects.

    :param sound: str -- name of the sound file without .wav extension
    """
    if sound == EXPLOSION:
        sound = random.choice(("explosion", "explosion_2"))
    arcade.play_sound(globals()[sound])
    # TODO: test if all sounds plays correctly [x][x][ ]


class SpaceObject(arcade.Sprite):
    """
    Each object generated in the game is a SpaceObject. It is basically a wrapper used to correctly spawn arcade.Sprite
    object with usage of helper function get_image_path().
    """

    def __init__(self, filename: str, size: int = 1):
        super().__init__(get_image_path(filename), SPRITES_SCALE * size)  # this is what we need this base-class for

    def update(self):
        self.angle = self.angle % 360  # guarantee that angle would be in range 0 to 360 degrees
        super().update()


class Spaceship(SpaceObject):
    """
    Each spaceship in game is an instance of this class, even player ship.
    """

    def __init__(self, filename: str):
        """
        Create new Spaceship instance. IMPORTANT: arcade.Sprite requires passing a basic texture filename as a first
        argument. Pass it without '.png' extension - Spaceobject class provides it automatically.

        :param filename: str -- name of image file for a Sprite basic texture (IMPORTANT: without extension!)
        """
        super().__init__(filename)
        self.main_weapon = None
        self.secondary_weapon = None
        self.rate_of_fire = None
        self.last_shot = None
        self.gun_slots = []
        self.rockets = 0
        self.last_shot = 0
        self.shield = 0
        self.health = 10
        self.hit = False
        self.shield_hit = False

    def rearm(self, weapon: str):
        """
        Change weapon used by the ship, modify gun slots positions and rate of fire.

        :param weapon: str -- name of weapon to arm ship with
        """
        if weapon in weapons[LASERS]:
            self.main_weapon = weapon
            self.rate_of_fire = weapons[ROF][weapon]
            if not self.gun_slots:
                self.gun_slots = [[LASER_GUN_SINGLE, self.top, self.center_x]]
            elif len(self.gun_slots) == 1:
                self.gun_slots = [[LASER_GUN_LEFT, self.top, self.left], [LASER_GUN_RIGHT, self.top, self.right]]
            else:
                pass
        elif weapon in weapons[KINETIC]:
            self.main_weapon = weapon
            self.rate_of_fire[weapon] = weapons[ROF][weapon]
            pass
        else:
            self.secondary_weapon = weapon

    def shoot(self):
        """
        Handles a single weapon shot initializing creation of new Projectile instance.
        """
        for slot in self.gun_slots:
            play_sound(weapons[SOUNDS][self.main_weapon])
            if isinstance(self, PlayerShip):
                power = self.powerup_damage_mod
            else:
                power = 1
            game.projectiles.append(Projectile(self.main_weapon, power, self.angle, slot))
            self.last_shot = game.game_time

    def launch_rocket(self):
        """
        Handle launching a rocket.
        """
        play_sound(weapons[SOUNDS][self.secondary_weapon])
        game.projectiles.append(Projectile(self.secondary_weapon, 1, self.angle, self.gun_slots[0]))
        self.rockets -= 1

    def damage(self, damage: int):
        """
        Handle the damage dealt to the Spaceship object. First eat shield, then take health, then destroy ship.
        """
        if self.shield > damage:
            self.shield -= damage
            if not self.shield_hit:
                self.shield_hit = True
                self.set_texture(-2)
                hit_color = RED if self == game.player else GREEN
                game.create_hint("Shield hit!", self.center_x, self.center_y, 0, 0, hit_color, 10, 1)
        else:
            self.health -= (damage - self.shield)
            self.shield = 0
            if not self.hit:
                self.hit = True
                self.set_texture(-1)
                hit_color = RED if self == game.player else GREEN
                game.create_hint("Hit!", self.center_x, self.center_y, 0, 0, hit_color, 10, 1)

        if self.health < 1:  # killing ships first, to avoid unnecessary updating their properties later
            self.kill()
        else:
            play_sound(HIT_SOUND)

    def update(self):
        super().update()

        if self.hit or self.shield_hit:
            self.clear_hit_texture()

        for slot in self.gun_slots:
            slot[1] = self.top if self.angle == UPWARD else self.bottom
            if slot[0] == LASER_GUN_SINGLE:
                slot[2] = self.center_x
            elif slot[0] == LASER_GUN_LEFT:
                slot[2] = self.left
            else:
                slot[2] = self.right

        self.obey_margins()  # shots does not obey screen margins

    def clear_hit_texture(self):
        """Replace 'hit' texture with normal one, after ship being hit."""
        if self.shield > 0:
            self.shield_hit = False
        else:
            self.hit = False
        self.set_texture(0)

    def obey_margins(self):
        """
        Guarantee that no Spaceship would go out the game window.
        """
        if self.center_x < MARGIN:
            self.center_x = MARGIN
        elif self.center_x > SCREEN_WIDTH - MARGIN:
            self.center_x = SCREEN_WIDTH - MARGIN

        if self.center_y < MARGIN + SCORE_STRIPE:
            self.center_y = MARGIN + SCORE_STRIPE
        elif self.center_y > SCREEN_HEIGHT - MARGIN:
            self.center_y = SCREEN_HEIGHT - MARGIN

    def kill(self):
        super().kill()
        game.explosions.append(Explosion(self.center_x, self.center_y))  # just an animated sprite


class PlayerShip(Spaceship):
    """
    Subclass for the player ship.
    """

    RIGHT, LEFT, UP, DOWN, STOP = SPACESHIP_STRAFE, -SPACESHIP_STRAFE, SPACESHIP_SPEED, -SPACESHIP_SPEED, 0

    def __init__(self, textures_list: list):
        super().__init__("player_ship/" + textures_list[0])
        self.booster_effects = {POWERUP_LASER_DUAL: [False, 0], POWERUP_LASER_STRONG: [False, 0]}
        self.powerup_damage_mod = 1
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.rearm(player[WEAPON])
        self.load_textures(textures_list[1:])
        self.rockets = player[ROCKETS]
        if self.rockets: self.rearm(weapons[ROCKETS][1])
        self.shooting = False
        self.overheat = 0

        self.horizontal = PlayerShip.STOP
        self.vertical = PlayerShip.STOP

    def load_textures(self, textures_list: list):
        """
        Set up all textures for a playership sprite. Ship texture changes accordingly to themovementnt direction.
        """
        textures = ["player_ship/" + texture for texture in textures_list]
        [self.append_texture(arcade.load_texture(get_image_path(texture), scale=SPRITES_SCALE)) for texture in textures]

    def update_texture(self):
        """
        Toggle through self.textures accordingly to display corrects engines working (keys on keyboard pressed).
        """
        if self.change_y > 0:
            if self.change_x > 0:
                self.set_texture(2)  # key D or RIGHT
            elif self.change_x < 0:
                self.set_texture(3)  # key A o LEFT
            else:
                self.set_texture(1)  # key W or UP
        elif self.change_y < 0:
            if self.change_x > 0:
                self.set_texture(7)  # key D
            elif self.change_x < 0:
                self.set_texture(8)  # key A
            else:
                self.set_texture(6)  # key S or DOWN
        else:
            if self.change_x > 0:
                self.set_texture(5)  # key D
            elif self.change_x < 0:
                self.set_texture(4)  # key A
            else:
                self.set_texture(0)  # no key pressed

    def toggle_shooting(self):
        """
        Switch between 'shooting' and 'not-shooting' modes. If self.shooting is True, PlayerShip would fire it's main
        weapon as fast as it's ROF variable permits for, and as long as self.overheat is not >= 100.
        """
        self.shooting = not self.shooting

    def update(self):
        super().update()

        self.update_movement()  # set the movement accordingly to the keys pressed by player

        self.check_for_collisions()

        self.update_texture()  # update texture accordingly to the movement (to show work of engines):

        self.manage_booster_effects()

        if all((self.shooting, self.last_shot is not None, game.game_time - self.last_shot >= self.rate_of_fire)):
            game.shots_fired += 1
            self.last_shot = game.game_time
            self.overheat += 5  # TODO: overheating system [ ]
            self.shoot()

    def update_movement(self):
        """Set the movement speed values accordingly to the key pressed by the player."""
        self.change_x = self.horizontal
        self.change_y = self.vertical

    def check_for_collisions(self):
        """
        Check if player ship collides with hostile ships or meteorites (?). If so, destroy it.
        """
        hit_list = arcade.check_for_collision_with_list(self, game.hostiles)
        if not game.god_mode:
            for hit in hit_list:
                hit.kill()
                self.kill()
                break

    def manage_booster_effects(self):
        """
        Check each active booster effect if it's duration surpassed booster game_time limit. If so, terminate it.
        """
        for booster in self.booster_effects:
            if booster[0]:
                if self.booster_effects[booster][1] == 0:
                    self.end_booster_effect(booster)
                else:
                    self.booster_effects[booster][1] -= 1

    def apply_booster(self, booster_type: str):
        """
        Apply a booster effect to the player's ship.
        """
        hints = {POWERUP_ROCKETS_1: "ROCKETS +1", POWERUP_ROCKETS_2: "ROCKETS +2", POWERUP_ROCKETS_3: "ROCKETS +3",
                 POWERUP_LASER_DUAL: "DUAL LASER CANNON +30 sec.", POWERUP_LASER_STRONG: "STRONGER LASER CANON +30sec",
                 POWERUP_SHIELD: "ENERGETIC SHIELD +50"}
        if booster_type == POWERUP_LASER_DUAL:
            if not self.booster_effects[POWERUP_LASER_DUAL][0]:
                self.booster_effects[POWERUP_LASER_DUAL][0] = True
                self.rearm(weapons[LASERS][0])
                self.rearm(weapons[LASERS][0])
            self.booster_effects[POWERUP_LASER_DUAL][1] += POWERUP_TIME
        elif booster_type == POWERUP_LASER_STRONG:
            if not self.booster_effects[POWERUP_LASER_STRONG][0]:
                self.booster_effects[POWERUP_LASER_STRONG][0] = True
            self.booster_effects[POWERUP_LASER_STRONG][1] += POWERUP_TIME
            self.powerup_damage_mod += 0.25
        elif booster_type == POWERUP_ROCKETS_1:
            self.rearm(weapons[ROCKETS][1])
            self.rockets += 1
        elif booster_type == POWERUP_ROCKETS_2:
            self.rearm(weapons[ROCKETS][1])
            self.rockets += 2
        elif booster_type == POWERUP_ROCKETS_3:
            self.rearm(weapons[ROCKETS][1])
            self.rockets += 3
        elif booster_type == POWERUP_SHIELD:
            self.shield += 50
        game.create_hint(hints[booster_type], color=GREEN, size=25, time=2)

    def end_booster_effect(self, booster):
        """
        Remove booster effect after 30 seconds.
        """
        if booster == POWERUP_LASER_DUAL:
            self.main_weapon = None
            self.gun_slots = []
            self.rearm(weapons[LASERS][0])
        else:
            self.powerup_damage_mod = 1
        self.booster_effects[booster][0] = False

    def kill(self):
        super().kill()
        game.if_new_high_score()


class Hostile(Spaceship):
    """
    Subclass for enemies. They can do many funny things, like avoiding player's shots.
    """

    def __init__(self, difficulty: int):
        max_enemy = difficulty + 1 if difficulty <= len(hostiles[HOSTILES]) else len(hostiles[HOSTILES])
        hostile = random.choice(hostiles[HOSTILES][0:max_enemy])  # TODO: better enemies spawning system?
        super().__init__("hostiles/" + hostile)
        self.model = hostile
        self.speed = hostiles[SPEED][hostile]
        self.health = hostiles[HEALTH][hostile]
        self.shield = hostiles[SHIELD][hostile]
        self.evasiveness = 40 - difficulty  # tricky, lesser number, higher chance that hostile will evade
        self.avoiding = False
        self.targeted_position = None
        self.dangerous = None
        self.player_x, self.player_y = None, None
        self.turrets = self.install_turrets()
        self.append_texture(arcade.load_texture(get_image_path("hostiles/" + hostile + "_shield"), scale=SPRITES_SCALE))
        self.append_texture(arcade.load_texture(get_image_path("hostiles/" + hostile + "_hit"), scale=SPRITES_SCALE))
        for i in range(hostiles[WEAPON][hostile][0]):
            self.rearm(hostiles[WEAPON][hostile][1])

    def install_turrets(self):
        """
        If hostile ship has turrets, spawn correct Sprites, and place them in proper positions.

        :return: None or list of turrets (SpaceObject instances)
        """
        if self.model in hostiles[TURRETS]:
            installed_turrets = []
            for turret in hostiles[TURRETS][self.model]:
                new_turret = Turret(turret[0], turret[1], turret[2], turret[3], turret[4], turret[5])
                new_turret.center_x = self.left + turret[2]
                new_turret.center_y = self.top - turret[3]
                new_turret.angle = self.angle
                installed_turrets.append(new_turret)
                game.turrets.append(new_turret)
            return installed_turrets
        return None

    def update(self):
        super().update()

        self.player_x, self.player_y = game.player.center_x, game.player.center_y

        if self.in_danger():
            self.evade()

        if (not self.avoiding or not self.targeted_position) and random.randint(1, 100) > 75:
            self.maneuvre()

        if not self.avoiding or not self.targeted_position:
            self.aim_at_player()
            # if in line with a player, enemy fires it's weapon:
            if game.game_time - self.last_shot > self.rate_of_fire and abs(self.center_x - game.player.center_x) < 50:
                self.shoot()

        self.update_speed()  # each enemy ship has it's own speed modifier

        if self.turrets:
            self.handle_turrets()

    def damage(self, damage: int):
        game.hits += 1
        super().damage(damage)

    def in_danger(self):
        """
        Check if there is a player-shot projectile in line of this hostile ship.
        """
        self.avoiding = False
        for projectile in game.projectiles:
            if projectile.angle == UPWARD:
                if projectile.center_y < self.center_y:
                    if abs(self.center_x - projectile.center_x) < 75:
                        if random.randint(1, 100) > self.evasiveness:  # there is the tricky part!
                            self.dangerous = projectile
                            return True
        return self.avoiding

    def evade(self):
        """
        Check best direction to avoid being hit.
        """
        if not self.avoiding:
            if self.center_x + 100 >= SCREEN_WIDTH - MARGIN or self.center_x < self.dangerous.center_x:
                self.change_x = -SPACESHIP_STRAFE
            elif self.center_x < MARGIN + 100 or self.center_x > self.dangerous.center_x:
                self.change_x = SPACESHIP_STRAFE
            else:
                self.change_x = random.choice((SPACESHIP_SPEED, -SPACESHIP_SPEED))
        self.avoiding = True

    def maneuvre(self):
        """
        Makes ship doing random maneuvers to add a bit mess to hostiles movement.
        """
        min_distance, max_distance = hostiles[MIN_DISTANCE][self.model], hostiles[MAX_DISTANCE][self.model]
        target_x, target_y = (random.randint(MARGIN, SCREEN_WIDTH - MARGIN),
                              random.randint(SCREEN_HEIGHT * min_distance, SCREEN_HEIGHT * max_distance))
        self.targeted_position = (target_x, target_y)

        if abs(self.center_x - target_x) <= 50 and abs(self.center_y - target_y) < 50:
            self.targeted_position = False
            return

        if self.center_x < target_x:
            self.change_x = SPACESHIP_STRAFE
        elif self.center_x > target_x:
            self.change_x = -SPACESHIP_STRAFE

        if self.center_y < target_y:
            self.change_y = SPACESHIP_STRAFE
        elif self.center_y > target_y:
            self.change_y = -SPACESHIP_SPEED

    def aim_at_player(self):
        """
        Try to move Hostile left or right to position it just above player's ship.
        """
        if abs(self.center_x - self.player_x) > SPRITES_SCALE / 2:
            if self.center_x < self.player_x:
                self.change_x = SPACESHIP_STRAFE
            elif self.center_x > self.player_x:
                self.change_x = -SPACESHIP_STRAFE
        else:
            self.change_x = 0

    def handle_turrets(self):
        """
        If hostile ship has at least 1 turret object attached to it, handle their position, rotation and shooting at the
         player.
        """
        for i in range(len(self.turrets)):
            turret = self.turrets[i]
            # position:
            turret.center_x = self.center_x + turret.offset_x
            turret.center_y = self.center_y - turret.offset_y
            # rotation - aiming at player:
            radians = math.atan2(self.player_x - self.center_x, self.player_y - self.center_y)
            turret.angle = -math.degrees(radians)
            # shooting at player:
            if game.game_time - turret.last_shot > turret.rate_of_fire:
                self.turret_shot(turret)
                turret.last_shot = game.game_time

    @staticmethod
    def turret_shot(turret):
        """
        Each turret shots independently from it's ship.

        :param turret: Turret instance
        """
        play_sound(weapons[SOUNDS][turret.gun])
        shot = Projectile(turret.gun, 1, turret.angle, ["", turret.center_y, turret.center_x])
        game.projectiles.append(shot)

    def update_speed(self):
        """
        Each enemy ship has it's own speed modifier: self.speed which is used to modify base speed.
        """
        self.change_x *= self.speed
        self.change_y *= self.speed

    def kill(self):
        if self.turrets:
            for turret in self.turrets:
                turret.kill()

        super().kill()

        score = hostiles[SCORES][self.model]
        game.create_hint(str(score), self.center_x, self.center_y, 0, -5, GREEN, 12 + ((score / 10) % 10))
        game.score += score
        game.destroyed += 1

        self.spawn_powerup()

    def spawn_powerup(self):
        """
        Create new PowerUp instance when hostile spaceship is destroyed and additional conditions are met.
        """
        chance = (POWERUP_CHANCE
                  + hostiles[SCORES][self.model] / 10
                  - game.difficulty.value
                  + (game.game_time - PowerUp.last_spawn) / FPS)

        if random.randint(1, 100) <= chance:
            PowerUp(self.center_x, self.center_y)


class Projectile(SpaceObject):
    """
    Basic class for all kind of 'shots' fired  in game by the player and his enemies.
    """

    def __init__(self, type_: str, power: int, angle: float, gun_position: list):
        """
        Initialize new Projectile object, when player or enemy fires it's weapon.

        :param type_: str -- type of the shot
        :param power: float -- damage modifier
        :param angle: float -- angle the shot was fired
        :param gun_position: list [int, int] -- x and y coordinates of firing point
        """
        super().__init__("shots/" + type_, power)
        self.type_ = type_
        self.angle = angle
        self.target, self.marker = None, None
        self.damage = weapons[DAMAGES][type_]
        self.speed = weapons[SPEED][type_]
        self.center_x = gun_position[2]
        self.center_y = gun_position[1]
        self.change_x, self.change_y = self.calculate_speed_vector()

    def calculate_speed_vector(self):
        """
        Calculate proper elements of the speed vector of projectile fired from gun. Required for rotating turrets.

        :return: float, float -- x and y velocities
        """
        velocity = weapons[SPEED][self.type_]
        if 90 >= self.angle > 0:
            change_y = math.cos(math.radians(self.angle))
            change_x = -math.sin(math.radians(self.angle))
        else:
            change_y = math.cos(math.radians(self.angle))
            change_x = -math.sin(math.radians(self.angle))
        return change_x * velocity, change_y * velocity

    def update(self):
        super().update()
        # delete each projectile which goes off the screen:
        self.check_if_on_the_screen()

        if self.type_ in weapons[ROCKETS]:  # rockets are fancy - they turn!
            self.rocket_autoaim()

        self.check_for_hits()

    def draw(self):
        super().draw()
        if self.type_ in weapons[ROCKETS] and self.target:
            pass

    def rocket_autoaim(self):
        """
        Method used only by 'rockets'. They make turns towards enemies.
        """
        if not self.target and len(game.hostiles) > 0:  # acquire target if has any and there are possible targets
            if self.angle == UPWARD:  # if rocket fired by player
                # TODO: rockets ignoring targets already acquired by other rockets and take next one [ ]
                self.target = arcade.get_closest_sprite(self, game.hostiles)[0]  # closest enemy ship
            else:
                self.target = game.player

        if self.target:
            if self.center_x < self.target.center_x:  # making turns towards the target
                self.change_x = SPACESHIP_STRAFE
            elif self.center_x > self.target.center_x:
                self.change_x = -SPACESHIP_STRAFE

        if not self.marker:
            self.marker = True
            game.add_target_marker(self, self.target)

    def check_if_on_the_screen(self):
        """
        Destroy a Projectile if it went off the screen to save memory.
        """
        if 0 > self.center_y or self.center_y > SCREEN_HEIGHT or 0 > self.center_x or self.center_x > SCREEN_WIDTH:
            self.kill()

    def check_for_hits(self):
        """
        Check if a Projectile hit any hostile ship (if shot by player) or player ship (if shot by hostile ship). If so,
        deal the damage and destroy Projectile instance.
        """
        if self.type_.startswith("player"):
            hit_list = arcade.check_for_collision_with_list(self, game.hostiles)
        else:
            hit_list = arcade.check_for_collision_with_list(self, game.players)

        for hit in hit_list:
            hit.damage(self.damage)
            self.kill()
            break

    def kill(self):
        super().kill()


class Turret(SpaceObject):

    def __init__(self, filename: str, gun: str, offset_x: int, offset_y: int, rof: int, rot: int):
        """
        Initialize new Turret instance fo a Spaceship object.

        :param filename: str -- name o the turret
        :param gun: str -- name of the weapon model
        :param offset_x: int -- offset from ship.center_x in pixels
        :param offset_y: int -- offset from ship.center_y in pixels
        :param rof: int -- rate of fire
        :param rot: int -- rotation speed
        """
        super().__init__("hostiles/" + filename)
        self.gun = gun
        self.rate_of_fire = rof
        self.rotation_speed = rot
        self.last_shot = 0
        self.offset_x = offset_x
        self.offset_y = offset_y


class PowerUp(SpaceObject):
    """
    All kinds of collectible powerups available to use by player.
    """

    last_spawn = 0

    def __init__(self, pos_x: float, pos_y: float):
        self.type_ = random.choice(powerups)
        super().__init__("powerups/" + self.type_)
        self.center_x = pos_x
        self.center_y = pos_y
        self.change_y = -SPACESHIP_STRAFE
        PowerUp.last_spawn = game.game_time
        game.powerups.append(self)

    def update(self):
        super().update()
        if 0 > self.center_y:
            self.kill()

        if arcade.check_for_collision(self, game.player):
            play_sound(POWERUP_SOUND)
            game.player.apply_booster(self.type_)
            self.kill()


class Explosion(SpaceObject):
    """
    This object is spawned when something explodes.
    """

    def __init__(self, x, y):
        super().__init__("explosion/explosion0000")
        for i in range(40):
            if i < 10:
                zeros = "000"
            else:
                zeros = "00"
            tex = "explosion/explosion" + zeros + str(i)
            self.append_texture(arcade.load_texture(get_image_path(tex)))
        self.center_y = y
        self.center_x = x
        self.set_texture(0)
        self.detonation = int(game.game_time)
        play_sound(EXPLOSION)

    def update(self):
        super().update()
        tex_index = int(game.game_time - self.detonation)
        self.set_texture(tex_index)
        if tex_index == 39:
            self.kill()


class Game(arcade.Window):
    """
    Basic class creating main game window and managing the game.
    """

    def __init__(self, width, height, title, fullscreen, resizeable, test: bool = False):
        """
        Initialization of new game window and game logic.

        :param width: int -- vertical height of game window
        :param height: int -- horizontal size of game window
        :param title: str -- title of window displayed s window name
        :param fullscreen: bool -- if game should be started in full-screen mode
        :param resizeable: bool -- if player can resize the window
        """
        super().__init__(width, height, title, fullscreen, resizeable)
        self.in_menu = False  # game starts in the menu
        self.cursor = Cursor(self, GRAPHICS_PATH, "/cursors/cursor")
        self.menu = None
        arcade.set_background_color(BACKGROUND_COLOR)
        self.set_update_rate(1 / FPS)

        self.difficulty = SharedVariable(0, [])
        self.next_difficulty_raise = 0

        # Additional elements displayed on the screen:
        self.hints = None
        self.stars = None
        self.targets_markers = None

        self.cursors = None
        self.players = None
        self.hostiles = None
        self.projectiles = None
        self.powerups = None
        self.turrets = None
        self.explosions = None
        self.spritelists = None  # all the arcade.spriteLists would be put into the list

        self.player = None
        self.player_name = ""

        self.paused = False
        # we have two 'times' because we need to keep time updating when game is paused or in scores table
        self.game_time, self.pause_time, self.minutes, self.seconds = 0.0, 0.0, 0, 0

        self.shots_fired = 0
        self.hits = 0
        self.destroyed = 0
        self.score = 0

        self.best_scores = None
        self.should_display_scores = False
        self.new_score_index = None

        self.challenge_mode = True  # game mode in which stronger enemies are spawned in larger amounts when time flows
        self.god_mode = False

        if not test:
            self.setup_menus()

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def setup_menus(self):
        """
        Create new Menu object as current game menu.
        """
        # top-level menu:
        elements, background = self.create_main_menu()
        main_menu = SubMenu(name=MAIN_MENU, menu_elements=elements, background=background, main=True)
        # initialize Menu object and add all the SubMenus:
        self.menu = Menu(self, main_menu)
        # hwo-to-play instructions submenu:
        elements, background = self.create_instructions_submenu()
        instructions = SubMenu(name=INSTRUCTIONS_SUBMENU, menu_elements=elements, background=background)
        # game options submenu:
        elements = self.create_options_submenu()
        options = SubMenu(name=OPTIONS_SUBMENU, menu_elements=elements)
        self.menu.add_submenu(instructions)
        self.menu.add_submenu(options)
        self.in_menu = True

    def create_main_menu(self):
        """Generate top-level SubMenu."""
        # initialize Buttons which we require in our game main-menu:
        padding, pos_x, pos_y = MARGIN * 3, SCREEN_WIDTH / 2, SCREEN_HEIGHT
        start_game_button = Button("START GAME", pos_x, pos_y - padding, function=self.setup_new_game)
        game_options_button = Button("OPTIONS", pos_x, pos_y - (padding * 2), function=self.show_options_menu)
        how_to_play_button = Button("HOW TO PLAY", pos_x, pos_y - (padding * 3), function=self.show_instructions_menu)
        quit_game_button = Button("QUIT GAME", pos_x, pos_y - (padding * 4), function=arcade.close_window)
        # put them into the list which will be passed to the Menu class:
        elements = [start_game_button, game_options_button, how_to_play_button, quit_game_button]
        # create background image for our main menu:
        background = arcade.load_texture(GRAPHICS_PATH + "/menu/menu_background.jpg")
        return elements, background

    def create_instructions_submenu(self):
        """Generate game instructions SubMenu."""
        elements = [
            Button("BACK", MARGIN, SCREEN_HEIGHT - MARGIN, function=partial(self.menu.toggle_submenu, MAIN_MENU))]
        background = arcade.load_texture(GRAPHICS_PATH + "/menu/instruction_black.png")
        return elements, background

    def create_options_submenu(self):
        difficulty_slider = Slider(pos_x=SCREEN_WIDTH / 2, pos_y=SCREEN_HEIGHT / 2, variable=self.difficulty,
                                   variable_name="difficulty", variable_min=0, variable_max=10)
        elements = [
            Button("BACK", MARGIN, SCREEN_HEIGHT - MARGIN, function=partial(self.menu.toggle_submenu, MAIN_MENU)),
            difficulty_slider]
        return elements

    def setup_new_game(self):
        """
        Setup all game variables. Used when new game is started and when game is restarted after player's death.
        """
        self.in_menu = False

        self.hints = []
        self.stars = self.create_stars()
        self.targets_markers = []

        self.next_difficulty_raise = 30 * FPS

        self.players, self.hostiles, self.projectiles, self.powerups, self.turrets, self.explosions = \
            self.create_spritelists()
        self.spritelists = [self.players, self.hostiles, self.projectiles, self.powerups, self.turrets, self.explosions]

        self.player = self.spawn_player()
        self.player_name = ""

        self.paused = False
        self.game_time, self.pause_time, self.minutes, self.seconds = 0.0, 0.0, 0, 0

        self.shots_fired = 0
        self.hits = 0
        self.destroyed = 0
        self.score = 0
        self.best_scores = self.load_best_scores()

        self.should_display_scores = False
        self.new_score_index = None

        load_sounds()
        print(self.difficulty.value)

    def show_options_menu(self):
        """Navigate to the options section in game menu."""
        self.menu.toggle_submenu(OPTIONS_SUBMENU)

    def show_instructions_menu(self):
        """Navigate to the instructions how to play in game menu."""
        self.menu.toggle_submenu(INSTRUCTIONS_SUBMENU)

    def create_stars(self):
        """
        Generate 'stars' displayed in the background. Stars are points stored in the 3-levels structure. Main dict
        contains 4 dicts or each color o the stars and each o these dict contains 3-lists of stars of different sizes.

        :return: dict -- dict of 4 dicts (colors) of 3 lists (sizes) of stars (lists)
        """
        stars = {WHITE: {1: [], 2: [], 3: []}, BLUE: {1: [], 2: [], 3: []},
                 RED: {1: [], 2: [], 3: []}, YELLOW: {1: [], 2: [], 3: []}}
        for row in range(SCREEN_WIDTH):
            for i in range(STARS_DENSITY):
                new_star = self.create_star(row)
                stars[new_star[3]][new_star[2]].append(new_star)
        return stars

    @staticmethod
    def create_star(row: int):
        """
        Generate a single 'star' object to be added to the self.stars list - game background. Each 'star' is a list
        containing info about it's x, and y coordinates, star's size, and speed.

        :return: list -- star in format: [x, y, size, color, speed]
        """
        col = random.randint(0, SCREEN_WIDTH)
        size = random.choice(STAR_SIZES)
        color = random.choice(STARS_COLORS)
        speed = random.random()
        return [col, row, size, color, speed]

    def scroll_stars(self):
        """
        Scroll all the points of self.stars downward, and add new stars at the top (moving stars from the bottom of the
        screen to the top).
        """
        for color in self.stars:
            for size in self.stars[color]:
                for star in self.stars[color][size]:
                    star[1] -= BACKGROUND_SPEED * star[4]
                    if star[1] < 0: star[1] = SCREEN_HEIGHT + 1; star[0] = random.randint(0, SCREEN_WIDTH)

    def draw_stars(self):
        """Display 'stars" on the background, which are just 1px white dots."""
        for color in self.stars:
            for size in self.stars[color]:
                arcade.draw_points(self.stars[color][size], color, size)

    @staticmethod
    def create_spritelists():
        """
        Create empty arcade.SpriteList objects for each game sprite list required.ss

        :return: arcade.SpriteList objects
        """
        return (arcade.SpriteList(), arcade.SpriteList(), arcade.SpriteList(), arcade.SpriteList(), arcade.SpriteList(),
                arcade.SpriteList())

    def spawn_player(self):
        """
        Crate player spaceship instance and add it to the self.players spritelist.
        :return: PlayerShip instance
        """
        new_player = PlayerShip(player[TEXTURE])
        self.players.append(new_player)
        return new_player

    def spawn_hostile(self):
        """
        Create enemy spaceship and place it on the upper boundary of the screen. ALso put into the self.hostiles.
        """
        hostile = Hostile(self.difficulty.value)
        hostile.center_y = SCREEN_HEIGHT - MARGIN
        hostile.center_x = random.randint(MARGIN, SCREEN_WIDTH - MARGIN)
        hostile.angle = DOWNWARD
        self.hostiles.append(hostile)

    def not_enough_enemies(self):
        """
        Calculate if there is optimal amount of hostile ships on the screen.

        :return: bool -- should the game spawn new enemy?
        """
        max_rating = 5 + self.difficulty.value
        return sum([hostiles[RATINGS][hostile.model] for hostile in self.hostiles]) < max_rating

    def if_difficulty_to_low(self):
        """
        Check for the conditions of raising game difficulty.

        :return: bool -- if game difficulty should be raised
        """
        return self.difficulty.value <= len(hostiles[HOSTILES]) and self.game_time >= self.next_difficulty_raise

    def raise_difficulty(self):
        """
        Raise the level of self.difficulty by 1. Game difficulty changes power and amount of spawned enemies.
        """
        self.difficulty.value += 1
        self.next_difficulty_raise += self.next_difficulty_raise
        self.create_hint("ESCALATION!", pos_y=SCREEN_HEIGHT * 0.6, speed_y=-5, color=RED, size=30, time=2)

    def create_hint(self, text: str, pos_x: float = SCREEN_WIDTH / 2, pos_y: float = SCREEN_HEIGHT / 2,
                    speed_x: int = 0,
                    speed_y: int = 0, color: arcade.color = WHITE, size: int = 10, time: int = 1):
        """
        Create new 'hint'to be displayed on the screen during the game. Text should be short, since hints are displayed
        for short game_time. Hint is added to the self.hits list and each frame game iterates through this list and
        displays hints found there.

        :param text: str -- text of the hint, should be short!
        :param pos_x: float -- x position on the screen
        :param pos_y: float -- y position on the screen
        :param speed_x: float -- vertical movement of hint, positive is upward, negative is downward
        :param speed_y: float -- horizontal movement of hint, positive is right, negative is left
        :param color: arcade.color object -- color of the text (default is arcade.color.WHITE)
        :param size: int -- size of the font
        :param time: int -- time that hint would be displayed for, in seconds
        """
        self.hints.append([text, pos_x, pos_y, speed_x, speed_y, color, size, time * FPS])

    def update_hints(self):
        """
        Iterate through list of the hints and update their position on the screen and life-time parameter i it is largen
         than 0. Otherwise, remove the hint from the hints list.
        """
        for hint in self.hints:
            if hint[-1] > 0:
                hint[-1] -= 1
                if hint[3] != 0: hint[1] += hint[3]
                if hint[4] != 0: hint[2] += hint[4]
            else:
                self.hints.remove(hint)

    def display_hints(self):
        """
        Display all the hints on the hints list. It should be usually only one hint there. I not, make sure their x, and
        y (0 and 1) parameter are different, or they would overlap.
        """
        for hint in self.hints:
            arcade.draw_text(hint[0], hint[1], hint[2], hint[5], hint[6], align="center", anchor_x="center")

    def add_target_marker(self, rocket: Projectile = None, target: Hostile = None):
        """
        Register new target of player's rocket. It will be marked on the screen with red rectangle.

        :param rocket: Projectile instance -- player's rocket instance which marked that target
        :param target: Hostile instance -- enemy ship targeted by the rocket
        """
        if rocket is not None and target is not None:
            new_target = {"rocket": rocket, "target": target, "x": target.center_x, "y": target.center_y,
                          "width": target.width, "height": target.height}
            self.targets_markers.append(new_target)

    def update_targets_markers(self):
        """
        Change position of rectangular gizmos showing hostile ships targeted by player's rockets accordingly to their
        actual targets_markers x and y coordinates. If target does no longer exists or rocket which marked it went off
        the screen, delete this marker.
        """
        for target in self.targets_markers:
            if target["rocket"] in self.projectiles and target["target"] in self.hostiles:
                target["x"] = target["target"].center_x
                target["y"] = target["target"].center_y
            else:
                self.targets_markers.remove(target)

    def draw_targets_markers(self):
        """
        Display a red rectangle on the screen for each element found in self.targets_markers list. Rectangle is a marker
         for the hostile ships targeted by the player's rockets.
        """
        for target in self.targets_markers:
            arcade.draw_rectangle_outline(target["x"], target["y"], target["width"], target["height"], GREEN)

    def on_update(self, delta_time: float):
        """
        Update game logic.

        :param delta_time:
        """
        if self.in_menu:
            self.menu.update()
            self.cursor.on_update()
        if self.players:
            if not self.paused:
                self.game_time += 1
                self.minutes, self.seconds = int(self.game_time) // 60, self.game_time % 60

                if self.game_time % 90 == 0 and self.not_enough_enemies():
                    self.spawn_hostile()

                # TODO: spawning bosses [ ], raising difficulty [x][ ], laser overheating [ ]

                if self.challenge_mode and self.if_difficulty_to_low():
                    self.raise_difficulty()

                for sprite_list in self.spritelists:
                    if len(sprite_list) > 0:
                        sprite_list.update()

                if len(self.targets_markers) > 0 and self.game_time % 3 == 0: self.update_targets_markers()

                self.scroll_stars()

                self.update_hints()
            else:
                self.pause_time += 1

    def on_draw(self):
        """
        Draw all the in-game objects in the game window.
        """
        arcade.start_render()
        if self.in_menu:
            self.menu.draw()
            self.cursor.draw()
        else:
            if self.players:  # game is rendered only, if player is alive
                self.draw_stars()

                for sprite_list in self.spritelists:
                    sprite_list.draw()

                if len(self.targets_markers) > 0: self.draw_targets_markers()

                if len(self.hints) > 0: self.display_hints()

                self.draw_hud()

                if self.paused:
                    arcade.draw_text("PAUSED", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE_SMOKE, 24)
            else:
                if self.should_display_scores:
                    self.draw_scores_table()
                else:
                    self.endgame()

    def draw_hud(self):
        """
        Display hud information on the screen.
        """
        output = f"Fired shots: {self.shots_fired}, Hit enemies: {self.hits}, Destroyed: {self.destroyed}, " \
            f"Rockets: {self.player.rockets}, Shield: {self.player.shield}, Score: {self.score}"

        if self.god_mode: output += ", Godmode: on"

        arcade.draw_text(output, 10, 20, arcade.color.ANTIQUE_WHITE, 14)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """
        Ceases mouse-movements and handling to the Cursor.on_mouse_motion() method.

        :param float x: x position of mouse
        :param float y: y position of mouse
        :param float dx: Change in x since the last time this method was called
        :param float dy: Change in y since the last time this method was called
        """
        self.cursor.on_mouse_motion(x, y, self.in_menu)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """
        Ceases mouse-buttons handling to the Cursor.on_mouse_press() method.

        :param float x: x position of the mouse
        :param float y: y position of the mouse
        :param int button: What button was hit. One of: arcade.MOUSE_BUTTON_LEFT, arcade.MOUSE_BUTTON_RIGHT,
        arcade.MOUSE_BUTTON_MIDDLE
        :param int modifiers: Shift/click, ctrl/click, etc
        """
        self.cursor.on_mouse_press(button, self.in_menu)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """

        :param x:
        :param y:
        :param button:
        :param modifiers:
        """
        self.cursor.on_mouse_release(button, self.in_menu)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        """

        :param x:
        :param y:
        :param dx:
        :param dy:
        :param buttons:
        :param modifiers:
        """
        self.on_mouse_motion(x, y, dx, dy)
        self.cursor.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_key_press(self, key: int, modifiers: int):
        """
        Override this function to add key press functionality.

        :param int key: Key that was hit
        :param int modifiers: If it was shift/ctrl/alt
        """
        if not self.players:
            if self.should_display_scores:
                self.enter_player_name(key, modifiers)
            else:
                if key == arcade.key.ENTER:
                    self.save_best_scores()
                    self.setup_new_game()
                elif key == arcade.key.ESCAPE:
                    self.save_best_scores()
                    self.in_menu = True
        else:  # TODO: FIX STEERING!
            if key == arcade.key.P or key == arcade.key.PAUSE:
                self.toggle_pause()
            if not self.paused:
                if key == arcade.key.W or key == arcade.key.UP:
                    self.player.vertical = PlayerShip.UP
                if key == arcade.key.S or key == arcade.key.DOWN:
                    self.player.vertical = PlayerShip.DOWN
                if key == arcade.key.A or key == arcade.key.LEFT:
                    self.player.horizontal = PlayerShip.LEFT
                if key == arcade.key.D or key == arcade.key.RIGHT:
                    self.player.horizontal = PlayerShip.RIGHT
                if key == arcade.key.SPACE:
                    self.player.toggle_shooting()
                if key == arcade.key.R:
                    if self.player.rockets > 0:
                        self.player.launch_rocket()
                        self.shots_fired += 1
                if key == arcade.key.G:  # GOD MODE for testing
                    self.toggle_god_mode()

    def enter_player_name(self, key: int, modifier: int):
        """
        If we are in cores-table, convert user key-inputs to 'letters' and modify current player's name. Required for
        saving player's new high score.

        :param modifier: int -- special keys like ALT, SHIFT, CTRLss
        :param key: int -- key pressed
        """
        if key == arcade.key.BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif key == arcade.key.SPACE:
            self.player_name += " "
        elif key == arcade.key.ENTER:
            self.should_display_scores = False
        elif chr(key) in string.ascii_letters:
            self.player_name += chr(key).upper() if modifier == arcade.key.LSHIFT else chr(key)
        elif chr(key) in string.digits:
            self.player_name += chr(key)
        else:
            return

    def on_key_release(self, key: int, modifiers: int):
        """
        Handle releasing keyboard keys.

        :param int key: Key that was hit
        :param int modifiers: If it was shift/ctrl/alt
        """
        if not self.paused and self.players:
            if key == arcade.key.W or key == arcade.key.UP:
                self.player.vertical = PlayerShip.STOP
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.player.vertical = PlayerShip.STOP
            if key == arcade.key.A or key == arcade.key.LEFT:
                self.player.horizontal = PlayerShip.STOP
            if key == arcade.key.D or key == arcade.key.RIGHT:
                self.player.horizontal = PlayerShip.STOP
            if key == arcade.key.SPACE:
                self.player.toggle_shooting()

    def if_new_high_score(self):
        """
        Set up the boolean attribute self.should_display_score which is used to decide if best-scores table should be
        shown to the player after his death, so he can enter his own score, or not.
        """
        new_high_score, self.new_score_index = self.compare_with_best_scores(self.best_scores, self.score)
        if new_high_score:
            self.should_display_scores = True

    def update_scores(self, index: int = None):
        if index is not None:
            self.best_scores.inser(index, {"name": self.player_name, "score": self.score})
        else:
            self.best_scores.append({"name": self.player_name, "score": self.score})
            self.best_scores.sort(key=lambda x: x["score"])

    def draw_scores_table(self):
        """
        Draw best scores table on the screen and dialog to enter player's name to add his score.
        :return: str -- text output to be displayed on the screen
        """
        scores_table, tab, spaces, base_color = [], " " * 4, " " * (12 - len(self.player_name)), arcade.color.WHITE
        for i in range(len(self.best_scores)):
            if i == self.new_score_index:
                s = f"Player name: {self.best_scores[i]['name']}" + tab + f"Score: {self.best_scores[i]['score']}"
                scores_table.append([s, False])
                p = f"Your name: {self.player_name}" + spaces + f"Your score: {self.score}"
                scores_table.append([p, True])
            else:
                s = f"Player name: {self.best_scores[i]['name']}" + tab + f"Score: {self.best_scores[i]['score']}"
                scores_table.append([s, False])
        if len(scores_table) == 1:
            p = "Your name: {}".format(self.player_name) + spaces + "Your score: {}".format(self.score)
            scores_table.append([p, True])
        scores_table.reverse()

        for i in range(len(scores_table)):
            score = scores_table[i]
            color = base_color
            if score[1]:  # if it is a player's current score
                color = arcade.color.BRIGHT_GREEN
            arcade.draw_text(score[0], SCREEN_WIDTH * 0.4, SCREEN_HEIGHT * 0.8 - i * 30, color, 20)

    @staticmethod
    def compare_with_best_scores(best_scores: list, current_score: int):
        """
        Check if current score is good enough to enter best scores ever played. If so, save it to the file with Shelve
        module.

        :type current_score: int -- score achieved by current player in last game
        :type best_scores: list of dicts -- best scores in format: [{name: str, score: int}...]
        :return: bool, int -- if there is new  score and, index of player's score on the best scores-table list
        """
        new_score, highest_index = False, None  # important variables passed further
        for i in range(len(best_scores)):
            if current_score > best_scores[i]["score"]:
                new_score, highest_index = True, i
            else:
                break
        if len(best_scores) < 10 and not new_score:
            new_score = True
        return new_score, highest_index

    @staticmethod
    def load_best_scores(path: str = CONFIG_PATH, filename: str = SCORES_FILE):
        """
        Use Shelve module to unpack previously saved best scores in game.

        :return: list of dicts -- best scores in the game in format: [{name: str, score: int}...]
        """
        file_path = path + filename
        if not os.path.isfile(file_path):
            new_file = shelve.open(file_path)
            new_file["scores"] = []
            new_file.close()
        with shelve.open(file_path) as d:
            return d["scores"]

    def save_best_scores(self):
        """
        Save most actual version of best scores table to the Shelve file, including new score of current game.
        """
        self.best_scores.append({"name": self.player_name, "score": self.score})
        self.best_scores.sort(key=lambda x: x["score"])
        filename = CONFIG_PATH + SCORES_FILE
        file = shelve.open(filename)
        file["scores"] = self.best_scores if len(self.best_scores) < 11 else self.best_scores[-10:]
        file.close()
        self.endgame()

    def toggle_pause(self):
        """
        Change state of pause and reset pause timer.
        """
        self.pause_time = 0.0
        self.paused = not self.paused

    def toggle_god_mode(self):
        """
        Turn on/off god mode. For testing purpose.
        """
        self.god_mode = not self.god_mode
        self.player.health = math.inf if self.god_mode else 10

        state = "ON" if self.god_mode else "OFF"
        color = arcade.color.ANDROID_GREEN if self.god_mode else RED
        self.create_hint("GOD MODE " + state, color=color, size=20, time=1)

    @staticmethod
    def endgame():
        """
        When player dies, ad game ends, show proper hint to the player.
        """
        output = "GAME OVER!"
        arcade.draw_text(output, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.RED_DEVIL, 24)
        hint = "Press ENTER to restart, or ESC to quit..."
        arcade.draw_text(hint, SCREEN_WIDTH / 2, (SCREEN_HEIGHT / 2) - 30, arcade.color.RED_DEVIL, 12)


def run_game():
    """
    Actual entry point of the game.py required in case of initializing script from other script.
    """
    global game, player, hostiles, powerups, levels, weapons
    player, hostiles, powerups, levels, weapons = load_config_files()
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, False, True)
    arcade.run()


if __name__ == "__main__":
    run_game()
