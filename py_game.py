import pygame
import sys
import time

class AnimatedSprite:
    def __init__(self, image_paths, stop_image_path):
        self.walking_images = [pygame.transform.scale(pygame.image.load(img).convert_alpha(), (50, 50)) for img in image_paths]
        self.stop_image = pygame.transform.scale(pygame.image.load(stop_image_path).convert_alpha(), (50, 50))
        self.index = 0
        self.animation_time = 0.2
        self.last_update_time = time.time()

    def update(self):
        current_time = time.time()
        if current_time - self.last_update_time > self.animation_time:
            self.index = (self.index + 1) % len(self.walking_images)
            self.last_update_time = current_time

    def draw(self, surface, x, y, is_moving):
        if is_moving:
            surface.blit(self.walking_images[self.index], (x, y))
        else:
            surface.blit(self.stop_image, (x, y))

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class GameWindow:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Criminal Game")
        self.running = True
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # --- Charger les assets du premier code ---
        self.background_image = pygame.image.load("./map/map_1.webp")
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        self.sprite_principal_clair = pygame.image.load("./sprites/Sprite_perso_principal.webp")
        self.sprite_principal_clair = pygame.transform.scale(self.sprite_principal_clair, (450, 750))
        self.sprite_principal_assombri = pygame.image.load("./sprites/Sprite_perso_principal_assombrie.webp")
        self.sprite_principal_assombri = pygame.transform.scale(self.sprite_principal_assombri, (450, 750))

        self.sprite_mami_clair = pygame.image.load("./sprites/Sprite_mami.webp")
        self.sprite_mami_clair = pygame.transform.scale(self.sprite_mami_clair, (450, 750))
        self.sprite_mami_assombri = pygame.image.load("./sprites/Sprite_mami_assombrie.webp")
        self.sprite_mami_assombri = pygame.transform.scale(self.sprite_mami_assombri, (450, 750))

        # --- Charger le sprite de Mami pour l'animation (elle est statique) ---
        self.mami_image = pygame.transform.scale(pygame.image.load("./sprite_perso_map/mami.webp").convert_alpha(), (30, 45))

        # Gestion du dialogue et introduction
        self.active = False
        self.text_lines = ['']
        self.input_box = pygame.Rect(60, 400, 900, 150)
        self.color_inactive = (100, 100, 100)
        self.color_active = (200, 200, 200)
        self.color = self.color_inactive
        self.font = pygame.font.Font(None, 36)
        self.intro_lines = ["Oh la la, j'ai super faim...", "Pas facile d'être un loup-garou.", "..."]
        self.current_intro_index = 0
        self.introduction_finished = False

        # --- Variables de dialogue ---
        self.mami_message = False  # Indique si c'est le tour de Mami de parler

        # --- Charger les assets du deuxième code ---
        self.personnage = AnimatedSprite(
            ["./sprite_perso_map/marche_1.png", "./sprite_perso_map/marche_2.png"],
            "./sprite_perso_map/marche_1.png"
        )
        self.personnage_x = int(0.9 * width)
        self.personnage_y = int(0.5667 * height)
        self.chemin = [(int(0.9 * width), int(0.5667 * height)), (int(0.69 * width), int(0.5667 * height)), 
                       (int(0.69 * width), int(0.5167 * height)), (int(0.64 * width), int(0.5167 * height)), 
                       (int(0.64 * width), int(0.283 * height)), (int(0.57 * width), int(0.283 * height))]
        self.target_index = 0
        self.speed = 0.15  # Ajustement de la vitesse
        self.animation_phase = False

        # Position de Mami (statique) sur la carte
        self.mami_x = int(0.54 * width)  # Position X statique de Mami
        self.mami_y = int(0.283 * height)  # Position Y statique de Mami

        # Menu setup
        self.show_menu = True
        self.menu_background = pygame.image.load("./menu/Menu_Game.webp").convert()
        self.menu_background = pygame.transform.scale(self.menu_background, (self.width, self.height))
        self.button_width = 200
        self.button_height = 50
        self.margin = 50

        self.start_button = Button(
            self.margin,
            self.height // 2 - self.button_height // 2,
            self.button_width,
            self.button_height,
            "Start",
            self.WHITE,
            self.BLACK
        )

        self.exit_button = Button(
            self.width - self.margin - self.button_width,
            self.height // 2 - self.button_height // 2,
            self.button_width,
            self.button_height,
            "Exit",
            self.WHITE,
            self.BLACK
        )

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.show_menu:
                    self.menu_events(event)
                elif not self.introduction_finished:
                    self.handle_introduction(event)
                elif self.animation_phase:
                    pass  # Aucune interaction durant l'animation
                else:
                    self.handle_dialogue(event)

            # Dessin de la scène
            if self.show_menu:
                self.afficher_menu()
            else:
                self.screen.blit(self.background_image, (0, 0))

                if not self.introduction_finished:
                    self.afficher_intro_dialogue()
                elif self.animation_phase:
                    self.afficher_animation()
                else:
                    self.afficher_dialogue()

            pygame.display.flip()

        pygame.quit()

    def afficher_menu(self):
        self.screen.blit(self.menu_background, (0, 0))
        self.start_button.draw(self.screen)
        self.exit_button.draw(self.screen)

    def menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.is_clicked(event.pos):
                self.show_menu = False
            elif self.exit_button.is_clicked(event.pos):
                self.running = False

    def handle_introduction(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.current_intro_index < len(self.intro_lines) - 1:
                self.current_intro_index += 1
            else:
                self.introduction_finished = True
                self.animation_phase = True  # Démarre l'animation après l'introduction

    def afficher_intro_dialogue(self):
        # Afficher le sprite du personnage principal pendant l'introduction
        self.screen.blit(self.sprite_principal_clair, (100, 50))
        pygame.draw.rect(self.screen, self.color_active, self.input_box, 0)
        current_line = self.intro_lines[self.current_intro_index]
        txt_surface = self.font.render(current_line, True, (255, 255, 255))
        self.screen.blit(txt_surface, (self.input_box.x + 10, self.input_box.y + 10))

    def afficher_animation(self):
        # Afficher Mami statique sur la carte
        self.screen.blit(self.mami_image, (self.mami_x, self.mami_y))

        # Déplacer le personnage principal
        is_moving = self.deplacer_personnage()
        self.personnage.update()
        self.personnage.draw(self.screen, self.personnage_x, self.personnage_y, is_moving)
        if not is_moving and self.target_index >= len(self.chemin):
            self.animation_phase = False  # Terminer l'animation, passe au dialogue

    def deplacer_personnage(self):
        if self.target_index >= len(self.chemin):
            return False
        target_x, target_y = self.chemin[self.target_index]
        is_moving = False
        if self.personnage_x < target_x:
            self.personnage_x += self.speed
            is_moving = True
        elif self.personnage_x > target_x:
            self.personnage_x -= self.speed
            is_moving = True
        if self.personnage_y < target_y:
            self.personnage_y += self.speed
            is_moving = True
        elif self.personnage_y > target_y:
            self.personnage_y -= self.speed
            is_moving = True
        if abs(self.personnage_x - target_x) < self.speed and abs(self.personnage_y - target_y) < self.speed:
            self.target_index += 1
        return is_moving

    def handle_dialogue(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                self.active = True
                self.color = self.color_active
                self.mami_message = False  # Jhon parle
            else:
                self.active = False
                self.color = self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.send_message()
            elif event.key == pygame.K_BACKSPACE:
                if len(self.text_lines[-1]) > 0:
                    self.text_lines[-1] = self.text_lines[-1][:-1]
                elif len(self.text_lines) > 1:
                    self.text_lines.pop()
            else:
                current_line = self.text_lines[-1] + event.unicode
                text_width = self.font.size(current_line)[0]
                if text_width < self.input_box.width - 20:
                    self.text_lines[-1] = current_line
                else:
                    if len(self.text_lines) * self.font.get_linesize() < self.input_box.height - self.font.get_linesize():
                        self.text_lines.append(event.unicode)

    def afficher_dialogue(self):
        # Affiche Jhon ou Mami en fonction de qui parle
        if self.mami_message:
            self.screen.blit(self.sprite_principal_assombri, (100, 50))  # Jhon assombri
            self.screen.blit(self.sprite_mami_clair, (self.width - 550, 50))  # Mami claire
        else:
            self.screen.blit(self.sprite_principal_clair, (100, 50))  # Jhon clair
            self.screen.blit(self.sprite_mami_assombri, (self.width - 550, 50))  # Mami assombrie

        pygame.draw.rect(self.screen, self.color, self.input_box, 0)

        if self.mami_message:
            mami_txt_surface = self.font.render("Mami :", True, (255, 255, 255))
            self.screen.blit(mami_txt_surface, (self.input_box.x + 10, self.input_box.y + 10))
            ok_txt_surface = self.font.render("Ok très bien", True, (255, 255, 255))
            self.screen.blit(ok_txt_surface, (self.input_box.x + 10, self.input_box.y + 10 + self.font.get_linesize()))
        else:
            jhon_txt_surface = self.font.render("Jhon :", True, (255, 255, 255))
            self.screen.blit(jhon_txt_surface, (self.input_box.x + 10, self.input_box.y + 10))
            for i, line in enumerate(self.text_lines):
                txt_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(txt_surface, (self.input_box.x + 10, self.input_box.y + 10 + self.font.get_linesize() * (i + 1)))

    def send_message(self):
        print(f"Jhon : {' '.join(self.text_lines)}")
        self.text_lines = ['']
        self.active = False
        self.color = self.color_inactive
        self.mami_message = True  # Après que Jhon parle, c'est le tour de Mami