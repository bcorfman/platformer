"""
Load a Tiled map file with Levels

Artwork from: https://kenney.nl
Tiled available from: https://www.mapeditor.org/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_tiled_map_with_levels
"""

import os
import time

import arcade

TILE_SPRITE_SCALING = 0.5
PLAYER_SCALING = 0.6

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Tiled Map with Levels Example"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SPRITE_SCALING
MOVEMENT_SPEED = 5
SPRITE_SCALING = 3
BACKGROUND_RISE_AMOUNT = 40

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN_TOP = 60
VIEWPORT_MARGIN_BOTTOM = 60
VIEWPORT_RIGHT_MARGIN = 270
VIEWPORT_LEFT_MARGIN = 270

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = 23
GRAVITY = 1.1


class MyGame(arcade.Window):
    """Main application class."""

    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Tilemap Object
        self.tile_map = None

        # Sprite lists
        self.player_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None

        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0
        self.end_of_map = 0
        self.game_over = False
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None

        self.level = 1
        self.max_level = 2

        self.backgrounds = arcade.SpriteList()
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    def setup(self):
        """Set up the game and initialize the variables."""

        # Sprite lists
        self.player_list = arcade.SpriteList()
        
        # Create your sprites and sprite lists here
        rise = BACKGROUND_RISE_AMOUNT * SPRITE_SCALING

        # Set up the player
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            PLAYER_SCALING,
        )

        # Starting position of the player
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 64
        self.player_list.append(self.player_sprite)

        images = [":resources:images/cybercity_background/far-buildings.png"]
        for count, image in enumerate(images):
            bottom = rise * (len(images) - count - 1)

            sprite = arcade.Sprite(image, scale=SPRITE_SCALING)
            sprite.bottom = bottom
            sprite.left = 0
            self.backgrounds.append(sprite)

            sprite = arcade.Sprite(image, scale=SPRITE_SCALING)
            sprite.bottom = bottom
            sprite.left = sprite.width
            self.backgrounds.append(sprite)

        self.load_level(self.level)

        self.game_over = False

    def load_level(self, level):
        # layer_options = {"Platforms": {"use_spatial_hash": True}}

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(
            f":resources:tiled_maps/level_{level}.json", scaling=TILE_SPRITE_SCALING
        )

        # --- Walls ---

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            self.tile_map.sprite_lists["Platforms"],
            gravity_constant=GRAVITY,
        )

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Set the view port boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

    def pan_camera_to_user(self, panning_fraction: float = 1.0):
        # This spot would center on the user
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )

        if screen_center_y < 0:
            screen_center_y = 0
        user_centered = screen_center_x, screen_center_y

        self.camera.move_to(user_centered, panning_fraction)
        
    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        self.clear()

        self.camera.use()

        # Draw all the sprites.
        self.backgrounds.draw()
        self.player_list.draw()
        self.tile_map.sprite_lists["Platforms"].draw()

        if self.game_over:
            arcade.draw_text(
                "Game Over",
                self.view_left + 200,
                self.view_bottom + 200,
                arcade.color.BLACK,
                30,
            )

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """Movement and game logic"""
        self.player_sprite.center_x += self.player_sprite.change_x
        self.player_sprite.center_y += self.player_sprite.change_y
        self.pan_camera_to_user(0.1)

        camera_x = self.camera.position[0]

        for count, sprite in enumerate(self.backgrounds):
            layer = count // 2
            frame = count % 2
            offset = camera_x / (2 ** (layer + 2))
            jump = (camera_x - offset) // sprite.width
            final_offset = offset + (jump + frame) * sprite.width
            sprite.left = final_offset

        if self.player_sprite.right >= self.end_of_map:
            if self.level < self.max_level:
                self.level += 1
                self.load_level(self.level)
                self.player_sprite.center_x = 128
                self.player_sprite.center_y = 64
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
            else:
                self.game_over = True

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        if not self.game_over:
            self.physics_engine.update()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
