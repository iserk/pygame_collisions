import random
import pygame

from pygame import Vector2
import collision

SCREEN_SIZE = (800, 600)
GROUND_HEIGHT = 50


class Scene:
    def __init__(self, game):
        self.game = game
        self.layers = {0: []}
        self.camera = None

    def activate(self):
        self.layers = {0: []}
        self.camera = Camera(self.game.screen, 0, 0)

    def add(self, obj, layer=0):
        if layer not in self.layers:
            self.layers[layer] = []
        self.layers[layer].append(obj)
        obj.scene = self

    def handle_event(self, event):
        for key in self.layers:
            for obj in self.layers[key]:
                if not obj.handle_event(event):
                    break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.is_running = False
        return True

    def update(self, dt, elapsed_time):
        for key in self.layers:
            for obj in self.layers[key]:
                obj.update(dt, elapsed_time)

    def detect_collisions(self):
        # This version detects collisions between all objects
        for key in self.layers:
            for obj1 in self.layers[key]:
                for obj2 in self.layers[key]:
                    if obj1 != obj2:
                        # print(obj1.get_collider(), obj2.get_collider())
                        if collision.sat_collision_check(obj1.get_collider(), obj2.get_collider()):
                            print(f'Collision between {obj1} and {obj2}')
                            obj1.on_collision(obj2)
                            obj2.on_collision(obj1)

    def render_background(self):
        pass

    def render(self):
        self.render_background()

        for key in sorted(self.layers.keys()):
            for obj in self.layers[key]:
                obj.render(self.camera)


class GameScene(Scene):
    BG_COLOR = (32, 128, 255)

    def __init__(self, game):
        super().__init__(game)
        self.hero = None
        self.mountains = []
        self.ground = None
        self.clouds = []

    def activate(self):
        super().activate()

        self.hero = HeroPlane(None)
        self.add(self.hero, layer=10)

        self.hero.x = 100
        self.hero.y = SCREEN_SIZE[1] - GROUND_HEIGHT - 10
        # self.hero.y = 100

        self.mountains = [Mountain.generate(self, SCREEN_SIZE[0] + 200 + 500 * i) for i in range(3)]
        self.ground = Ground(self)
        self.clouds = [Cloud(self, 100, 100), Cloud(self, 300, 200), Cloud(self, 500, 300)]

    def detect_collisions(self):
        # This version detects collisions between the hero and other objects
        hero = self.hero
        for obj in self.layers[0]:
            if isinstance(obj, Mountain) or isinstance(obj, Ground) or isinstance(obj, Cloud):
                if collision.sat_collision_check(hero.get_collider(), obj.get_collider()):
                    # print(f'Collision between {hero} and {obj}')
                    hero.on_collision(obj)
                    obj.on_collision(hero)

    def render_background(self):
        self.camera.screen.fill(self.BG_COLOR)

    def update(self, dt, elapsed_time):
        super().update(dt, elapsed_time)

        # self.camera.x = round(self.elapsed_time / 2)
        self.camera.x += dt * self.hero.HORIZONTAL_SPEED / 1000
        # self.camera.x += 1

        for key in self.layers:
            for obj in self.layers[key]:
                if isinstance(obj, Mountain):
                    if obj.x + obj.width / 2 < self.camera.x:
                        self.layers[key].remove(obj)
                        del obj

                        Mountain.generate(self, self.camera.x + SCREEN_SIZE[0] + 500)


class GameOverScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game_over_text = None
        self.keys_text = None

    def activate(self):
        super().activate()

        self.game_over_text = Text(None, 'Game Over', x=SCREEN_SIZE[0] / 2, y=SCREEN_SIZE[1] / 2, size=48, color=(255, 160, 160))
        self.add(self.game_over_text, layer=100)

        self.keys_text = Text(None, 'Press <SPACE> to restart or <ESC> to quit',
                              x=SCREEN_SIZE[0] / 2, y=SCREEN_SIZE[1] / 2 + 64,
                              size=24, color='black')
        self.add(self.keys_text, layer=100)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game.change_scene(GameScene(self.game))
            elif event.key == pygame.K_ESCAPE:
                self.game.is_running = False
        return True


class VictoryScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.victory_text = None
        self.keys_text = None

    def activate(self):
        super().activate()

        self.victory_text = Text(None, 'You Win!', x=SCREEN_SIZE[0] / 2, y=SCREEN_SIZE[1] / 2, size=48, color=(64, 255, 128))
        self.add(self.victory_text, layer=100)

        self.keys_text = Text(None, 'Press <SPACE> to restart or <ESC> to quit',
                              x=SCREEN_SIZE[0] / 2, y=SCREEN_SIZE[1] / 2 + 64,
                              size=24, color='black')
        self.add(self.keys_text, layer=100)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game.change_scene(GameScene(self.game))
            elif event.key == pygame.K_ESCAPE:
                self.game.is_running = False
        return True


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1)
        pygame.display.set_caption("Wire Plane")

        self.clock = pygame.time.Clock()

        self.scene = GameScene(self)
        self.scene.game = self
        self.scene.activate()

        self.start_time = pygame.time.get_ticks()
        self.dt = 0
        self.elapsed_time = 0
        self.is_running = False
        self.fps_list = []

    def change_scene(self, scene):
        self.scene = scene
        self.scene.activate()

    def run(self):
        self.is_running = True

        while self.is_running:
            self.dt = self.clock.tick()
            self.elapsed_time = pygame.time.get_ticks() - self.start_time

            for event in pygame.event.get():
                if not self.scene.handle_event(event):
                    continue
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.scene.update(self.dt, self.elapsed_time)
            self.scene.detect_collisions()
            self.scene.render()
            fps = self.clock.get_fps()
            self.fps_list.append(fps)
            pygame.display.set_caption(
                f"Wire Plane - FPS: {round(fps)}, Average FPS: {round(sum(self.fps_list) / len(self.fps_list))}, objects: {len(self.scene.layers[0])}")

            pygame.display.flip()


class Camera:
    def __init__(self, screen, x, y):
        self.screen = screen
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Camera({self.x}, {self.y})'


class GameObject:
    def __init__(self, scene):
        self.scene = scene
        if scene is not None:
            self.scene.add(self)

    def get_collider(self):
        return []

    def handle_event(self, event):
        return True

    def update(self, dt, elapsed_time):
        pass

    def on_collision(self, other):
        pass

    def render(self, camera):
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}({self.x}, {self.y})'


class Text(GameObject):
    def __init__(self, scene, text, x, y, size=12, color=(255, 255, 255)):
        super().__init__(scene)
        self.text = text
        self.size = size
        self.color = color
        self.x = x
        self.y = y

    def render(self, camera):
        font = pygame.font.SysFont('Arial', self.size)
        text = font.render(self.text, False, self.color)
        text_rect = text.get_rect()
        text_rect.center = (self.x, self.y)
        camera.screen.blit(text, text_rect)


class HeroPlane(GameObject):
    COLOR = (200, 230, 255)
    VERTICAL_SPEED = 200
    HORIZONTAL_SPEED = 200
    HORIZONTAL_SPEED_STEP = 1
    HORIZONTAL_SPEED_MAX = 1000

    def __init__(self, game):
        super().__init__(game)
        self.x = 100
        self.y = 500

    def get_collider(self):
        return [
            Vector2(self.scene.camera.x + self.x, self.y - 20),
            Vector2(self.scene.camera.x + self.x + 100, self.y - 20),
            Vector2(self.scene.camera.x + self.x + 100, self.y),
            Vector2(self.scene.camera.x + self.x, self.y)
        ]

    def on_collision(self, other):
        print(f'Collision between {self} and {other}')
        if isinstance(other, Ground):
            self.y = other.y - 10
            self.scene.game.change_scene(VictoryScene(self.scene.game))
        # elif isinstance(other, Cloud):
        #     self.scene.game.change_scene(VictoryScene(self.scene.game))
        elif isinstance(other, Mountain):
            self.scene.game.change_scene(GameOverScene(self.scene.game))

    def update(self, dt, elapsed_time):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.VERTICAL_SPEED * dt / 1000
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.VERTICAL_SPEED * dt / 1000
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.HORIZONTAL_SPEED -= self.HORIZONTAL_SPEED_STEP
            if self.HORIZONTAL_SPEED < 0:
                self.HORIZONTAL_SPEED = 0
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.HORIZONTAL_SPEED += self.HORIZONTAL_SPEED_STEP
            if self.HORIZONTAL_SPEED > self.HORIZONTAL_SPEED_MAX:
                self.HORIZONTAL_SPEED = self.HORIZONTAL_SPEED_MAX

    def render(self, camera, color=COLOR):
        pygame.draw.rect(camera.screen, color, (self.x, self.y - 20, 100, 20))


class Cloud(GameObject):
    def __init__(self, scene, x, y):
        super().__init__(scene)
        self.x = x
        self.y = y

    def get_collider(self):
        # polygon of 7 points
        return [
            Vector2(self.x, self.y),
            Vector2(self.x + 100, self.y),
            Vector2(self.x + 150, self.y - 50),
            Vector2(self.x + 200, self.y),
            Vector2(self.x + 300, self.y),
            Vector2(self.x + 200, self.y + 50),
            Vector2(self.x + 150, self.y + 50)
        ]

    def update(self, dt, elapsed_time):
        if self.x < self.scene.camera.x - 500:
            self.x = self.scene.camera.x + SCREEN_SIZE[0] + random.randint(0, 500)
            self.y = random.randint(0, SCREEN_SIZE[1] - GROUND_HEIGHT - 100)

    def render(self, camera):
        pygame.draw.polygon(
            camera.screen,
            (255, 255, 255),
            (
                (self.x - camera.x, self.y - camera.y),
                (self.x + 100 - camera.x, self.y - camera.y),
                (self.x + 150 - camera.x, self.y - 50 - camera.y),
                (self.x + 200 - camera.x, self.y - camera.y),
                (self.x + 300 - camera.x, self.y - camera.y),
                (self.x + 200 - camera.x, self.y + 50 - camera.y),
                (self.x + 150 - camera.x, self.y + 50 - camera.y)
            )
        )


class Mountain(GameObject):
    MAX_HEIGHT = 450
    MIN_HEIGHT = 100
    MAX_WIDTH = 400
    MIN_WIDTH = 100

    def __init__(self, scene, x, height, width):
        super().__init__(scene)
        self.x = x
        self.y = SCREEN_SIZE[1] - GROUND_HEIGHT
        self.height = height
        self.width = width

    def get_collider(self):
        return [
            Vector2(self.x - self.width / 2, self.y),
            Vector2(self.x + self.width / 2, self.y),
            Vector2(self.x, self.y - self.height)
        ]

    def render(self, camera):
        pygame.draw.polygon(
            camera.screen,
            (128, 64, 32),
            (
                (self.x - self.width / 2 - camera.x, self.y - camera.y),
                (self.x + self.width / 2 - camera.x, self.y - camera.y),
                (self.x - camera.x, self.y - self.height - camera.y)
            )
        )

    @staticmethod
    def generate(scene, x, height=None, width=None):
        if height is None:
            height = random.randint(Mountain.MIN_HEIGHT, Mountain.MAX_HEIGHT)
            # height = 400
        if width is None:
            width = round(height * random.randint(80, 120) / 100)
            # width = 400
        return Mountain(scene, x, height, width)


class Ground(GameObject):
    def __init__(self, scene):
        super().__init__(scene)
        self.x = 0
        self.y = SCREEN_SIZE[1] - GROUND_HEIGHT

    def get_collider(self):
        return [
            Vector2(self.x + self.scene.camera.x, self.y),
            Vector2(self.x + SCREEN_SIZE[0] + self.scene.camera.x, self.y),
            Vector2(self.x + SCREEN_SIZE[0] + self.scene.camera.x, SCREEN_SIZE[1]),
            Vector2(self.x + self.scene.camera.x, SCREEN_SIZE[1])
        ]

    def render(self, camera):
        pygame.draw.rect(camera.screen, (0, 255, 0), (self.x, self.y - camera.y, SCREEN_SIZE[0], GROUND_HEIGHT))


if __name__ == '__main__':
    game = Game()
    game.run()
