
import pygame
import time

pygame.init()

pygame.mixer.init()

sound = pygame.mixer.Sound("sounds/drowsy.mp3")

sound.play()

print("SOUND PLAYING")

time.sleep(5)

