import os
import random
import pygame


class Cloud:

  def __init__(self, image, x, y, speed, depth=1.0):
    self.image = image
    self.x = float(x)
    self.y = float(y)
    self.speed = speed
    self.depth = depth
    self.width = self.image.get_width()

  def update(self, screen_width, camera_dx=0.0):
    self.x += (self.speed * self.depth) - (camera_dx * self.depth * 0.25)

    if self.speed >= 0 and self.x > screen_width + 20:
      self.x = -self.width - random.randint(20, 120)
    elif self.speed < 0 and self.x + self.width < -20:
      self.x = screen_width + random.randint(20, 120)

  def draw(self, surface):
    surface.blit(self.image, (int(self.x), int(self.y)))


class CloudLayer:

  def __init__(
      self, cloud_images, screen_width, count=6, min_scale=1.4, max_scale=2.6
  ):
    self.clouds = []
    for _ in range(count):
      base_img = random.choice(cloud_images)
      depth = random.uniform(0.45, 1.0)
      scale = random.uniform(min_scale, max_scale) * (0.65 + 0.35 * depth)

      scaled_w = max(80, int(base_img.get_width() * scale))
      scaled_h = max(36, int(base_img.get_height() * scale))
      scaled_img = pygame.transform.smoothscale(base_img, (scaled_w, scaled_h))

      x = random.randint(-scaled_w, screen_width)
      y = random.randint(20, 200)
      speed = random.uniform(0.25, 0.9) * depth

      self.clouds.append(Cloud(scaled_img, x, y, speed, depth=depth))

    self.clouds.sort(key=lambda c: c.depth)

  def update(self, screen_width, camera_dx=0.0):
    for cloud in self.clouds:
      cloud.update(screen_width, camera_dx=camera_dx)

  def draw(self, surface):
    for cloud in self.clouds:
      cloud.draw(surface)


def _make_fallback_cloud(w=140, h=48, alpha=90):
  surf = pygame.Surface((w, h), pygame.SRCALPHA)
  pygame.draw.ellipse(surf, (170, 185, 200, alpha), (0, 10, w, h - 14))
  pygame.draw.ellipse(surf, (205, 215, 225, alpha), (w // 4, 0, w // 2, h // 2))
  return surf


def load_cloud_images(resolved_paths):
  loaded = []
  for path in resolved_paths:
    if os.path.exists(path):
      loaded.append(pygame.image.load(path).convert_alpha())
    else:
      print(f"Warning: Cloud image not found at '{path}'")
  if not loaded:
    loaded = [
        _make_fallback_cloud(130, 40, 75),
        _make_fallback_cloud(180, 55, 105),
    ]
  return loaded