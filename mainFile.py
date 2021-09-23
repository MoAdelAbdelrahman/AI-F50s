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
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "background.png")))


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

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(center=(self.x, self.y)).center)
        win.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class mountain:
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
        self.mntnTop = self.height - self.mntnTop.get_height()
        self.mntn_btm = self.height + self.gap

    def move(self):
        self.x -= self.vel

    def draw(self, win):
        win.blit(self.mntnTop, (self.x, self.top))
        win.blit(self.mntn_btm, (self.x, self.bottom))

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


def draw(win, plane):
    win.blit(bg_img, (0, 0))
    plane.draw(win)
    pygame.display.update()


def main():
    plane = Plane(300, 200)
    win = pygame.display.set_mode((WIN_W, WIN_H))
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        plane.move()
        draw(win, plane)
    pygame.quit()
    quit()


main()
