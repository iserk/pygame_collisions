import random
import pygame

SCREEN_SIZE = (800, 600)
GROUND_HEIGHT = 50
BG_COLOR = (32, 128, 255)


class Scene:
    def __init__(self, game):
        self.game = game
        self.layers = {}  # dict of lists

    def activate(self):
        self.layers = {}

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
                if isinstance(obj, Mountain):
                    if obj.x + obj.width / 2 < self.game.camera.x:
                        self.layers[key].remove(obj)
                        del obj
                        Mountain.generate(self, self.game.camera.x + SCREEN_SIZE[0] + 500)

    def detect_collisions(self):
        for key in self.layers:
            for obj1 in self.layers[key]:
                for obj2 in self.layers[key]:
                    if obj1 != obj2:
                        if obj1.x < obj2.x + obj2.width and \
                                obj1.x + obj1.width > obj2.x and \
                                obj1.y < obj2.y + obj2.height and \
                                obj1.y + obj1.height > obj2.y:
                            obj1.on_collision(obj2)
                            obj2.on_collision(obj1)

    def render(self, camera):
        for key in sorted(self.layers.keys()):
            for obj in self.layers[key]:
                obj.render(camera)


class Game:
    def __init__(self):
            pygame.init()
            self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1)
            pygame.display.set_caption("Wire Plane")

            self.clock = pygame.time.Clock()

            self.scene = Scene(self)
            self.scene.game = self
            self.camera = Camera(self.screen, 0, 0)
            self.hero = HeroPlane(None)
            self.scene.add(self.hero, layer=10)

            self.hero.x = 100
            # self.hero.y = SCREEN_SIZE[1] - GROUND_HEIGHT
            self.hero.y = 100

            self.mountains = [Mountain.generate(self.scene, SCREEN_SIZE[0] + 200 + 500 * i) for i in range(3)]
            self.ground = Ground(self.scene)

            self.start_time = pygame.time.get_ticks()
            self.dt = 0
            self.elapsed_time = 0
            self.is_running = False
            self.fps_list = []

    def run(self):
        self.screen.fill(BG_COLOR)
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

            # self.camera.x = round(self.elapsed_time / 2)
            self.camera.x += self.dt * self.hero.HORIZONTAL_SPEED / 1000
            # self.camera.x += 1

            self.screen.fill(BG_COLOR)

            self.scene.update(self.dt, self.elapsed_time)

            self.scene.render(self.camera)
            fps = self.clock.get_fps()
            self.fps_list.append(fps)
            pygame.display.set_caption(f"Wire Plane - FPS: {round(fps)}, Average FPS: {round(sum(self.fps_list) / len(self.fps_list))}, objects: {len(self.scene.layers[0])}")

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


class HeroPlane(GameObject):
    COLOR = (200, 230, 255)
    VERTICAL_SPEED = 100
    HORIZONTAL_SPEED = 200
    HORIZONTAL_SPEED_STEP = 1
    HORIZONTAL_SPEED_MAX = 1000

    def __init__(self, game):
        super().__init__(game)
        self.x = 100
        self.y = 500

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.render(self.scene.game.camera, BG_COLOR)
                self.y -= 50
                return False
            elif event.key == pygame.K_DOWN:
                self.render(self.scene.game.camera, BG_COLOR)
                self.y += 50
                return False
        return True

    def update(self, dt, elapsed_time):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y -= self.VERTICAL_SPEED * dt / 1000
        elif keys[pygame.K_s]:
            self.y += self.VERTICAL_SPEED * dt / 1000
        elif keys[pygame.K_a]:
            self.HORIZONTAL_SPEED -= self.HORIZONTAL_SPEED_STEP
            if self.HORIZONTAL_SPEED < 0:
                self.HORIZONTAL_SPEED = 0
        elif keys[pygame.K_d]:
            self.HORIZONTAL_SPEED += self.HORIZONTAL_SPEED_STEP
            if self.HORIZONTAL_SPEED > self.HORIZONTAL_SPEED_MAX:
                self.HORIZONTAL_SPEED = self.HORIZONTAL_SPEED_MAX

    def render(self, camera, color=COLOR):
        pygame.draw.rect(camera.screen, color, (self.x, self.y - 20, 100, 20))


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

    def render(self, camera):
        # pygame.draw.line(
        #     camera.screen,
        #     (128, 64, 32),
        #     (self.x - self.width / 2 - camera.x, self.y - camera.y),
        #     (self.x - camera.x, self.y - self.height - camera.y), 1)
        #
        # pygame.draw.line(
        #     camera.screen,
        #     BG_COLOR,
        #     (self.x + self.width / 2 - camera.x, self.y - camera.y),
        #     (self.x - camera.x, self.y - self.height - camera.y), 3)

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

    def render(self, camera):
        pygame.draw.rect(camera.screen, (0, 255, 0), (self.x, self.y - camera.y, SCREEN_SIZE[0], GROUND_HEIGHT))


if __name__ == '__main__':
    game = Game()
    game.run()
