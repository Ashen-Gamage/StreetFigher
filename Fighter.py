import pygame


class Fighter():
    # constructor
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player  # Player number (1 or 2)
        self.size = data[0]  # Sprite frame width and height in the sheet
        self.image_scale = data[1]  # Scale multiplier for the sprite
        self.offset = data[2]  # [x_offset, y_offset] to align sprite over hitbox
        self.flip = flip  # Flag to flip sprite horizontally based on opponent position
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0  # 0:idle, 1:run, 2:jump, 3:attack1, 4:attack2, 5:hit, 6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()  # Track time for animation updates
        self.rect = pygame.Rect((x, y, 80, 180))  # Fighter collision hitbox
        self.vel_y = 0  # Vertical velocity for jumping
        self.running = False  # Flag to check if the fighter is running
        self.jump = False  # Flag to check if the fighter is jumping
        self.attacking = False  # Flag to check if the fighter is attacking
        self.attack_type = 0  # Variable to track the type of attack
        self.attack_cooldown = 0  # Cooldown timer after attack finishes
        self.sound = sound  # Sound effect for the fighter's attack
        self.hit = False  # Flag to check if the fighter has been hit
        self.health = 100  # Health of the fighter
        self.alive = True  # Flag to check if the fighter is alive

    # load images from sprite sheet
    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(
                    (x * self.size, y * self.size, self.size, self.size)
                )
                temp_img_list.append(
                    pygame.transform.scale(
                        temp_img, (self.size * self.image_scale, self.size * self.image_scale)
                    )
                )
            animation_list.append(temp_img_list)
        return animation_list

    # MOVE METHOD
    def move(self, SCREEN_WIDTH, SCREEN_HEIGHT, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False  # Reset running flag each frame

        # get key press
        key = pygame.key.get_pressed()

        # can only perform actions if alive and not currently attacking
        if not self.attacking and self.alive and not round_over:
            # controls for player 1
            if self.player == 1:
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True

                # single jump (only when on the ground)
                if key[pygame.K_w] and not self.jump:
                    self.vel_y = -30
                    self.jump = True

                # attack
                if key[pygame.K_r] or key[pygame.K_t]:
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2
                    self.attack(surface, target)

            # controls for player 2
            if self.player == 2:
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True

                # single jump (only when on the ground)
                if key[pygame.K_UP] and not self.jump:
                    self.vel_y = -30
                    self.jump = True

                # attack
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2
                    self.attack(surface, target)

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure fighter stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right
        if self.rect.bottom + dy > SCREEN_HEIGHT - 110:
            self.vel_y = 0
            self.jump = False  # Reset jump only when touching the ground
            dy = SCREEN_HEIGHT - 110 - self.rect.bottom

        # ensure fighter faces opponent
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # update fighter position
        self.rect.x += dx
        self.rect.y += dy

    # handle animation updates
    def update(self):
        # check what action the fighter is performing
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # death
        elif self.hit:
            self.update_action(5)  # hit
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(3)  # attack1
            elif self.attack_type == 2:
                self.update_action(4)  # attack2
        elif self.jump:
            self.update_action(2)  # jump
        elif self.running:
            self.update_action(1)  # run
        else:
            self.update_action(0)  # idle

        animation_cooldown = 50
        # update image depending on current action
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            # if the animation has run out, reset back to the start
            if self.frame_index >= len(self.animation_list[self.action]):
                # check if the player is dead
                if not self.alive:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0
                    # once the attack animation finishes, reset attacking and start cooldown
                    if self.action == 3 or self.action == 4:
                        self.attacking = False
                        self.attack_cooldown = 20
                    # if the fighter was hit, recover and start cooldown
                    if self.action == 5:
                        self.hit = False
                        self.attacking = False
                        self.attack_cooldown = 20

    def attack(self, surface, target):
        if self.attack_cooldown == 0:
            #execute attack
            self.attacking = True
            self.sound.play()  # Play the attack sound
            attack_rect = pygame.Rect(
                self.rect.centerx - (2 * self.rect.width * self.flip),
                self.rect.y,
                2 * self.rect.width,
                self.rect.height,
            )
            if attack_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        # check if the new action is different from the current action
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(
            img,
            (
                self.rect.x - (self.offset[0] * self.image_scale),
                self.rect.y - (self.offset[1] * self.image_scale),
            ),
        )