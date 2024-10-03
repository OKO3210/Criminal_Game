import os
from mistralai import Mistral
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

# Green Flag Red Flag

#score = [0,1,2,3,4,5,6,7,8,9,10]
score = [0,1,2]
green_flags = ["bateau", "gateau"]
red_flags = ["braquage", "loup garou"]

# Historique de conversation (ajoute les messages ici)

npc_info = (
    "f{system_message}"
    "Tu es une grand-mère amicale qui vit seule dans une petite maison à la lisière d'une forêt. "
    "Ce soir, juste avant la pleine lune, un jeune homme sonne à ta porte. "
    "Tu es bienveillante, mais prudente, car tu as entendu des rumeurs sur les loups-garous dans la région. "
    "Ta tâche est de décider si tu vas laisser entrer ce jeune homme ou non. "
    "Tu réagiras en fonction des mots qu'il utilise. "
)
context =  (
    f"Si le jeune homme mentionne des mots contenus dans la variable {green_flags} "
    f"tu seras heureuse de l'accueillir. Mais si tu entends des mots contenus dans la variable {red_flags}"
    "tu seras méfiante et tu risques de lui claquer la porte au nez. "
    "Maintenant, pose-lui une question pour commencer la conversation."
)

def start_conversation(npc_info, context) :

    player_score = 1
    conversation_history = []

    # Initialize the conversation with a system message
    system_message = {
        "role": "system",
        "content": npc_info + context
    }
    conversation_history.append(system_message)

    # Call Api
    chat_response = client.chat.complete(
        model=model,
        messages=conversation_history
    )

    reponse = chat_response.choices[0].message.content
    print(chat_response.choices[0].message.content)

    while player_score != 2: 

        prompt = input()

        # Nouveau message
        new_message = {
            "role": "user",
            "content": prompt
        }

        # Ajouter le nouveau message à l'historique
        conversation_history.append(new_message)

        # Appel de l'API avec l'historique de conversation
        chat_response = client.chat.complete(
            model=model,
            messages=conversation_history
        )

        reponse = chat_response.choices[0].message.content

        # Check if green_flag/red_flag in question

        if any(flag in prompt for flag in red_flags):
            player_score -= 1  # Décrémenter le score si red flag détecté
        elif any(flag in prompt for flag in green_flags):
            player_score += 1  # Incrémenter le score si green flag détecté
                 
        conversation_history.append({"role" : "assistant", "content":reponse})
        
        print("conversation_history :", conversation_history)
        print("player_score : ", player_score)
        print(chat_response.choices[0].message.content)

start_conversation(npc_info, context)
