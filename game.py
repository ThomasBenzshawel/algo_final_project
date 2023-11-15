"""
Platformer Game
"""
import arcade

# GAME CONSTANTS
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
PLAYER_MOVEMENT_SPEED = 10  # pixels per frame
GRAVITY = 1
PLAYER_JUMP_SPEED = 20 # pixels per frame


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        """
        Create game object.
        """

        # CALL PARENT TO SET UP WINDOW
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # DEFAULT SCENE, PLAYER SPRITE, PHYSICS, AND CAMERA TO NONE
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None

        # CHANGE BACKGROUND COLOR TO BLUE
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """
        Set up the game here. Call this function to restart the game.
        """
        # CREATE CAMERA
        self.camera = arcade.Camera(self.width, self.height)

        # GET SCENE OBJECT
        self.scene = arcade.Scene()

        # ADD PLAYER AND WALLS TO SCENE
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash = True)

        # CREATE CHARACTER SPRITE
        image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        # CREATE WALL SPRITE(S)
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        # CREATE CRATE SPRITES
        coordinate_list = [[512, 96], [256, 96], [768, 96]]
        for coordinate in coordinate_list:
            # Add a crate on the ground
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", TILE_SCALING)
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        # SET PHYSICS ENGINE
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.scene.get_sprite_list("Walls"),
                                                             GRAVITY)

        pass

    def on_update(self, delta_time):
        """
        Movement and game logic.
        """

        # MOVE PLAYER BASED ON PHYSICS
        self.physics_engine.update()

        # POSITION CAMERA ON PLAYER
        self.center_camera_to_player()

    def on_draw(self):
        """
        Render the screen.
        """
        # CLEAR SCREEN TO BACKGROUND COLOR
        arcade.start_render()

        # ACTIVATE CAMERA
        self.camera.use()

        # DRAW SCENE
        self.scene.draw()

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed to track movement.
        """
        # MOVE CHARACTER BASED ON KEYCODE
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user releases a key to track movement.
        """
        # MOVE CHARACTER BASED ON KEYCODE
        if key == arcade.key.UP or key == arcade.key.W:
                self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)


def main():
    """
    Main function.
    """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
#%%