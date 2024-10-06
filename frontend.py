import pygame
import sys
import time
from config import *

class AnimatedSprite:
    """Classe pour gérer un sprite animé, comme un personnage qui marche."""
    def __init__(self, image_paths, stop_image_path):
        self.walking_images = [pygame.transform.scale(pygame.image.load(img).convert_alpha(), (50, 50)) for img in image_paths]
        self.stop_image = pygame.transform.scale(pygame.image.load(stop_image_path).convert_alpha(), (50, 50))
        
        self.index = 0
        self.animation_time = 0.2
        self.last_update_time = time.time()

    def update(self):
        """Met à jour l'image du sprite animée en fonction du temps écoulé."""
        current_time = time.time()
        if current_time - self.last_update_time > self.animation_time:
            self.index = (self.index + 1) % len(self.walking_images)
            self.last_update_time = current_time

    def draw(self, surface, x, y, is_moving):
        """Dessiner le sprite sur la surface en fonction de s'il est en mouvement ou non."""
        if is_moving:
            surface.blit(self.walking_images[self.index], (x, y))
        else:
            surface.blit(self.stop_image, (x, y))

class Button:
    """Classe pour gérer des boutons interactifs."""
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        """Dessiner le bouton avec son texte sur la surface donnée."""
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        """Vérifier si le bouton est cliqué en fonction de la position de la souris."""
        return self.rect.collidepoint(pos)

class GameWindow:
    """Classe principale qui gère la fenêtre du jeu et ses différents états."""
    def __init__(self, width, height):
        pygame.init()
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Criminal Game")
        self.running = True


        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        self.background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        self.sprite_principal_normal = pygame.image.load(SPRITE_PRINCIPAL_NORMAL_PATH)
        self.sprite_principal_clair = pygame.transform.scale(self.sprite_principal_normal, (450, 750))
        self.sprite_principal_sombre = pygame.image.load(SPRITE_PRINCIPAL_SOMBRE_PATH)
        self.sprite_principal_assombri = pygame.transform.scale(self.sprite_principal_sombre, (450, 750))


        self.sprite_mami_normal = pygame.image.load(SPRITE_MAMI_NORMAL_PATH)
        self.sprite_mami_clair = pygame.transform.scale(self.sprite_mami_normal, (450, 750))
        self.sprite_mami_sombre = pygame.image.load(SPRITE_MAMI_SOMBRE_PATH)
        self.sprite_mami_assombri = pygame.transform.scale(self.sprite_mami_sombre, (450, 750))
        self.mami_image = pygame.transform.scale(pygame.image.load(MAMI_MAP_SPRITE_PATH).convert_alpha(), (30, 45))

        self.messages_list = []

        self.active = False
        self.text_lines = ['']
        self.input_box = pygame.Rect(60, 400, 900, 150)
        self.color_inactive = (100, 100, 100)
        self.color_active = (200, 200, 200)
        self.color = self.color_inactive
        self.font = pygame.font.Font(None, 36)
        self.intro_lines = ["Oh la la, j'ai super faim...", "Pas facile d'être un loup-garou de nos jours.", "Attends, miam ! Ça sent vraiment bon la mamie. Avec un peu de ruse, je sens que je pourrais bien finir le ventre plein ce soir."]
        self.current_intro_index = 0
        self.introduction_finished = False

        self.mami_message = False

        self.personnage = AnimatedSprite(WALKING_SPRITE_PATHS, STOP_SPRITE_PATH)
        self.personnage_x = int(0.9 * width)
        self.personnage_y = int(0.5667 * height)
        self.chemin = [(int(0.9 * width), int(0.5667 * height)), (int(0.69 * width), int(0.5667 * height)), 
                       (int(0.69 * width), int(0.5167 * height)), (int(0.64 * width), int(0.5167 * height)), 
                       (int(0.64 * width), int(0.283 * height)), (int(0.57 * width), int(0.283 * height))]
        self.target_index = 0
        self.speed = 0.1
        self.animation_phase = False

        self.mami_x = int(0.54 * width)
        self.mami_y = int(0.283 * height)

        self.show_menu = True
        self.menu_background = pygame.image.load(MENU_BACKGROUND_PATH).convert()
        self.menu_background = pygame.transform.scale(self.menu_background, (self.width, self.height))
        self.button_width = 200
        self.button_height = 50 
        self.margin = 50

        dialogue_width = 800
        dialogue_height = 200
        dialogue_x = (self.width - dialogue_width) // 2
        dialogue_y = self.height - dialogue_height - 20
        self.dialogue_box = pygame.Rect(dialogue_x, dialogue_y, dialogue_width, dialogue_height)

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

        self.show_tutorial = False

        pygame.mixer.init()

        pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        
        pygame.mixer.music.play(-1)

        self.victory_sound = pygame.mixer.Sound(VICTORY_SOUND_PATH)
        self.defeat_sound = pygame.mixer.Sound(DEFEAT_SOUND_PATH)

    def afficher_menu(self):
        """Afficher le menu principal."""
        self.screen.blit(self.menu_background, (0, 0))
        self.start_button.draw(self.screen)
        self.exit_button.draw(self.screen)

    def menu_events(self, event):
        """Gérer les événements dans le menu."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.is_clicked(event.pos):
                self.fade_to_black()
                self.show_menu = False
            elif self.exit_button.is_clicked(event.pos):
                pygame.quit()
                sys.exit()

    def fade_to_black(self):
        fade_surface = pygame.Surface((self.width, self.height))
        fade_surface.fill((0, 0, 0))

        for alpha in range(0, 256, 2):
            fade_surface.set_alpha(alpha)
            self.screen.blit(self.menu_background, (0, 0))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(5)

        pygame.time.delay(500)

        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.sprite_principal_clair, (100, 50))
        for alpha in range(255, -1, -2):
            fade_surface.set_alpha(alpha)
            self.screen.blit(self.background_image, (0, 0))
            self.screen.blit(self.sprite_principal_clair, (100, 50))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(5)

    def handle_introduction(self, event):
        """Gérer les événements pendant l'introduction."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.current_intro_index < len(self.intro_lines) - 1:
                self.current_intro_index += 1
            else:
                self.introduction_finished = True
                self.animation_phase = True


    def afficher_intro_dialogue(self):
        """Afficher le dialogue d'introduction."""
        self.screen.blit(self.background_image, (0, 0))

        self.screen.blit(self.sprite_principal_clair, (100, 50))

        pygame.draw.rect(self.screen, self.WHITE, self.dialogue_box)
        pygame.draw.rect(self.screen, self.BLACK, self.dialogue_box, 2)

        current_line = self.intro_lines[self.current_intro_index]
        wrapped_text = self.wrap_text(f"Jhon: {current_line}", self.dialogue_box.width - 20)

        y = self.dialogue_box.top + 10
        for line in wrapped_text:
            text_surface = self.font.render(line, True, self.BLACK)
            self.screen.blit(text_surface, (self.dialogue_box.left + 10, y))
            y += self.font.get_linesize()

        instruction = "Appuyez sur Entrée pour continuer..."
        instruction_surface = self.font.render(instruction, True, self.BLACK)
        instruction_rect = instruction_surface.get_rect(bottom=self.dialogue_box.bottom - 10, right=self.dialogue_box.right - 10)
        self.screen.blit(instruction_surface, instruction_rect)

        pygame.display.flip()


    def afficher_animation(self):
        """Afficher l'animation du personnage se déplaçant vers Mami."""
        self.screen.blit(self.mami_image, (self.mami_x, self.mami_y))

        is_moving = self.deplacer_personnage()
        self.personnage.update()
        self.personnage.draw(self.screen, self.personnage_x, self.personnage_y, is_moving)

        if not is_moving and self.target_index >= len(self.chemin):
            self.animation_phase = False

    def deplacer_personnage(self):
        """Déplacer le personnage le long des points de cheminement définis."""
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

    def afficher_animation(self):
        """Afficher l'animation du personnage se déplaçant vers Mami."""
        self.screen.blit(self.mami_image, (self.mami_x, self.mami_y))
        is_moving = self.deplacer_personnage()
        self.personnage.update()
        self.personnage.draw(self.screen, self.personnage_x, self.personnage_y, is_moving)
        if not is_moving and self.target_index >= len(self.chemin):
            self.animation_phase = False
            self.show_tutorial = True

    def afficher_tutoriel(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        titre = "Tuto :"
        texte = [
            "Tu es un loup garou.",
            "Le but de ce jeu est de convaincre la mamie de vous laisser rentrer chez elle",
            "pour pouvoir la manger tranquillement le soir.",
            "Attention, si vous êtes trop suspect, elle risque de s'en aller",
            "en vous claquant la porte au nez.",
            "",
            "Appuyez sur Entrée pour continuer"
        ]

        total_height = len(texte) * self.font.get_linesize() + 50

        start_y = (self.height - total_height) // 2

        titre_surface = self.font.render(titre, True, self.WHITE)
        titre_rect = titre_surface.get_rect(center=(self.width // 2, start_y))
        self.screen.blit(titre_surface, titre_rect)

        y = start_y + 50
        for ligne in texte:
            texte_surface = self.font.render(ligne, True, self.WHITE)
            texte_rect = texte_surface.get_rect(center=(self.width // 2, y))
            self.screen.blit(texte_surface, texte_rect)
            y += self.font.get_linesize()

        pygame.display.flip()

    def handle_dialogue(self, event):
        """Gérer les événements pendant le dialogue."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                self.active = True
                self.color = self.color_active
                self.mami_message = False
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
        self.screen.blit(self.background_image, (0, 0))

        jhon_x = 100
        jhon_y = 50
        mami_x = self.width - 550
        mami_y = 50

        if self.mami_message:
            self.screen.blit(self.sprite_mami_clair, (mami_x, mami_y))
            self.screen.blit(self.sprite_principal_assombri, (jhon_x, jhon_y))
        else:
            self.screen.blit(self.sprite_mami_assombri, (mami_x, mami_y))
            self.screen.blit(self.sprite_principal_clair, (jhon_x, jhon_y))

        dialogue_box_height = 200
        self.dialogue_box = pygame.Rect(50, self.height - dialogue_box_height - 10, self.width - 100, dialogue_box_height)
        pygame.draw.rect(self.screen, self.WHITE, self.dialogue_box)
        pygame.draw.rect(self.screen, self.BLACK, self.dialogue_box, 2)

        input_box_height = 30
        self.input_box = pygame.Rect(60, self.dialogue_box.top + 10, self.width - 120, input_box_height)
        pygame.draw.rect(self.screen, self.color, self.input_box, 2)

        text_surface = self.font.render(self.text_lines[-1], True, self.BLACK)
        self.screen.blit(text_surface, (self.input_box.x + 5, self.input_box.y + 5))

        y = self.input_box.bottom + 10
        last_messages = self.messages_list[-2:] if len(self.messages_list) >= 2 else self.messages_list
        for message in last_messages:
            role = message["role"]
            content = message["content"]
            text = f"{role}: {content}"
            wrapped_text = self.wrap_text(text, self.dialogue_box.width - 20)
            
            for line in wrapped_text:
                text_surface = self.font.render(line, True, self.BLACK)
                if y + text_surface.get_height() > self.dialogue_box.bottom - 10:
                    break
                self.screen.blit(text_surface, (self.dialogue_box.left + 10, y))
                y += self.font.get_linesize()
            
            y += 10

        pygame.display.flip()

    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = self.font.render(word + " ", True, self.BLACK)
            word_width = word_surface.get_width()

            if current_width + word_width > max_width:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width

        if current_line:
            lines.append(" ".join(current_line))

        return lines
    
    def update_mami_response(self, response):
        if self.messages_list and self.messages_list[-1]["role"] == "Mamie":
            self.messages_list[-1]["content"] = response
        else:
            self.messages_list.append({"role": "Mamie", "content": response})
        self.afficher_dialogue()

    def send_message(self):
        """Envoyer le message de Jhon et passer à Mami."""
        print(f"Jhon : {' '.join(self.text_lines)}")
        self.text_lines = ['']
        self.active = False
        self.color = self.color_inactive
        self.mami_message = True

    def afficher_victoire(self):
        victory_image = pygame.image.load("./ecrans_fin/victory.webp")
        victory_image = pygame.transform.scale(victory_image, (self.width, self.height))
        self.screen.blit(victory_image, (0, 0))
        pygame.display.flip()
        
        self.victory_sound.play()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False

    def afficher_defaite(self):
        defeat_image = pygame.image.load("./ecrans_fin/defeat.webp")
        defeat_image = pygame.transform.scale(defeat_image, (self.width, self.height))
        self.screen.blit(defeat_image, (0, 0))
        pygame.display.flip()
        
        self.defeat_sound.play()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False