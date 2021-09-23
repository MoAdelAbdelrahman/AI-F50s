import pygame
import neat
import os
import time
import random


WIN_W = 800
WIN_H = 600

plane_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "plane1.png"))),
              pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "plane2final.png"))),
              pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "plane3.png")))]
mntn_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "mntn.png")))
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
bg_img = pygame.image.load(os.path.join("imgs", "background.png"))
bg_anime = pygame.image.load(os.path.join("imgs", "bganime.png"))


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

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.animationTime:
            self.img = self.imgs[0].convert_alpha()
        elif self.img_count < self.animationTime*2:
            self.img = self.imgs[1].convert_alpha()
        elif self.img_count < self.animationTime*3:
            self.img = self.imgs[2].convert_alpha()
        elif self.img_count < self.animationTime*4:
            self.img = self.imgs[1].convert_alpha()
        elif self.img_count == self.animationTime*4+1:
            self.img = self.imgs[0].convert_alpha()
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.imgs[1].convert_alpha()
            self.img_count = self.animationTime * 2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(center=(self.x, self.y)).center)
        win.blit(rotated_img, new_rect.topleft)

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
        win.blit(self.mntnTop.convert_alpha(), (self.x, self.top))
        win.blit(self.mntn_btm.convert_alpha(), (self.x, self.bottom))

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

    def draw(self, win):
        win.blit(self.img.convert_alpha(), (self.x1, self.y))
        win.blit(self.img.convert_alpha(), (self.x2, self.y))


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

    def draw(self, win):
        win.blit(self.img.convert_alpha(), (self.x1, self.y))
        win.blit(self.img.convert_alpha(), (self.x2, self.y))


def draw_win(win, plane, mountains, base, back):
    win.blit(bg_img.convert_alpha(), (0, 0))

    back.draw(win)
    base.draw(win)
    for mntn in mountains:
        mntn.draw(win)
    plane.draw(win)
    pygame.display.update()



def main():
    backAnimation = Bg_anime(0)
    plane = Plane(300, 200)
    base = Base(510)
    pos_factor = 600
    speed = 30
    mntns = [Mountain(pos_factor)]
    win = pygame.display.set_mode((WIN_W, WIN_H))
    clock = pygame.time.Clock()
    score = 0
    run = True
    plane.img.convert_alpha()
    base.img.convert_alpha()
    backAnimation.img.convert_alpha()

    # main game loop
    while run:
        clock.tick(speed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # mountains movement
        add_mntn = False
        dismissed = []
        for mntn in mntns:
            if mntn.collide(plane):
                pass

            if mntn.x + mntn.mntnTop.get_width() < 0:
                dismissed.append(mntn)

            if not mntn.passed and mntn.x < plane.x:
                mntn.passed = True
                add_mntn = True
            mntn.move()
        if add_mntn:
            score += 1
            mntns.append(Mountain(pos_factor))

        for m in dismissed:
            mntns.remove(m)


        # moving other objects
        # plane.move()
        backAnimation.move()
        base.move()
        draw_win(win, plane, mntns, base, backAnimation)
    pygame.quit()
    quit()


main()
