
import pygame
import time

pygame.init()

pygame.mixer.init()

pygame.mixer.music.load("sounds/drowsy.mp3")

pygame.mixer.music.play()

print("PLAYING...")

time.sleep(10)
