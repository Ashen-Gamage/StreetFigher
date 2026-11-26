import os
import pygame
import sys

from pygame import mixer
from Fighter import Fighter

mixer.init()
pygame.init()


# exe.file
def resource_path(relative_path):
  base_path = getattr(
      sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))
  )
  return os.path.join(base_path, relative_path)


# create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brawler")

# set framerate
clock = pygame.time.Clock()
fps = 60

# define colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (50, 205, 50)
DARK_BTN = (35, 35, 45)
HOVER_BTN = (65, 65, 85)

# define game variables
game_started = False
sound_enabled = True
MUSIC_VOLUME = 0.35
SWORD_VOLUME = 0.5
MAGIC_VOLUME = 0.75

intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]  # [player1_score, player2_score]
round_over = False
Round_over_cooldown = 2000  # 2 seconds cooldown after a round ends

# define fighter variables
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]

WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]


class DummySound:

  def play(self):
    pass

  def set_volume(self, vol):
    pass


def load_sound(path, volume=0.5):
  if os.path.exists(path):
    snd = pygame.mixer.Sound(path)
    snd.set_volume(volume)
    return snd
  print(f"Warning: Sound file not found at '{path}'")
  return DummySound()


def apply_sound_state():
  if sound_enabled:
    sword_fx.set_volume(SWORD_VOLUME)
    magic_fx.set_volume(MAGIC_VOLUME)
    if pygame.mixer.music.get_busy():
      pygame.mixer.music.set_volume(MUSIC_VOLUME)
      pygame.mixer.music.unpause()
  else:
    sword_fx.set_volume(0.0)
    magic_fx.set_volume(0.0)
    if pygame.mixer.music.get_busy():
      pygame.mixer.music.set_volume(0.0)
      pygame.mixer.music.pause()


# load music and sounds
music_path = resource_path("Assests/audio/music.wav")
has_music = os.path.exists(music_path)
if has_music:
  pygame.mixer.music.load(music_path)
  pygame.mixer.music.set_volume(MUSIC_VOLUME)
  pygame.mixer.music.play(-1)
else:
  print(f"Warning: Music file not found at '{music_path}'")

sword_fx = load_sound(resource_path("Assests/audio/sword.wav"), SWORD_VOLUME)
magic_fx = load_sound(resource_path("Assests/audio/magic.wav"), MAGIC_VOLUME)

# load background image
bg_image = pygame.image.load(
    resource_path("Assests/images/background/background.jpg")
).convert_alpha()

# load fighter images
warrior_image = pygame.image.load(
    resource_path("Assests/images/warrior/Sprites/warrior.png")
).convert_alpha()
wizard_image = pygame.image.load(
    resource_path("Assests/images/wizard/Sprites/wizard.png")
).convert_alpha()

# load victory image
victory_image = pygame.image.load(
    resource_path("Assests/images/icons/victory.png")
).convert_alpha()

# find number of steps in each animation
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 2, 8, 8, 3, 7]

# define fonts
title_font = pygame.font.Font(
    resource_path("Assests/images/turok/Turok.ttf"), 64
)
count_font = pygame.font.Font(
    resource_path("Assests/images/turok/Turok.ttf"), 80
)
score_font = pygame.font.Font(
    resource_path("Assests/images/turok/Turok.ttf"), 27
)
info_font = pygame.font.Font(
    resource_path("Assests/images/turok/Turok.ttf"), 22
)

# UI buttons
start_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 455, 240, 62)
sound_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, 530, 280, 44)


def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))


def draw_centered_text(text, font, text_col, center_x, center_y):
  img = font.render(text, True, text_col)
  rect = img.get_rect(center=(center_x, center_y))
  screen.blit(img, rect)


def draw_button(rect, label, font, mouse_pos, accent_color=WHITE):
  is_hovered = rect.collidepoint(mouse_pos)
  bg_col = HOVER_BTN if is_hovered else DARK_BTN
  border_col = YELLOW if is_hovered else accent_color
  pygame.draw.rect(screen, bg_col, rect, border_radius=8)
  pygame.draw.rect(screen, border_col, rect, width=3, border_radius=8)
  draw_centered_text(label, font, border_col, rect.centerx, rect.centery)


def draw_bg():
  scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
  screen.blit(scaled_bg, (0, 0))


def draw_health_bar(health, x, y):
  ratio = max(0, health) / 100
  pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 204, 24))
  pygame.draw.rect(screen, RED, (x, y, 200, 20))
  pygame.draw.rect(screen, YELLOW, (x, y, 200 * ratio, 20))


def draw_start_screen(mouse_pos):
  draw_bg()

  # dark overlay for crisp readability
  overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
  overlay.fill((0, 0, 0, 165))
  screen.blit(overlay, (0, 0))

  # title
  draw_centered_text("BRAWLER", title_font, YELLOW, SCREEN_WIDTH // 2, 65)

  # controls cards for Player 1 & Player 2
  p1_card = pygame.Rect(70, 125, 410, 300)
  p2_card = pygame.Rect(520, 125, 410, 300)

  pygame.draw.rect(screen, (25, 25, 35), p1_card, border_radius=10)
  pygame.draw.rect(screen, RED, p1_card, width=2, border_radius=10)

  pygame.draw.rect(screen, (25, 25, 35), p2_card, border_radius=10)
  pygame.draw.rect(screen, YELLOW, p2_card, width=2, border_radius=10)

  # Player 1 controls
  draw_centered_text(
      "PLAYER 1 - WARRIOR", score_font, RED, p1_card.centerx, 158
  )
  p1_lines = [
      "Move Left / Right : A / D",
      "Jump             : W",
      "Attack 1 / 2     : R / T",
  ]
  for idx, line in enumerate(p1_lines):
    draw_text(line, info_font, WHITE, p1_card.x + 25, 205 + idx * 55)

  # Player 2 controls
  draw_centered_text(
      "PLAYER 2 - WIZARD", score_font, YELLOW, p2_card.centerx, 158
  )
  p2_lines = [
      "Move Left / Right : Left / Right",
      "Jump             : Up Arrow",
      "Attack 1 / 2     : Numpad 1 / 2",
  ]
  for idx, line in enumerate(p2_lines):
    draw_text(line, info_font, WHITE, p2_card.x + 25, 205 + idx * 55)

  # Start & Sound buttons
  draw_button(start_btn_rect, "START GAME", score_font, mouse_pos, GREEN)
  sound_label = "SOUND: ON (M)" if sound_enabled else "SOUND: OFF (M)"
  sound_col = GREEN if sound_enabled else RED
  draw_button(sound_btn_rect, sound_label, info_font, mouse_pos, sound_col)


# create two instances of the Fighter class
fighter_1 = Fighter(
    1,
    200,
    310,
    False,
    WARRIOR_DATA,
    warrior_image,
    WARRIOR_ANIMATION_STEPS,
    sword_fx,
)
fighter_2 = Fighter(
    2,
    700,
    310,
    True,
    WIZARD_DATA,
    wizard_image,
    WIZARD_ANIMATION_STEPS,
    magic_fx,
)

# game loop
run = True
while run:
  clock.tick(fps)
  mouse_pos = pygame.mouse.get_pos()

  # event handling
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_m:
        sound_enabled = not sound_enabled
        apply_sound_state()
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
      if not game_started:
        if start_btn_rect.collidepoint(event.pos):
          game_started = True
          intro_count = 3
          last_count_update = pygame.time.get_ticks()
        elif sound_btn_rect.collidepoint(event.pos):
          sound_enabled = not sound_enabled
          apply_sound_state()

  if not game_started:
    draw_start_screen(mouse_pos)
  else:
    # draw background
    draw_bg()

    # show player stats
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 780, 20)
    draw_text("P1: " + str(score[0]), score_font, RED, 20, 50)
    draw_text("P2: " + str(score[1]), score_font, RED, 780, 50)

    # update intro countdown
    if intro_count <= 0:
      fighter_1.move(
          SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over
      )
      fighter_2.move(
          SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over
      )
    else:
      draw_centered_text(
          str(intro_count), count_font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3
      )
      if (pygame.time.get_ticks() - last_count_update) >= 1000:
        intro_count -= 1
        last_count_update = pygame.time.get_ticks()

    # update & draw fighters
    fighter_1.update()
    fighter_2.update()
    fighter_1.draw(screen)
    fighter_2.draw(screen)

    # check for player defeat
    if not round_over:
      if not fighter_1.alive:
        score[1] += 1
        round_over = True
        round_over_time = pygame.time.get_ticks()
      elif not fighter_2.alive:
        score[0] += 1
        round_over = True
        round_over_time = pygame.time.get_ticks()
    else:
      screen.blit(victory_image, (360, 120))
      draw_text("Round Over", count_font, RED, 320, SCREEN_HEIGHT / 3)
      draw_text("Press R to Restart", score_font, RED, 400, SCREEN_HEIGHT / 2)

      if (pygame.time.get_ticks() - round_over_time) >= Round_over_cooldown:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
          fighter_1 = Fighter(
              1,
              200,
              310,
              False,
              WARRIOR_DATA,
              warrior_image,
              WARRIOR_ANIMATION_STEPS,
              sword_fx,
          )
          fighter_2 = Fighter(
              2,
              700,
              310,
              True,
              WIZARD_DATA,
              wizard_image,
              WIZARD_ANIMATION_STEPS,
              magic_fx,
          )
          intro_count = 3
          last_count_update = pygame.time.get_ticks()
          round_over = False

  pygame.display.update()

pygame.quit()