import pygame
import time
import random
import os

pygame.font.init()

WIN_WIDTH = 576
WIN_HEIGHT = 800

BIRD_IMGS = []
BIRD_IMGS.append(pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))))
BIRD_IMGS.append(pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))))
BIRD_IMGS.append(pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))))

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsan", 50)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        if d > 16: d = 16
        if d <= 0: d -= 2

        self.y += d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[0]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)  # rotate around center and not top left corner
        win.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe():
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def die(score, hs):
    if score > hs:
        hs = score
        with open("high_score.txt", "w") as hs_file:
            hs_file.write(str(hs))
    return hs
def draw_window(win, bird, pipes, base, score, high_score, is_dead):
    win.blit(BG_IMG, (0, 0))
    base.draw(win)
    for pipe in pipes:
        pipe.draw(win)

    bird.draw(win)

    score_text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_text, (WIN_WIDTH - 10 - score_text.get_width(), 10))

    high_score_text = STAT_FONT.render("High Score: " + str(high_score), 1, (255, 255, 255))
    win.blit(high_score_text, (10, 10))

    if is_dead:
        die_text = STAT_FONT.render("You died", 1, (255, 255, 255))
        win.blit(die_text, (WIN_WIDTH / 2 - die_text.get_width() / 2, WIN_HEIGHT / 2 - die_text.get_height()))

        die_text = STAT_FONT.render("Press enter to play again", 1, (255, 255, 255))
        win.blit(die_text, (WIN_WIDTH / 2 - die_text.get_width() / 2, WIN_HEIGHT / 2))

        game_over_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        game_over_screen.fill((0, 0, 0))
        game_over_screen.set_alpha(160)
        win.blit(game_over_screen, (0, 0))

    pygame.display.update()


def main():
    bird = Bird(230, 350)

    is_dead = False

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0
    with open("high_score.txt", "a") as hs_file:
        pass
    with open("high_score.txt", "r+") as hs_file:
        if hs_file.readline() == "":
            hs_file.write(str(0))
        hs_file.seek(0)
        high_score = int(hs_file.readline())
        print(high_score)

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # QUIT GAME
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if is_dead and event.key == pygame.K_RETURN:  # NEW GAME
                    bird = Bird(230, 350)
                    score = 0
                    is_dead = False
                    pipes = [Pipe(600)]
                if not is_dead and event.key == pygame.K_SPACE:  # JUMP
                    bird.jump()

        if not is_dead:

            base.move()
            bird.move()

            add_pipe = False
            rem = []
            for pipe in pipes:
                if pipe.collide(bird):
                    is_dead = True
                    high_score = die(score, high_score)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)

                pipe.move()
            if add_pipe:
                score += 1
                print(score)
                pipes.append(Pipe(600))
            for r in rem:
                pipes.remove(r)

            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                is_dead = True
                high_score = die(score, high_score)

        draw_window(win, bird, pipes, base, score, high_score, is_dead)


if __name__ == "__main__":
    main()
