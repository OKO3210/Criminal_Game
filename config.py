import pygame

# Dimensions de la fenêtre
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Chemins des fichiers
BACKGROUND_IMAGE_PATH = "./map/map_1.webp"
MENU_BACKGROUND_PATH = "./menu/Menu_Game.webp"
VICTORY_IMAGE_PATH = "./ecrans_fin/victory.webp"
DEFEAT_IMAGE_PATH = "./ecrans_fin/defeat.webp"

# Chemins des sprites
SPRITE_PRINCIPAL_NORMAL_PATH = "./sprites/Sprite_perso_principal.webp"
SPRITE_PRINCIPAL_SOMBRE_PATH = "./sprites/Sprite_perso_principal_assombrie.webp"
SPRITE_MAMI_NORMAL_PATH = "./sprites/Sprite_mami.webp"
SPRITE_MAMI_SOMBRE_PATH = "./sprites/Sprite_mami_assombrie.webp"
MAMI_MAP_SPRITE_PATH = "./sprite_perso_map/mami.webp"

# Chemins des sons
BACKGROUND_MUSIC_PATH = "./son/musique_1.mp3"
VICTORY_SOUND_PATH = "./son/applaudissement.mp3"
DEFEAT_SOUND_PATH = "./son/hurlement.mp3"

# Paramètres du jeu
PLAYER_INITIAL_SCORE = 2
ANIMATION_SPEED = 0.1
MUSIC_VOLUME = 0.3

# Dimensions des éléments d'interface
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 50

# Chemins des sprites d'animation
WALKING_SPRITE_PATHS = ["./sprite_perso_map/marche_1.png", "./sprite_perso_map/marche_2.png"]
STOP_SPRITE_PATH = "./sprite_perso_map/marche_1.png"

# Paramètres de dialogue
DIALOGUE_BOX_HEIGHT = 200
INPUT_BOX_HEIGHT = 30