import pygame
import neat
import os
import time
import random
pygame.font.init()


WIN_W = 800
WIN_H = 600

plane_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "plane1.png"))),
              pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "plane2final.png"))),
              pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "plane3.png")))]
mntn_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "mntn.png")))
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))

bg_anime = pygame.image.load(os.path.join("imgs", "bganime.png"))
font = pygame.font.SysFont("comicsans", 50)


class Plane:
    imgs = plane_imgs
    max_rotate = 25
    rotate_vel = 20
    animationTime = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.ticker = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.imgs[0]

    def jump(self):
        self.vel = -10.5
        self.ticker = 0
        self.height = self.y

    def move(self):
        self.ticker += 1
        d = self.vel * self.ticker + 1.5 * self.ticker ** 2
        if d >= 16:
            d = 16
        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.max_rotate:
                self.tilt = self.max_rotate
        else:
            if self.tilt > -90:
                self.tilt -= self.rotate_vel

    def prepare(self):
        self.img.convert_alpha()
        planeRect = self.img.get_rect()
        planeSurface = pygame.Surface((planeRect.width, planeRect.height), pygame.SRCALPHA)
        planeSurface.fill((0, 0, 0, 0))
        planeSurface.blit(self.img, planeRect)
        return planeSurface

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.animationTime:
            self.img = self.imgs[0]
        elif self.img_count < self.animationTime*2:
            self.img = self.imgs[1]
        elif self.img_count < self.animationTime*3:
            self.img = self.imgs[2]
        elif self.img_count < self.animationTime*4:
            self.img = self.imgs[1]
        elif self.img_count == self.animationTime*4+1:
            self.img = self.imgs[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.imgs[1]
            self.img_count = self.animationTime * 2

        Surface = self.prepare()

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(center=(self.x, self.y)).center)
        win.blit(Surface, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Mountain:
    gap = 200
    vel = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100
        self.top = 0
        self.bottom = 0
        self.mntnTop = pygame.transform.flip(mntn_img, False, True)
        self.mntn_btm = mntn_img
        self.passed = False
        self.setHeight()

    def setHeight(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.mntnTop.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.vel

    def draw(self, win):
        bliterTop = self.mntnTop.convert_alpha()
        bliterBtm = self.mntn_btm.convert_alpha()
        win.blit(bliterTop, (self.x, self.top))
        win.blit(bliterBtm, (self.x, self.bottom))

    def collide(self, plane):
        plane_mask = plane.get_mask()
        topMntnMask = pygame.mask.from_surface(self.mntnTop)
        bottomMntnMask = pygame.mask.from_surface(self.mntn_btm)

        top_offset = (self.x - plane.x, self.top - round(plane.y))
        bottom_offset = (self.x - plane.x, self.bottom - round(plane.y))

        planePointB = plane_mask.overlap(bottomMntnMask, bottom_offset)
        planePointT = plane_mask.overlap(topMntnMask, top_offset)

        if planePointB or planePointT:
            return True
        return False


class Bg_anime:
    vel = 5
    width = bg_anime.get_width()
    img = bg_anime

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def prepare(self):
        BG = self.img.get_rect()
        BGSurface = pygame.Surface((BG.width, BG.height), pygame.SRCALPHA)
        BGSurface.fill((0, 0, 0, 0))
        BGSurface.blit(self.img, BG)
        return BGSurface

    def draw(self, win):
        Surface = self.prepare()
        win.blit(Surface, (self.x1, self.y))
        win.blit(Surface, (self.x2, self.y))


class Base:
    vel = 5
    width = base_img.get_width()
    img = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def prepare(self):
        self.img.convert_alpha()
        baseRect = self.img.get_rect()
        baseSurface = pygame.Surface((baseRect.width, baseRect.height), pygame.SRCALPHA)
        baseSurface.fill((0, 0, 0, 0))
        baseSurface.blit(self.img, baseRect)
        return baseSurface

    def draw(self, win):
        surface = self.prepare()
        win.blit(surface, (self.x1, self.y))
        win.blit(surface, (self.x2, self.y))


def draw_win(win, plane, mountains, base, back, passedCount):
    clock = pygame.time.Clock()
    clock.tick(120)
    back.draw(win)
    base.draw(win)
    text = font.render(str(passedCount), 1, (0, 255, 0))

    for mntn in mountains:
        mntn.draw(win)
    plane.draw(win)
    win.blit(text, (WIN_W - 10 - text.get_width(), 10))
    pygame.display.update()


def main():
    backAnimation = Bg_anime(0)
    plane = Plane(int(WIN_W / 2), int(WIN_H / 2))
    base = Base(510)
    pos_factor = 600
    speed = 30
    clock = pygame.time.Clock()
    win = pygame.display.set_mode((WIN_W, WIN_H))
    firstMntn = Mountain(pos_factor)
    mntns = [firstMntn]
    score = 0
    run = True
    checkerOutOfFrame = firstMntn.mntnTop.get_width()
    # main game loop
    while run:
        clock.tick(speed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # mountains movement
        add_mntn = False
        dismissed = []
        for i in range(len(mntns)):
            mntns[i].mntnTop.convert_alpha()
            mntns[i].mntn_btm.convert_alpha()
            mntns[i].move()
            if mntns[i].collide(plane):
                pass

            # out of frame
            if mntns[i].x + checkerOutOfFrame < 0:
                dismissed.append(mntns[i])

            # plane passed the mountain
            if not mntns[i].passed and mntns[i].x + pos_factor < plane.x:
                mntns[i].passed = True
                score += 1
                add_mntn = True

        if add_mntn:
            mntns.append(Mountain(pos_factor))

        # out of frame mountain to delete
        if mntns[i] in dismissed:
            mntns.remove(mntns[i])

        #plane hit the floor
        if plane.y + plane.img.get_height() >= 630:
            pass
        # moving other objects
        # plane.move()
        backAnimation.move()
        base.move()
        draw_win(win, plane, mntns, base, backAnimation, score)
    pygame.quit()
    quit()


main()
