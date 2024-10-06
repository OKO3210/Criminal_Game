import pygame
from frontend import GameWindow
from backend import Backend
from config import *

class Controller:
    def __init__(self):
        self.frontend_object = GameWindow(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.backend_object = Backend()
        self.running = True
        self.waiting_for_response = False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.frontend_object.running = False
                    self.running = False

                if self.frontend_object.show_menu:
                    self.frontend_object.menu_events(event)
                elif not self.frontend_object.introduction_finished:
                    self.frontend_object.handle_introduction(event)
                elif self.frontend_object.animation_phase:
                    pass
                elif self.frontend_object.show_tutorial:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.frontend_object.show_tutorial = False
                else:
                    self.handle_dialogue(event)

            if self.frontend_object.show_menu:
                self.frontend_object.afficher_menu()
            else:
                self.frontend_object.screen.blit(self.frontend_object.background_image, (0, 0))
                if not self.frontend_object.introduction_finished:
                    self.frontend_object.afficher_intro_dialogue()
                elif self.frontend_object.animation_phase:
                    self.frontend_object.afficher_animation()
                elif self.frontend_object.show_tutorial:
                    self.frontend_object.afficher_tutoriel()
                else:
                    if not self.waiting_for_response:
                        self.frontend_object.afficher_dialogue()

            self.check_score()

            pygame.display.update()

        if self.backend_object.player_score >= 5:
            self.frontend_object.afficher_victoire()
        elif self.backend_object.player_score <= 0:
            self.frontend_object.afficher_defaite()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    waiting = False

        pygame.quit()

    def handle_dialogue(self, event):
        """Gérer les interactions de dialogue avec l'IA."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.frontend_object.input_box.collidepoint(event.pos):
                self.frontend_object.active = True
                self.frontend_object.color = self.frontend_object.color_active
                self.frontend_object.mami_message = False
            else:
                self.frontend_object.active = False
                self.frontend_object.color = self.frontend_object.color_inactive

        if event.type == pygame.KEYDOWN and self.frontend_object.active:
            if event.key == pygame.K_RETURN:
                self.send_message()
            elif event.key == pygame.K_BACKSPACE:
                if len(self.frontend_object.text_lines[-1]) > 0:
                    self.frontend_object.text_lines[-1] = self.frontend_object.text_lines[-1][:-1]
                elif len(self.frontend_object.text_lines) > 1:
                    self.frontend_object.text_lines.pop()
            else:
                current_line = self.frontend_object.text_lines[-1] + event.unicode
                text_width = self.frontend_object.font.size(current_line)[0]
                if text_width < self.frontend_object.input_box.width - 20:
                    self.frontend_object.text_lines[-1] = current_line
                else:
                    if len(self.frontend_object.text_lines) * self.frontend_object.font.get_linesize() < self.frontend_object.input_box.height - self.frontend_object.font.get_linesize():
                        self.frontend_object.text_lines.append(event.unicode)

    def send_message(self):
        user_message = " ".join(self.frontend_object.text_lines).strip()
        if user_message:
            self.frontend_object.messages_list.append({"role": "Jhon", "content": user_message})
            print(f"Message de Jhon ajouté à la liste : {self.frontend_object.messages_list}")
            self.waiting_for_response = True
            response_generator = self.backend_object.get_mamie_response(user_message)
            full_response = ""
            for response_chunk in response_generator:
                full_response += response_chunk
                self.frontend_object.update_mami_response(full_response)
                pygame.time.wait(50)
            self.waiting_for_response = False
            self.frontend_object.mami_message = True
            self.frontend_object.text_lines = ['']
            self.frontend_object.active = False
            self.frontend_object.color = self.frontend_object.color_inactive
            self.check_score()


    def check_score(self):
        """Vérifier le score du joueur et afficher l'écran de victoire ou de défaite."""
        if self.backend_object.player_score >= 5:
            self.frontend_object.afficher_victoire()
            self.running = False
        elif self.backend_object.player_score <= 0:
            self.frontend_object.afficher_defaite()
            self.running = False