import random
import arcade
import os

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.2
COIN_COUNT = 50

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Follow Player Simple Example"

CHARACTER_SPRITE_SPEED = 5
COIN_SPRITE_SPEED = 3


class Coin(arcade.Sprite):
    def follow_sprite(self, player_sprite):
        if self.center_y < player_sprite.center_y:
            self.center_y += min(COIN_SPRITE_SPEED, player_sprite.center_y - self.center_y)
        elif self.center_y > player_sprite.center_y:
            self.center_y -= min(COIN_SPRITE_SPEED, self.center_y - player_sprite.center_y)

        if self.center_x < player_sprite.center_x:
            self.center_x += min(COIN_SPRITE_SPEED, player_sprite.center_x - self.center_x)
        elif self.center_x > player_sprite.center_x:
            self.center_x -= min(COIN_SPRITE_SPEED, self.center_x - player_sprite.center_x)


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        self.player_list = None
        self.coin_list = None
        self.player_sprite = None
        self.score = 0
        self.keys_pressed = set()
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.score = 0

        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/"
                                           "femalePerson_idle.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        for i in range(COIN_COUNT):
            coin = Coin(":resources:images/items/coinGold.png", SPRITE_SCALING_COIN)
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT)
            self.coin_list.append(coin)

    def on_draw(self):
        self.clear()
        self.coin_list.draw()
        self.player_list.draw()
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)

    def on_update(self, delta_time):
        if arcade.key.UP in self.keys_pressed:
            self.player_sprite.center_y += CHARACTER_SPRITE_SPEED
        if arcade.key.DOWN in self.keys_pressed:
            self.player_sprite.center_y -= CHARACTER_SPRITE_SPEED
        if arcade.key.LEFT in self.keys_pressed:
            self.player_sprite.center_x -= CHARACTER_SPRITE_SPEED
        if arcade.key.RIGHT in self.keys_pressed:
            self.player_sprite.center_x += CHARACTER_SPRITE_SPEED

        self.player_sprite.center_x = max(0, min(self.player_sprite.center_x, SCREEN_WIDTH))
        self.player_sprite.center_y = max(0, min(self.player_sprite.center_y, SCREEN_HEIGHT))

        for coin in self.coin_list:
            coin.follow_sprite(self.player_sprite)

        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        for coin in hit_list:
            coin.remove_from_sprite_lists()
            self.score += 1


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
