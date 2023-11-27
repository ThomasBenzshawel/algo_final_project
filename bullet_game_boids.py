"""
Project modeled after basic set up from: https://api.arcade.academy/en/2.6.1/examples/sprite_bullets_aimed.html#sprite-bullets-aimed
Sprite Bullets

Simple program to show basic sprite usage.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_bullets_aimed
"""

# IMPORT LIBRARIES
from typing import Tuple
import arcade
import math
import os
import numpy as np

# SET SCALING VALUES
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.02
SPRITE_SCALING_LASER = 0.8
TILE_SCALING = 1

# SET ENEMY COUNT
COIN_COUNT = 50

# SET HEALTH & DAMAGE DATA
HEALTH_BAR_OFFSET = 32
BIRD_DAMAGE = -2
PLAYER_HEALTH = 100

# SET SCREEN
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprites, Bullets and boids Example"
window = None
COLLISION_THRESHOLD = 10

# SET SPEED VALUES
PLAYER_SPEED = 5
BULLET_SPEED = 10

# SET USED KEYS
MOVEMENT_KEYS = [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.UP, arcade.key.DOWN]
BULLET_SHOOTING_KEYS = [arcade.key.A, arcade.key.S, arcade.key.D, arcade.key.W]

# PLAYER ANIMATION SETTINGS
UPDATES_PER_FRAME = 5
RIGHT_FACING = 0
LEFT_FACING = 1


class PlayerCharacter(arcade.Sprite):
    """
    Represents player character.
    Based off of this tutorial: https://api.arcade.academy/en/stable/examples/sprite_move_animation.html

    :param arcade.Sprite: The player sprite.
    """
    def __init__(self, bar_list):
        """
        Initialize object.

        :param bar_list: Bars for healthbar.
        """

        # CALL PARENT
        super().__init__()

        # SET UP HEALTH
        self.health = PLAYER_HEALTH
        self.health_bar = HealthBar(self, bar_list, (self.center_x, self.center_y))

        # Default to face-right
        # DEFAULT CHARACTER TO FACE RIGHT
        self.character_face_direction = RIGHT_FACING

        # FLIPPING BETWEEN ANIMATION IMAGES
        self.cur_texture = 0

        # SCALE PLAYER
        self.scale = SPRITE_SCALING_PLAYER

        # ADJUST COLLISION BOX TO REMOVE EMPTY SPACE.
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]

        # LOAD SPRITES
        main_path = ":resources:images/animated_characters/robot/robot"

        # MAKE IDLE TEXTURE
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")

        # LOAD WALKING TEXTURES
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

    def update_animation(self, delta_time: float = 1 / 60):
        """
        Update character animation.

        :param delta_time: One second
        """
        # FLIP IMAGE BASED ON FACING DIRECTION
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # IDLE
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # MOVING
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]


class HealthBar:
    """
    Represents a bar which can display information about a sprite.
    TAKEN FROM https://api.arcade.academy/en/latest/examples/sprite_health.html

    :param Player owner: The owner of this indicator bar.
    :param arcade.SpriteList sprite_list: The sprite list used to draw the indicator bar components.
    :param Tuple[float, float] position: The initial position of the bar.
    :param arcade.Color full_color: The color of the bar.
    :param arcade.Color background_color: The background color of the bar.
    :param int width: The width of the bar.
    :param int height: The height of the bar.
    :param int border_size: The size of the bar's border.
    """

    def __init__(self,
                 owner: PlayerCharacter,
                 sprite_list: arcade.SpriteList,
                 position: Tuple[float, float] = (0, 0),
                 full_color: arcade.Color = arcade.color.GREEN,
                 background_color: arcade.Color = arcade.color.BLACK,
                 width: int = 100,
                 height: int = 4,
                 border_size: int = 4,) -> None:
        # Store the reference to the owner and the sprite list
        self.owner: PlayerCharacter = owner
        self.sprite_list: arcade.SpriteList = sprite_list

        # Set the needed size variables
        self._box_width: int = width
        self._box_height: int = height
        self._half_box_width: int = self._box_width // 2
        self._center_x: float = 0.0
        self._center_y: float = 0.0
        self._fullness: float = 0.0

        # CREATE BOXES TO MAKE HEALTH BAR
        self._background_box: arcade.SpriteSolidColor = arcade.SpriteSolidColor(self._box_width + border_size,
                                                                                self._box_height + border_size,
                                                                                background_color,)
        self._full_box: arcade.SpriteSolidColor = arcade.SpriteSolidColor(self._box_width,
                                                                          self._box_height,
                                                                          full_color,)
        self.sprite_list.append(self._background_box)
        self.sprite_list.append(self._full_box)

        # SET FULLNESS BASED OFF HEALTH
        self.fullness: float = 1.0
        self.position: Tuple[float, float] = position

    def __repr__(self) -> str:
        return f"<IndicatorBar (Owner={self.owner})>"

    @property
    def background_box(self) -> arcade.SpriteSolidColor:
        """Returns the background box of the indicator bar."""
        return self._background_box

    @property
    def full_box(self) -> arcade.SpriteSolidColor:
        """Returns the full box of the indicator bar."""
        return self._full_box

    @property
    def fullness(self) -> float:
        """Returns the fullness of the bar."""
        return self._fullness

    @fullness.setter
    def fullness(self, new_fullness: float) -> None:
        """Sets the fullness of the bar."""
        # Check if new_fullness if valid
        if not (0.0 <= new_fullness <= 1.0):
            raise ValueError(
                f"Got {new_fullness}, but fullness must be between 0.0 and 1.0."
            )

        # Set the size of the bar
        self._fullness = new_fullness
        if new_fullness == 0.0:
            # Set the full_box to not be visible since it is not full anymore
            self.full_box.visible = False
        else:
            # Set the full_box to be visible incase it wasn't then update the bar
            self.full_box.visible = True
            self.full_box.width = self._box_width * new_fullness
            self.full_box.left = self._center_x - (self._box_width // 2)

    @property
    def position(self) -> Tuple[float, float]:
        """Returns the current position of the bar."""
        return self._center_x, self._center_y

    @position.setter
    def position(self, new_position: Tuple[float, float]) -> None:
        """Sets the new position of the bar."""
        # Check if the position has changed. If so, change the bar's position
        if new_position != self.position:
            self._center_x, self._center_y = new_position
            self.background_box.position = new_position
            self.full_box.position = new_position

            # Make sure full_box is to the left of the bar instead of the middle
            self.full_box.left = self._center_x - (self._box_width // 2)


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.

    :param filename: The texture file.
    """
    return [arcade.load_texture(filename),
            arcade.load_texture(filename, flipped_horizontally=True)]


def new_flock(count, lower_limits, upper_limits):
    width = upper_limits - lower_limits
    return lower_limits[:, np.newaxis] + np.random.rand(2, count) * width[:, np.newaxis]


class MyGame(arcade.Window):
    """
    Main application class.

    :param arcade.Window: The window the game is displayed on.
    """

    def __init__(self):
        """
        Initializer.
        """
        # PARENT CLASS INITIALIZER
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # SPRITE LISTS
        self.bar_list = None
        self.player_list = None
        self.coin_list = None
        self.bullet_list = None
        self.scene_list = None

        # MOVEMENT KEY
        self.current_key = None

        # BOID INFO
        self.positions = None
        self.velocities = None

        # PLAYER INFO
        self.player_sprite = None
        self.score = 0
        self.score_text = None

        # SOUNDS
        # TODO - CHECK
        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser1.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/phaseJump1.wav")

        # SCENE DESIGN
        self.tile_map = None
        self.scene = None
        self.my_map = None
        self.physics_engine = None
        # arcade.set_background_color(arcade.color.AMAZON)
        # self.background = None

    def setup(self):
        """
        Set up the game and initialize the variables.
        """
        # # SET BACKGROUND
        # layer_options = {
        #     "Plants" : {"use_spacial_hash" : True},
        #     "Buildings" : {"use_spacial_hash" : True}
        # }
        # self.my_map = tile_map.load_tilemap("maps/map.json", scaling = 2.5, use_spatial_hash = True)
        # self.scene = arcade.Scene.from_tilemap(self.my_map)
        layer_options = {"Buildings": { "use_spatial_hash": True,},}

        self.tile_map = arcade.load_tilemap("maps/map.tmj", TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant = 2, walls = self.scene["Buildings"]
        )

        # self.background = arcade.load_texture("images/background.png")

        # SPRITE LISTS
        self.bar_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.scene_list = arcade.SpriteList()

        # RESET SCORE
        self.score = 0

        # Image from kenney.nl "
        self.player_sprite = PlayerCharacter(self.bar_list)
        self.player_sprite.center_x = 300
        self.player_sprite.center_y = 150
        self.player_list.append(self.player_sprite)

        # RANDOM POSITIONS FOR BOIDS
        self.positions = new_flock(COIN_COUNT, np.array([0, 0]), np.array([SCREEN_WIDTH, SCREEN_HEIGHT]))

        self.velocities = new_flock(COIN_COUNT, np.array([0, -5]), np.array([2, 3]))

        # Create the coins
        for i in range(len(self.positions[0])):
            # Create the coin instance
            # Coin image from kenney.nl
            # coin = arcade.Sprite(":resources:images/items/coinGold.png", SPRITE_SCALING_COIN)
            coin = arcade.Sprite("images/bird.gif", SPRITE_SCALING_COIN)

            # Position the coin
            coin.center_x = self.positions[0][i]
            coin.center_y = self.positions[1][i]

            # Add the coin to the lists
            self.coin_list.append(coin)

        # STORE WHERE ITEMS ARE ON SCREEN
        buildings1 = arcade.Sprite("images/black.png", 1)
        buildings1.center_x = 120
        buildings1.center_y = 315
        buildings1.set_hit_box([(0, 350), (225, 350), (225, 275), (0, 275)])

        buildings2 = arcade.Sprite("images/black.png", 2)
        buildings2.center_x = 600
        buildings2.center_y = 500
        buildings2.set_hit_box([(375, 585), (800, 585), (800, 425), (375, 425)])

        buildings3 = arcade.Sprite("images/black1.png", 1.25)
        buildings3.center_x = 150
        buildings3.center_y = 500
        buildings3.set_hit_box([(75, 550), (225, 550), (225, 450), (75, 450)])

        buildings4 = arcade.Sprite("images/black1.png", .75)
        buildings4.center_x = 410
        buildings4.center_y = 295
        buildings4.set_hit_box([(365, 325), (455, 325), (455, 268), (365, 268)])

        buildings5 = arcade.Sprite("images/black1.png", 1.25)
        buildings5.center_x = 125
        buildings5.center_y = 150
        buildings5.set_hit_box([(50, 200), (200, 200), (200, 100), (50, 100)])

        trees1 = arcade.Sprite("images/black1.png", 3)
        trees1.center_x = 700
        trees1.center_y = 85
        trees1.set_hit_box([(520, 200), (800, 200), (800, 0), (520, 0)])

        trees2 = arcade.Sprite("images/black.png", 4)
        trees2.center_x = 300
        trees2.center_y = -55
        trees2.set_hit_box([(0, 100), (800, 100), (800, 0), (0, 0)])

        trees3 = arcade.Sprite("images/black.png", 4)
        trees3.center_x = 360
        trees3.center_y = 700
        trees3.set_hit_box([(0, 600), (800, 600), (800, 550), (0, 550)])

        trees4 = arcade.Sprite("images/black1.png", 2)
        trees4.center_x = 800
        trees4.center_y = 450
        trees4.set_hit_box([(675, 600), (800, 600), (800, 375), (675, 375)])

        trees5 = arcade.Sprite("images/black1.png", 2)
        trees5.center_x = 850
        trees5.center_y = 325
        trees5.set_hit_box([(725, 800), (600, 800), (600, 250), (725, 250)])

        # TESTER
        # dot = arcade.Sprite("images/dot.png", .01)
        # dot.center_x = 100
        # dot.center_y = 600

        trees6 = arcade.Sprite("images/black1.png", 6)
        trees6.center_x = -275
        trees6.center_y = 325
        trees6.set_hit_box([(0, 600), (100, 600), (100, 0), (0, 0)])

        # ADD UNMOVABLE AREAS
        self.scene_list.append(buildings1)
        self.scene_list.append(buildings2)
        self.scene_list.append(buildings3)
        self.scene_list.append(buildings4)
        self.scene_list.append(buildings5)
        self.scene_list.append(trees1)
        self.scene_list.append(trees2)
        self.scene_list.append(trees3)
        self.scene_list.append(trees4)
        self.scene_list.append(trees5)
        self.scene_list.append(trees6)
        # self.scene_list.append(dot)

    def on_draw(self):
        """
        Render the screen.
        """
        # START RENDERING PROCESS
        self.clear()
        arcade.start_render()

        # DRAW BACKGROUND
        self.scene.draw()
        # arcade.draw_lrwh_rectangle_textured(0, 0,
        #                                     SCREEN_WIDTH, SCREEN_HEIGHT,
        #                                     self.background)

        # DRAW ALL SPRITES
        self.coin_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()
        self.bar_list.draw()
        #self.scene_list.draw()

        # PUT SCORE ON THE SCREEN
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse button is clicked.
        TODO -- REMOVE??
        """
        # Create a bullet
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png",
                               SPRITE_SCALING_LASER)

        # Position the bullet at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # Get from the mouse the destination location for the bullet
        dest_x = x
        dest_y = y

        # Calculate how to get the bullet to the destination.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Set the bullet's angle and velocity
        bullet.angle = math.degrees(angle)
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        # Add the bullet to the appropriate lists
        self.bullet_list.append(bullet)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed. Perform the corresponding actions.

        :param self: TODO
        :param key: The key that was pressed on the keyboard.
        :param modifiers: TODO
        """
        # Check if the pressed key is an arrow key
        if key in MOVEMENT_KEYS:
            self.current_key = key

            # Schedule the movement update function to run continuously
            if key == arcade.key.LEFT:
                arcade.schedule(self.check_and_move, 1 / 60)
            elif key == arcade.key.RIGHT:
                arcade.schedule(self.check_and_move, 1 / 60)
            elif key == arcade.key.UP:
                arcade.schedule(self.check_and_move, 1 / 60)
            elif key == arcade.key.DOWN:
                arcade.schedule(self.check_and_move, 1 / 60)

        # SHOOT BULLETS WITH A,S,D,W KEYS
        elif key in BULLET_SHOOTING_KEYS:
            if key == arcade.key.A:
                self.shoot_bullet(180)  # shoot left
            elif key == arcade.key.D:
                self.shoot_bullet(0)  # shoot right
            elif key == arcade.key.W:
                self.shoot_bullet(90)  # shoot up
            elif key == arcade.key.S:
                self.shoot_bullet(-90)  # shoot down

    def on_key_release(self, key, modifiers):
        """
        Called whenever a key is released. Perform the corresponding actions.

        :param self: TODO
        :param key: The key that was pressed on the keyboard.
        :param modifiers: TODO
        """
        # Stop the scheduled movement update function when the key is released
        if key in MOVEMENT_KEYS:
            self.current_key = None
            arcade.unschedule(self.check_and_move)

    def check_and_move(self, delta_time):
        """
        Function to check for collisions and move the sprite continuously.

        :param delta_time: Time since the last update.
        """
        l_valid = False
        r_valid = False
        d_valid = False
        u_valid = False

        # Calculate the next position based on the current movement direction
        if self.current_key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_SPEED  # move left
        elif self.current_key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_SPEED
        elif self.current_key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_SPEED  # move down
        elif self.current_key == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_SPEED  # move up

    def on_update(self, delta_time):

        self.update_boids(self.positions, self.velocities)

        for i, coin in enumerate(self.coin_list):
            # Position the coin
            coin.center_x = self.positions[0][i]
            coin.center_y = self.positions[1][i]

        # UPDATE PLAYER LOCATION
        self.player_list.update()
        self.player_sprite.health_bar.position = (self.player_sprite.center_x,
                                                  self.player_sprite.center_y + HEALTH_BAR_OFFSET,)

        # UPDATE PLAYER ANIMATION
        self.player_list.update_animation()

        # ADD ALL BULLET SPRITES
        self.bullet_list.update()

        # CHECK IF A BULLET HIT AN ENEMY
        for bullet in self.bullet_list:
            # CHECK IF A ENEMY WAS HIT
            hit_list = arcade.check_for_collision_with_list(bullet, self.coin_list)

            # REMOVE BULLET IF CONTACT
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # UPDATE SCORE
            # TODO -- UPDATE
            for coin in hit_list:
                coin.remove_from_sprite_lists()
                self.score += 1

            # REMOVE BULLET IF OFF OF SCREEN
            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()

        # CHECK IF ENEMY HIT PLAYER
        for coin in self.coin_list:
            attack_list = arcade.check_for_collision_with_list(coin, self.player_list)

            # ADJUST HEALTH FOR EACH HIT
            if len(attack_list) > 0:
                self.player_sprite.health = self.player_sprite.health + (BIRD_DAMAGE * len(attack_list))

                # CHECK IF PLAYER IS DEAD, IF NOT UPDATE HEALTH BAR
                if self.player_sprite.health <= 0:
                    # arcade.exit()
                    self.player_sprite.health_bar.fullness = (0 / PLAYER_HEALTH)
                else:
                    self.player_sprite.health_bar.fullness = (self.player_sprite.health / PLAYER_HEALTH)

    def shoot_bullet(self, angle):
        """
        Helper method to shoot a bullet in the specified angle.

        :param angle: The direction the bullet goes.
        """
        # CREATE BULLET
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png",
                               SPRITE_SCALING_LASER)

        # START BULLET AT PLAYER POSITION
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # SET ANGLE
        bullet.angle = angle

        # CALCULATE LOCATION BASED ON ANGLE
        bullet.change_x = math.cos(math.radians(angle)) * BULLET_SPEED
        bullet.change_y = math.sin(math.radians(angle)) * BULLET_SPEED

        # ADD BULLET TO BULLET SPRITE LIST
        self.bullet_list.append(bullet)

    def update_boids(self, positions, velocities):
        for i in range(len(velocities[0])):

            if positions[0][i] < self.player_sprite.center_x:
                velocities[0][i] = velocities[0][i] + .5
            elif positions[0][i] > self.player_sprite.center_x:
                velocities[0][i] = velocities[0][i] - .5

            if positions[1][i] < self.player_sprite.center_y:
                velocities[1][i] = velocities[1][i] + .5
            elif positions[1][i] > self.player_sprite.center_y:
                velocities[1][i] = velocities[1][i] - .5

        move_to_middle_strength = 0.005
        middle = np.mean(positions, 1)
        direction_to_middle = positions - middle[:, np.newaxis]
        velocities -= direction_to_middle * move_to_middle_strength

        separations = positions[:, np.newaxis, :] - positions[:, :, np.newaxis]
        squared_displacements = separations * separations
        square_distances = np.sum(squared_displacements, 0)
        alert_distance = 200
        far_away = square_distances > alert_distance
        separations_if_close = np.copy(separations)
        separations_if_close[0, :, :][far_away] = 0
        separations_if_close[1, :, :][far_away] = 0
        velocities += np.sum(separations_if_close, 1)

        velocity_differences = velocities[:, np.newaxis, :] - velocities[:, :, np.newaxis]
        formation_flying_distance = 100000
        formation_flying_strength = 0.075
        very_far = square_distances > formation_flying_distance
        velocity_differences_if_close = np.copy(velocity_differences)
        velocity_differences_if_close[0, :, :][very_far] = 0
        velocity_differences_if_close[1, :, :][very_far] = 0
        velocities -= np.mean(velocity_differences_if_close, 1) * formation_flying_strength

        positions += velocities


def main():
    """
    Run application.
    """
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()

#%%