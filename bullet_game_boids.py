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
SPRITE_SCALING_BIRD = 0.02
SPRITE_SCALING_LASER = 0.8
TILE_SCALING = 1

# SET ENEMY COUNT
BIRD_COUNT = 15

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

        # LOAD SPRITES
        main_path = ":resources:images/animated_characters/robot/robot"

        # MAKE IDLE TEXTURE
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")

        # LOAD WALKING TEXTURES
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # ADJUST COLLISION BOX TO REMOVE EMPTY SPACE.
        self.width = 24
        self.height = 48
        # self.points = [[-22, -64], [22, -64], [22, -86], [-22, -86]]
        # self.set_hit_box(self.points)

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


#TODO UPDATE
def new_flock(count, lower_limits, upper_limits):
    width = upper_limits - lower_limits
    # MAKE THE ARRAYS THE NUMPY WAY
    x_and_y = lower_limits[:, np.newaxis] + np.random.rand(2, count) * width[:, np.newaxis]

    # Split them into (x, y) tuples
    position_list = []
    for i in range(len(x_and_y[0])):
        x = x_and_y[0][i]
        y = x_and_y[1][i]
        
        position_list.append([x, y])
        
    return position_list


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
        self.boid_list = None
        self.bullet_list = None
        self.scene_list = None

        # MOVEMENT KEY
        self.current_key = None

        # BOID INFO
        self.velocities = None

        # PLAYER INFO
        self.player_sprite = None
        self.score = 0
        self.score_text = None

        # SCENE DESIGN
        self.tile_map = None
        self.scene = None
        self.my_map = None
        self.physics_engine = None

    def setup(self):
        """
        Set up the game and initialize the variables.
        """
        # SPRITE LISTS
        self.bar_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.boid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.scene_list = arcade.SpriteList()

        # RESET SCORE
        self.score = 0

        # PLAYER
        self.player_sprite = PlayerCharacter(self.bar_list)
        self.player_sprite.center_x = 300
        self.player_sprite.center_y = 150
        self.player_list.append(self.player_sprite)

        # BACKGROUND
        layer_options = {
            "Buildings": {
                "use_spatial_hash": True,
            },
            "Plants": {
                "use_spatial_hash": True,
            },
            "TreeR1": {
                "use_spatial_hash": True,
            },
            "TreeR2": {
                "use_spatial_hash": True,
            },
            "TreeR3": {
                "use_spatial_hash": True,
            },
            "TreeR4": {
                "use_spatial_hash": True,
            },
            "TreeR5": {
                "use_spatial_hash": True,
            },
            "TreeR6": {
                "use_spatial_hash": True,
            },
            "TreeR7": {
                "use_spatial_hash": True,
            },
            "TreeR8": {
                "use_spatial_hash": True,
            },
            "TreeR9": {
                "use_spatial_hash": True,
            },
            "TreeR10": {
                "use_spatial_hash": True,
            },
            "TreeR11": {
                "use_spatial_hash": True,
            },
            "TreeR12": {
                "use_spatial_hash": True,
            },
            "TreeR13": {
                "use_spatial_hash": True,
            },
            "TreeR14": {
                "use_spatial_hash": True,
            },
            "TreeR15": {
                "use_spatial_hash": True,
            },
            "TreeR816": {
                "use_spatial_hash": True,
            },
            "TreeR17": {
                "use_spatial_hash": True,
            },
            "TreeR818": {
                "use_spatial_hash": True,
            },
        }
        self.tile_map = arcade.load_tilemap("maps/map.tmj", TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # RANDOM POSITIONS FOR BOIDS
        positions = new_flock(BIRD_COUNT, np.array([0, 0]), np.array([SCREEN_WIDTH, SCREEN_HEIGHT]))
        self.velocities = new_flock(BIRD_COUNT, np.array([0, -5]), np.array([2, 3]))

        # CREATE BOIDS
        for loc in positions:
            # CREATE BOID
            boid = arcade.Sprite("images/bird.gif", SPRITE_SCALING_BIRD)

            # POSITION
            boid.center_x = loc[0]
            boid.center_y = loc[1]

            # STORE BOID
            self.boid_list.append(boid)

        # STORE WHERE ITEMS ARE ON SCREEN
        buildings1 = arcade.Sprite("images/black.png")
        buildings1.center_x = 80
        buildings1.center_y = 315
        self.scene_list.append(buildings1)

        buildings2 = arcade.Sprite("images/black.png", 2)
        buildings2.center_x = 670
        buildings2.center_y = 520
        self.scene_list.append(buildings2)

        buildings3 = arcade.Sprite("images/black1.png", 1)
        buildings3.center_x = 110
        buildings3.center_y = 500
        self.scene_list.append(buildings3)

        buildings4 = arcade.Sprite("images/black1.png", .75)
        buildings4.center_x = 465
        buildings4.center_y = 320
        self.scene_list.append(buildings4)

        buildings5 = arcade.Sprite("images/black1.png", 1.75)
        buildings5.center_x = 140
        buildings5.center_y = 175
        self.scene_list.append(buildings5)

        trees1 = arcade.Sprite("images/black1.png", 2)
        trees1.center_x = 700
        trees1.center_y = 75
        self.scene_list.append(trees1)

        trees2 = arcade.Sprite("images/black.png", 4)
        trees2.center_x = 300
        trees2.center_y = -55
        self.scene_list.append(trees2)

        trees3 = arcade.Sprite("images/black.png", 4)
        trees3.center_x = 360
        trees3.center_y = 700
        self.scene_list.append(trees3)

        trees4 = arcade.Sprite("images/black1.png", 4)
        trees4.center_x = 985
        trees4.center_y = 350
        self.scene_list.append(trees4)

        trees5 = arcade.Sprite("images/black1.png", 6)
        trees5.center_x = -350
        trees5.center_y = 325
        self.scene_list.append(trees5)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.scene_list,
                                                             gravity_constant=0)

    def on_draw(self):
        """
        Render the screen.
        """
        # START RENDERING PROCESS
        self.clear()
        arcade.start_render()

        # DRAW BACKGROUND
        self.scene.draw()

        # DRAW ALL SPRITES
        self.boid_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()
        self.bar_list.draw()

        for sprite in self.scene_list:
            arcade.draw_rectangle_outline(
                sprite.center_x,
                sprite.center_y,
                sprite.width,
                sprite.height,
                arcade.color.RED
            )

        for sprite in self.player_list:
            arcade.draw_rectangle_outline(
                sprite.center_x,
                sprite.center_y,
                sprite.width,
                sprite.height,
                arcade.color.PURPLE
            )

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

        :param key: The key that was pressed on the keyboard.
        """
        # MOVE WITH ARROW KEYS
        if key in MOVEMENT_KEYS:
            self.current_key = key
            if key == arcade.key.LEFT:
                self.player_sprite.change_x = -PLAYER_SPEED  # move left
            elif key == arcade.key.RIGHT:
                self.player_sprite.change_x = PLAYER_SPEED  # move right
            elif key == arcade.key.DOWN:
                self.player_sprite.change_y = -PLAYER_SPEED  # move down
            elif key == arcade.key.UP:
                self.player_sprite.change_y = PLAYER_SPEED  # move up

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
        # STOP MOVEMENT
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

        self.current_key = None

    def on_update(self, delta_time):

        boid_collide_list = []
        for boid in self.boid_list:
            boid_collide_list.append(arcade.check_for_collision_with_list(boid, self.scene_list))


        if len(boid_collide_list) == 0:
            self.update_boids(self.boid_list, self.velocities)
        else:
            self.update_boids(self.boid_list, self.velocities)


        # UPDATE PLAYER LOCATION
        collide_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene_list)

        if len(collide_list) == 0:
            self.player_list.update()
            self.player_sprite.health_bar.position = (self.player_sprite.center_x,
                                                      self.player_sprite.center_y + HEALTH_BAR_OFFSET,)
        else:
            collision_locations = [(sprite.center_x, sprite.center_y) for sprite in collide_list]
            print(f"Player Position Before: ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
            print(collision_locations[0][1])
            print(collision_locations)

            if self.player_sprite.change_y < 0 and self.player_sprite.center_y > collision_locations[0][1]:  # trying to move down
                self.player_sprite.center_y += 20
            elif self.player_sprite.change_y > 0 and self.player_sprite.center_y < collision_locations[0][1]: # trying to move up
                self.player_sprite.center_y -= 20
            elif self.player_sprite.change_x < 0 and self.player_sprite.center_x > collision_locations[0][0]:  # trying to left
                self.player_sprite.center_x += 20
            elif self.player_sprite.change_x > 0 and self.player_sprite.center_y < collision_locations[0][0]: # trying to right
                self.player_sprite.center_x -= 20

        # UPDATE PLAYER ANIMATION
        self.player_list.update_animation()

        # ADD ALL BULLET SPRITES
        self.bullet_list.update()

        # CHECK IF A BULLET HIT AN ENEMY
        for bullet in self.bullet_list:
            # CHECK IF A ENEMY WAS HIT
            hit_list = arcade.check_for_collision_with_list(bullet, self.boid_list)

            # REMOVE BULLET IF CONTACT
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # UPDATE SCORE
            for boid in hit_list:

                for i, boid2 in enumerate(self.boid_list):
                    if boid.center_y == boid2.center_y and boid.center_x == boid2.center_x:
                        del self.velocities[i]
                        print(self.velocities)


                boid.remove_from_sprite_lists()


                self.score += 1

            # REMOVE BULLET IF OFF OF SCREEN
            if bullet.bottom > self.width or bullet.top < 0 or bullet.right < 0 or bullet.left > self.width:
                bullet.remove_from_sprite_lists()

        # CHECK IF ENEMY HIT PLAYER
        for boid in self.boid_list:
            attack_list = arcade.check_for_collision_with_list(boid, self.player_list)

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

    def update_boids(self, boids, velocities):
        positions_list = []
        x_positions = []
        y_positions = []

        velocities_list = []
        x_velocities = []
        y_velocities = []

        for boid, velocity in zip(boids, velocities):
            position = [boid.center_x, boid.center_y]

            if position[0] < self.player_sprite.center_x:
                velocity[0] = velocity[0] + .2
            elif position[0] > self.player_sprite.center_x:
                velocity[0] = velocity[0] - .2

            if position[1] < self.player_sprite.center_y:
                velocity[1] = velocity[1] + .2
            elif position[1] > self.player_sprite.center_y:
                velocity[1] = velocity[1] - .2

            x_positions.append(position[0])
            x_velocities.append(velocity[0])

            y_positions.append(position[1])
            y_velocities.append(velocity[1])

        positions_list.append(np.array(x_positions))
        positions_list.append(np.array(y_positions))
        positions_list = np.array(positions_list)

        velocities_list.append(np.array(x_velocities))
        velocities_list.append(np.array(y_velocities))
        velocities_list = np.array(velocities_list)




        move_to_middle_strength = 0.01
        alert_distance = 300
        formation_flying_distance = 100000
        formation_flying_strength = 0.05

        middle = np.mean(positions_list, 1)
        direction_to_middle = positions_list - middle[:, np.newaxis]
        velocities_list -= direction_to_middle * move_to_middle_strength

        separations = positions_list[:, np.newaxis, :] - positions_list[:, :, np.newaxis]
        squared_displacements = separations * separations
        square_distances = np.sum(squared_displacements, 0)

        far_away = square_distances > alert_distance
        separations_if_close = np.copy(separations)
        separations_if_close[0, :, :][far_away] = 0
        separations_if_close[1, :, :][far_away] = 0
        velocities_list += np.sum(separations_if_close, 1)

        velocity_differences = velocities_list[:, np.newaxis, :] - velocities_list[:, :, np.newaxis]

        very_far = square_distances > formation_flying_distance
        velocity_differences_if_close = np.copy(velocity_differences)
        velocity_differences_if_close[0, :, :][very_far] = 0
        velocity_differences_if_close[1, :, :][very_far] = 0
        velocities_list -= np.mean(velocity_differences_if_close, 1) * formation_flying_strength

        positions_list += velocities_list

        positions = []
        velocities = []
        for i, boid in enumerate(self.boid_list):
            x = positions_list[0][i]
            y = positions_list[1][i]

            boid.center_x = x
            boid.center_y = y

            x_vel = velocities_list[0][i]
            y_vel = velocities_list[1][i]

            positions.append([x, y])
            velocities.append([x_vel, y_vel])

        self.velocities = velocities

def main():
    """
    Run application.
    """
    game = MyGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
