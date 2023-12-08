import pygame
import random
import pickle

pygame.display.set_caption("Survival")
icon = pygame.image.load('pictures/iconGame.png')
pygame.display.set_icon(icon)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen):
        super().__init__()
        self.x = x
        self.y = y
        self.hp = 3
        self.screen = screen
        self.walk_right = [pygame.image.load(f'pictures/player_right/player_right{i}.png').convert_alpha() for i in
                           range(1, 13)]
        self.resize_player_right = [pygame.transform.scale(image, (55, 75)) for image in self.walk_right]
        self.walk_left = [pygame.transform.flip(image, True, False) for image in self.walk_right]
        self.resize_player_left = [pygame.transform.scale(image, (55, 75)) for image in self.walk_left]
        self.player_rect = self.resize_player_right[0].get_rect(topleft=(self.x, self.x))
        self.is_jump = False
        self.player_speed = 8
        self.jump_count = 8
        self.player_anim_count = 0
        self.keys = pygame.key.get_pressed()
        
    def update_player(self, keys):
        if keys[pygame.K_a]:
            self.update_animation_player(self.screen, side=True)
        else:
            self.update_animation_player(self.screen, side=False)

    def update_animation_player(self, screen, side):
        self.player_anim_count += 1
        if side:
            screen.blit(self.resize_player_left[self.player_anim_count % len(self.resize_player_left)],
                        (self.x, self.y))
        else:
            screen.blit(self.resize_player_right[self.player_anim_count % len(self.resize_player_right)],
                        (self.x, self.y))
        self.player_rect.topleft = (self.x, self.y)

    def speed(self, keys):
        if keys[pygame.K_a] and self.x > 50:
            self.x -= self.player_speed
        elif keys[pygame.K_d] and self.x < 740:
            self.x += self.player_speed
        self.player_rect.topleft = (self.x, self.y)

    def jump(self, keys):
        if not self.is_jump:
            if keys[pygame.K_SPACE] or keys[pygame.K_w]:
                self.is_jump = True
        else:
            if self.jump_count >= -8:
                if self.jump_count > 0:
                    self.y -= (self.jump_count ** 2) / 2
                else:
                    self.y += (self.jump_count ** 2) / 2
                self.jump_count -= 1
            else:
                self.is_jump = False
                self.jump_count = 8
        self.player_rect.topleft = (self.x, self.y)


class Shuriken(pygame.sprite.Sprite):
    def __init__(self, game, player):
        super().__init__()
        self.shuriken_cols = []
        self.shuriken_left = 5
        self.shuriken_anim_count = 0
        self.game = game
        self.player = player
        self.shuriken = [pygame.image.load(f'pictures/suriken/suriken_{i}.png').convert_alpha() for i in range(1, 4)]
        self.resize_shuriken = [pygame.transform.scale(image, (30, 20)) for image in self.shuriken]
        self.shuriken_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.shuriken_timer, 5000)
        self.ghost = Ghost(self, self.player, self.shuriken)
        self.shuriken_rect = pygame.Rect(self.player.x + 30, self.player.y + 20, 30, 20)

    def shuriken_side(self):
        if self.shuriken_cols:
            self.shuriken_anim_count += 1
            for i in range(len(self.shuriken_cols) - 1, -1, -1):
                shuriken_rect, shuriken_direction = self.shuriken_cols[i]
                self.game.screen.blit(self.resize_shuriken[self.shuriken_anim_count % len(self.resize_shuriken)],
                                      (shuriken_rect.x, shuriken_rect.y))
                shuriken_rect.x += 15 * shuriken_direction

                if shuriken_rect.x > 1200 or shuriken_rect.x < 0:
                    self.shuriken_cols.pop(i)


class Ghost(pygame.sprite.Sprite):
    def __init__(self, game, player, shuriken):
        super().__init__()
        self.ghost_in_game = []
        self.enemy_ghost = pygame.transform.scale(pygame.image.load('pictures/enemy/ghost/ghost_1.png'), (40, 60))
        self.ghost_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ghost_timer, random.randrange(5000, 8000))
        self.player = player
        self.game = game
        self.shuriken = shuriken

    def update_ghost(self, background):
        if self.ghost_in_game and not background:
            for (i, el) in enumerate(self.ghost_in_game):
                self.game.screen.blit(self.enemy_ghost, (el.x, el.y))
                el.x -= 10
                if el.x < -100:
                    self.ghost_in_game.pop(i)
                if self.player.player_rect.colliderect(el):
                    self.player.hp -= 1
                    self.ghost_in_game.pop(i)
                for ghost_rect in self.ghost_in_game:
                    ghost_collision_rect = pygame.Rect(ghost_rect.x, ghost_rect.y, 40, 60)
                    for shuriken_rect, _ in self.shuriken.shuriken_cols:
                        if shuriken_rect.colliderect(ghost_collision_rect):
                            self.shuriken.shuriken_cols.remove((shuriken_rect, _))
                            self.ghost_in_game.remove(ghost_rect)
                            self.game.kills_enemy += 1


class Skeleton(pygame.sprite.Sprite):
    def __init__(self, game, player, shuriken):
        super().__init__()
        self.skeleton_in_game = []
        self.skeleton = [pygame.image.load(f'pictures/enemy/skeleton/skeleton_{i}.png').convert_alpha() for i in
                         range(1, 4)]
        self.skeleton_resize = [pygame.transform.scale(image, (55, 75)) for image in self.skeleton]
        self.skeleton_timer = pygame.USEREVENT + 3
        pygame.time.set_timer(self.skeleton_timer, random.randrange(7000, 10000))
        self.player = player
        self.game = game
        self.shuriken = shuriken
        self.hits = 0
        self.skeleton_anim_count = 0

    def update_skeleton(self, background):
        if self.skeleton_in_game and not background:
            for (i, el) in enumerate(self.skeleton_in_game):
                current_frame = self.skeleton_resize[self.skeleton_anim_count % len(self.skeleton_resize)]
                self.game.screen.blit(current_frame, (el.x, el.y))
                self.skeleton_anim_count += 1
                if self.hits % 2 != 0:
                    el.x -= 5
                else:
                    el.x -= 9
                if el.x < -100:
                    self.skeleton_in_game.pop(i)
                if self.player.player_rect.colliderect(el):
                    self.player.hp -= 1
                    self.skeleton_in_game.pop(i)
                for skeleton_rect in self.skeleton_in_game:
                    skeleton_collision_rect = pygame.Rect(skeleton_rect.x, skeleton_rect.y, 40, 60)
                    for shuriken_rect, _ in self.shuriken.shuriken_cols:
                        if shuriken_rect.colliderect(skeleton_collision_rect):
                            self.hits += 1
                            self.shuriken.shuriken_cols.remove((shuriken_rect, _))
                            if self.hits % 2 == 0:
                                self.skeleton_in_game.remove(skeleton_rect)
                                self.game.kills_enemy += 1


class Bat(pygame.sprite.Sprite):
    def __init__(self, game, player, shuriken):
        super().__init__()
        self.bat_in_game = []
        self.bat = [pygame.image.load(f'pictures/enemy/bat/bat_{i}.png').convert_alpha() for i in range(1, 3)]
        self.bat_resize = [pygame.transform.scale(image, (35, 55)) for image in self.bat]
        self.bat_timer = pygame.USEREVENT + 4
        pygame.time.set_timer(self.bat_timer, random.randrange(7000, 10000))
        self.player = player
        self.game = game
        self.shuriken = shuriken
        self.bat_anim_count = 0
        self.last_update = pygame.time.get_ticks()
        self.ANIMATION_SPEED = 150

    def update_bat(self, background):
        if self.bat_in_game and not background:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update > self.ANIMATION_SPEED:
                self.bat_anim_count += 1
                self.last_update = current_time
            for (i, el) in enumerate(self.bat_in_game):
                current_frame = self.bat_resize[self.bat_anim_count % len(self.bat_resize)]
                self.game.screen.blit(current_frame, (el.x, el.y))
                el.x -= 12
                if el.x < -100:
                    self.bat_in_game.pop(i)
                if self.player.player_rect.colliderect(el):
                    self.player.hp -= 1
                    self.bat_in_game.pop(i)
                for bat_rect in self.bat_in_game:
                    bat_collision_rect = pygame.Rect(bat_rect.x, bat_rect.y, 40, 60)
                    for shuriken_rect, _ in self.shuriken.shuriken_cols:
                        if shuriken_rect.colliderect(bat_collision_rect):
                            self.shuriken.shuriken_cols.remove((shuriken_rect, _))
                            self.bat_in_game.remove(bat_rect)
                            self.game.kills_enemy += 1


class Image(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.bg = pygame.transform.scale(pygame.image.load('pictures/gameBackground_5.jpg'),
                                         (self.screen_width, self.screen_height))
        self.bg_second = pygame.transform.scale(pygame.image.load('pictures/gameBackground_9.jpg'),
                                                (self.screen_width, self.screen_height))
        self.bg_death = pygame.transform.scale(pygame.image.load('pictures/backgroundDeath.jpg'),
                                               (self.screen_width, self.screen_height))
        self.bg_cloud = pygame.transform.scale(pygame.image.load('pictures/gameBackground_cloud.png'),
                                               (self.screen_width, 233))

        self.menu = pygame.image.load('pictures/Menu.png')
        self.menu_island = pygame.image.load('pictures/Menu_island.png')
        self.shop = pygame.image.load('pictures/Shop.png')

        self.key_a = pygame.transform.scale(pygame.image.load('pictures/buttons/key_a.png'), (50, 50))
        self.key_d = pygame.transform.scale(pygame.image.load('pictures/buttons/key_d.png'), (50, 50))
        self.key_w = pygame.transform.scale(pygame.image.load('pictures/buttons/key_w.png'), (50, 50))
        self.key_space = pygame.transform.scale(pygame.image.load('pictures/buttons/key_space.png'), (80, 60))
        self.left_click = pygame.transform.scale(pygame.image.load('pictures/buttons/left-click.png'), (60, 60))
        self.right_arrow = pygame.transform.scale(pygame.image.load('pictures/buttons/right-arrow.png'), (90, 80))
class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen_width = 800
        self.screen_height = 400
        self.player_x = 150
        self.player_y = 275
        self.bg_x = 0
        self.kills_enemy = 0

        self.island_y = 50
        self.island_y_temp = -1

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.start_label_rect = pygame.Rect((180, 45), (311, 107))
        self.shop_label_rect = pygame.Rect((180, 45), (332, 182))
        self.shop_back_rect = pygame.Rect((172, 52), (314, 275))
        self.shop_plus_hp_rect = pygame.Rect((25, 44), (302, 206))
        self.shop_plus_shuriken_rect = pygame.Rect((25, 44), (568, 206))
        self.exit_label_rect = pygame.Rect((180, 45), (332, 258))

        self.image = Image(self.screen_width, self.screen_height)
        self.player = Player(self.player_x, self.player_y, self.screen)
        self.shuriken = Shuriken(self, self.player)
        self.ghost = Ghost(self, self.player, self.shuriken)
        self.skeleton = Skeleton(self, self.player, self.shuriken)
        self.bat = Bat(self, self.player, self.shuriken)

        try:
            with open('suriken_data.txt', 'r') as file:
                self.plus_shuriken = int(file.readline())
        except FileNotFoundError:
            with open('suriken_data.txt', 'w') as file:
                file.write("0")
                self.plus_shuriken = 0
        self.shuriken.shuriken_left = 5 + self.plus_shuriken

        if self.shuriken.shuriken_left > 5:
            self.shuriken.shuriken_left -= self.plus_shuriken

        self.points = pygame.font.Font('fonts/Roboto-Regular.ttf', 20)
        self.text_shuriken = self.points.render('Shuriken: ' + str(self.shuriken.shuriken_left + self.plus_shuriken),
                                                True, (255, 255, 255))
        self.text_kills = self.points.render('Kills: ' + str(self.kills_enemy), True, (255, 255, 255))

        self.points_for_kills = pygame.font.Font('fonts/Roboto-Regular.ttf', 25)
        self.text_kills_after = self.points_for_kills.render('Kills: ' + str(self.kills_enemy), True, (255, 255, 255))

        self.label_for_lose = pygame.font.Font('fonts/Roboto-Regular.ttf', 40)
        self.lose_label = self.label_for_lose.render('You lose:(', True, (255, 0, 63))

        self.label = pygame.font.Font('fonts/Roboto-Regular.ttf', 30)
        self.restart_label = self.label.render('Play again', True, (237, 237, 237))
        self.restart_label_rect = self.restart_label.get_rect(topleft=(340, 200))

        self.restart_label_menu = self.label.render('Main menu', True, (237, 237, 237))
        self.restart_label_menu_rect = self.restart_label_menu.get_rect(topleft=(340, 250))

        try:
            with open('kills_data.txt', 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            with open('kills_data.txt', 'w') as file:
                file.write(str("Points: ") + "0" + '\n')

        with open('kills_data.txt', 'r') as file:
            lines = file.readlines()
            temp = 0
            for line in lines:
                parts = line.split()
                if len(parts) == 2 and parts[0] == "Points:":
                    score = int(parts[1])
                    temp += score

        self.all_points = temp

        with open('all_points.txt', 'a') as file:
            file.write(str(self.all_points) + '\n')

        try:
            with open('all_points.txt', 'r') as file:
                all_lines = file.readlines()
                if temp == self.all_points:
                    self.all_points = int(all_lines[-1].strip())
                if temp != self.all_points:
                    self.all_points = int(all_lines[-2].strip())
        except FileNotFoundError:
            with open('all_points.txt', 'w') as file:
                file.write(str(self.all_points))

        try:
            with open('hp_data.txt', 'r') as file:
                plus_str = file.readline().strip()
                self.plus = int(plus_str) if plus_str else 0
        except FileNotFoundError:
            with open('hp_data.txt', 'w') as file:
                file.write("0")
                self.plus = 0
        self.player.hp = 3 + self.plus

        if self.player.hp > 3:
            self.player.hp -= self.plus

        self.text_hp = self.points.render('HP: ' + str(self.player.hp + self.plus), True, (255, 255, 255))

        self.start_ticks = pygame.time.get_ticks()
        self.max_score = 0
        self.keys = pygame.key.get_pressed()
        self.background = True
        self.gameplay = True
        self.running = True
        self.menu_mode = True
        self.shop_mode = False
        self.game_over = False

    def run(self):
        while self.running:
            if self.menu_mode:
                self.menuWinows()
            elif self.shop_mode:
                self.shopWindow()
            else:
                if self.gameplay:
                    self.draw()
                    self.handle_events()
                    self.shuriken.shuriken_side()

                    self.player.update_player(self.keys)
                    self.player.speed(self.keys)
                    self.player.jump(self.keys)

                    self.ghost.update_ghost(self.background)
                    self.skeleton.update_skeleton(self.background)
                    self.bat.update_bat(self.background)

                    self.text()

                    self.keys = pygame.key.get_pressed()
                else:
                    self.death_screen()

            pygame.display.flip()
            self.clock.tick(20)

    def menuWinows(self):
        self.text_hp = self.points.render('HP: ' + str(self.player.hp + self.plus), True, (255, 255, 255))
        self.text_shuriken = self.points.render('Shuriken: ' + str(self.shuriken.shuriken_left + self.plus_shuriken),
                                                True, (255, 255, 255))
        with open('hp_data.txt', 'w') as file:
            file.write(str(self.plus))
        with open('suriken_data.txt', 'w') as file:
            file.write(str(self.plus_shuriken))
        self.screen.blit(self.image.menu, (0, 0))
        self.screen.blit(self.image.menu_island, (80, 5 - self.island_y))
        self.island_y += self.island_y_temp
        if self.island_y <= 0 or self.island_y >= 50:
            self.island_y_temp *= -1
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.start_label_rect.collidepoint(event.pos):
                        self.player.hp = 3 + self.plus
                        self.shuriken.shuriken_left = 5 + self.plus_shuriken
                        self.menu_mode = False
                        self.player.x = 150
                        self.background = True
                        self.gameplay = True
                        self.start_ticks = pygame.time.get_ticks()
                    elif self.shop_label_rect.collidepoint(event.pos):
                        self.shop_mode = True
                        self.menu_mode = False

                    elif self.exit_label_rect.collidepoint(event.pos):
                        self.running = False
                        pygame.quit()

    def shopWindow(self):
        self.screen.blit(self.image.shop, (0, 0))
        self.text_kills_after = self.points_for_kills.render('Points: ' + str(self.all_points), True, (255, 255, 255))
        self.screen.blit(self.text_hp, (240, 220))
        self.screen.blit(self.text_shuriken, (460, 220))
        self.screen.blit(self.text_kills_after, (360, 75))
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.shop_plus_hp_rect.collidepoint(event.pos):
                        if self.all_points >= 10:
                            self.plus += 1
                            with open('hp_data.txt', 'w') as file:
                                file.write(str(self.plus))
                            self.all_points -= 10
                            self.text_hp = self.points.render('HP: ' + str(self.player.hp + self.plus), True,
                                                              (19, 173, 47))
                            self.screen.blit(self.text_hp, (240, 220))
                        else:
                            self.text_hp = self.points.render('HP: ' + str(self.player.hp + self.plus), True,
                                                              (166, 18, 10))
                            self.screen.blit(self.text_hp, (240, 220))
                        with open('all_points.txt', 'a') as file:
                            file.write(str(self.all_points) + '\n')
                    elif self.shop_plus_shuriken_rect.collidepoint(event.pos):
                        if self.all_points >= 5:
                            self.plus_shuriken += 1
                            with open('suriken_data.txt', 'w') as file:
                                file.write(str(self.plus_shuriken))
                            self.all_points -= 5
                            self.text_shuriken = self.points.render(
                                'Shuriken: ' + str(self.shuriken.shuriken_left + self.plus_shuriken), True,
                                (19, 173, 47))
                        else:
                            self.text_shuriken = self.points.render(
                                'Shuriken: ' + str(self.shuriken.shuriken_left + self.plus_shuriken), True,
                                (166, 18, 10))
                        with open('all_points.txt', 'a') as file:
                            file.write(str(self.all_points) + '\n')
                    elif self.shop_back_rect.collidepoint(event.pos):
                        self.shop_mode = False
                        self.menu_mode = True

    def death_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
        self.screen.blit(self.image.bg_death, (0, 0))
        with open('kills_data.txt', 'r') as file:
            lines = file.readlines()

        for line in lines:
            parts = line.split()
            if len(parts) == 2 and parts[0] == "Points:":
                score = int(parts[1])
                if score > self.max_score:
                    self.max_score = score

        if self.kills_enemy == self.max_score:
            self.text_kills_after = self.points_for_kills.render('New record: ' + str(self.kills_enemy), True,
                                                                 (255, 255, 255))
            self.screen.blit(self.text_kills_after, (350, 140))

        else:
            self.text_kills_after = self.points_for_kills.render(
                'Your result: ' + str(self.kills_enemy) + " Record: " + str(self.max_score), True, (255, 255, 255))
            self.screen.blit(self.text_kills_after, (300, 140))

        self.screen.blit(self.lose_label, (340, 80))
        self.screen.blit(self.restart_label, self.restart_label_rect)
        self.screen.blit(self.restart_label_menu, self.restart_label_menu_rect)

        mouse = pygame.mouse.get_pos()
        if self.restart_label_menu_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            self.menu_mode = True
            self.player.hp = 3 + self.plus
            self.shuriken.shuriken_left = 5
            self.all_points += self.kills_enemy
            with open('all_points.txt', 'a') as file:
                file.write(str(self.all_points) + '\n')
            self.kills_enemy = 0

        if self.restart_label_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            self.all_points += self.kills_enemy
            with open('all_points.txt', 'a') as file:
                file.write(str(self.all_points) + '\n')
            self.gameplay = True
            self.game_over = False
            self.player.x = 150
            self.ghost.ghost_in_game.clear()
            self.skeleton.skeleton_in_game.clear()
            self.bat.bat_in_game.clear()
            self.player.hp = 3 + self.plus
            self.shuriken.shuriken_left = 5 + self.plus_shuriken
            self.kills_enemy = 0
            self.start_ticks = pygame.time.get_ticks()
            self.background = True

    def handle_events(self):
        if self.player.hp <= 0 and not self.game_over:
            with open('kills_data.txt', 'a') as file:
                file.write(str("Points: ") + str(self.kills_enemy) + '\n')
            self.game_over = True

        if self.player.hp <= 0:
            self.gameplay = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                with open('all_points.txt', 'a') as file:
                    file.write(str(self.all_points) + '\n')
                self.running = False
                pygame.quit()
            if event.type == self.ghost.ghost_timer:
                self.ghost.enemy_rect = pygame.Rect(840, 270, 40, 60)
                self.ghost.ghost_in_game.append(self.ghost.enemy_rect)

            if event.type == self.skeleton.skeleton_timer:
                self.skeleton.skeleton_rect = pygame.Rect(840, 270, 40, 60)
                self.skeleton.skeleton_in_game.append(self.skeleton.skeleton_rect)

            if event.type == self.bat.bat_timer:
                self.bat.bat_rect = pygame.Rect(840, 200, 40, 60)
                self.bat.bat_in_game.append(self.bat.bat_rect)

            if event.type == self.shuriken.shuriken_timer and self.shuriken.shuriken_left < 5 + self.plus_shuriken:
                self.shuriken.shuriken_left += 1

            if self.gameplay and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 0 < self.shuriken.shuriken_left:
                shuriken_rect = pygame.Rect(self.player.player_rect.x + 30, self.player.player_rect.y + 20, 30, 20)
                mouse_x, _ = pygame.mouse.get_pos()
                if mouse_x <= self.player.player_rect.x:
                    shuriken_direction = -1
                else:
                    shuriken_direction = 1
                self.shuriken.shuriken_cols.append((shuriken_rect, shuriken_direction))
                self.shuriken.shuriken_left -= 1

    def draw(self):
        if self.player.x < 600 and self.background:
            self.screen.blit(self.image.bg, (0, 0))
            self.screen.blit(self.image.key_a, (210, 200))
            self.screen.blit(self.image.key_d, (300, 200))
            self.screen.blit(self.image.key_w, (255, 140))
            self.screen.blit(self.image.key_space, (410, 200))
            self.screen.blit(self.image.left_click, (490, 200))
            self.screen.blit(self.image.right_arrow, (590, 240))
        else:
            self.background = False
            self.screen.blit(self.image.bg_second, (0, 0))
            self.screen.blit(self.image.bg_cloud, (self.bg_x, 0))
            self.screen.blit(self.image.bg_cloud, (self.bg_x + self.screen_width, 0))
            self.bg_x -= 2
            if self.bg_x == -self.bg_x:
                self.bg_x = 0

    def text(self):
        if self.background is False:
            seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
            minutes = seconds // 60
            seconds = seconds % 60
            text_timer = self.points.render('Time: ' + str(int(minutes)) + ' : ' + str(int(seconds)), True,
                                            (179, 16, 57))
            self.screen.blit(text_timer, (680, 10))

            self.text_kills = self.points.render('Kills: ' + str(self.kills_enemy), True, (255, 255, 255))
            self.text_shuriken = self.points.render('Shuriken: ' + str(self.shuriken.shuriken_left), True,
                                                    (255, 255, 255))
            self.text_hp = self.points.render('HP: ' + str(self.player.hp), True, (255, 255, 255))

            self.screen.blit(self.text_shuriken, (10, 10))
            self.screen.blit(self.text_hp, (10, 40))
            self.screen.blit(self.text_kills, (10, 80))


game = Game()
game.run()
