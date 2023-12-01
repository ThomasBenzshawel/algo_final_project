"""
Project modeled after basic set up from: https://api.arcade.academy/en/2.6.1/examples/sprite_bullets_aimed.html#sprite-bullets-aimed
Sprite Bullets

Simple program to show basic sprite usage.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_bullets_aimed
"""

# IMPORT LIBRARIES
import random
import arcade
import math
import os

# SET SCALING VALUES
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.2
SPRITE_SCALING_LASER = 0.8

# SET ENEMY COUNT
COIN_COUNT = 50

# SET SCREEN
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprites and Bullets Example"
window = None

# SET SPEED VALUES
PLAYER_SPEED = 5
BULLET_SPEED = 5

# SET USED KEYS
MOVEMENT_KEYS = [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.UP, arcade.key.DOWN]
BULLET_SHOOTING_KEYS = [arcade.key.A, arcade.key.S, arcade.key.D, arcade.key.W]


class MyGame(arcade.Window):
    """
    Main application class.
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
        self.player_list = None
        self.coin_list = None
        self.bullet_list = None

        # PLAYER INFO
        self.player_sprite = None
        self.score = 0
        self.score_text = None

        # SOUNDS
        # Sounds from kenney.nl
        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser1.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/phaseJump1.wav")

        # SET BACKGROUND COLOR
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """
        Set up the game and initialize the variables.
        """
        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # RESET SCORE
        self.score = 0

        # Image from kenney.nl
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 70
        self.player_list.append(self.player_sprite)

        # Create the coins
        for i in range(COIN_COUNT):
            # Create the coin instance
            # Coin image from kenney.nl
            coin = arcade.Sprite(":resources:images/items/coinGold.png", SPRITE_SCALING_COIN)

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(120, SCREEN_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        """
        Render the screen.
        """
        # START RENDERING PROCESS
        arcade.start_render()

        # DRAW ALL SPRITES
        self.coin_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()

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
        # PLAYER MOVES WITH ARROW KEYS
        if key in MOVEMENT_KEYS:
            if key == arcade.key.LEFT:
                self.player_sprite.change_x = -5  # move left
            elif key == arcade.key.RIGHT:
                self.player_sprite.change_x = 5  # move right
            elif key == arcade.key.UP:
                self.player_sprite.change_y = 5  # move up
            elif key == arcade.key.DOWN:
                self.player_sprite.change_y = -5  # move down

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
        # STOP PLAYER MOVEMENT
        if key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.player_sprite.change_x = 0  # stop moving horizontally
        elif key in [arcade.key.UP, arcade.key.DOWN]:
            self.player_sprite.change_y = 0  # stop moving vertically

    def on_update(self, delta_time):
        """
        Movement and game logic

        :param delta_time: TODO
        """
        # UPDATE PLAYER LOCATION
        self.player_sprite.center_x += self.player_sprite.change_x
        self.player_sprite.center_y += self.player_sprite.change_y

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


def main():
    """
    Run application.
    """
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
