import pygame

class Engine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([256, 240])
        self.screen.fill((0, 0, 0))
        self.running = False
        self.finished = False
    
    def set_pixel(self, x, y, color):
        self.screen.set_at((x, y), color)

    def update(self):
        if not self.finished:
            self.running = True
        if self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            pygame.display.flip()
        if not self.running:
            self.finished = True
            pygame.quit()

    def get_keys(self):
        # We need to process events so that key.get_pressed() updates correctly
        # if there's any pending events not caught by update() yet.
        pygame.event.pump()
        if not self.running:
            return {}
        return pygame.key.get_pressed()

if __name__ == '__main__':
    e = Engine()
    for i in range(10000):
        e.update()

