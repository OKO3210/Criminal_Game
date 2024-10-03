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

green_flags = ["mer", "patisserie", "fete"]
red_flags = ["braquage", "loup garou", "mort"]

# Historique de conversation (ajoute les messages ici)

npc_info = (
    "Tu es une grand-mère amicale qui vit seule dans une petite maison à la lisière d'une forêt. "
    "Ce soir, juste avant la pleine lune, un jeune homme sonne à ta porte. "
    "Tu es bienveillante, mais prudente, car tu as entendu des rumeurs sur les loups-garous dans la région. "
    "Ta tâche est de décider si tu vas laisser entrer ce jeune homme ou non. "
    "Tu réagiras en fonction des mots qu'il utilise. "
)
context =  (
    f"Si le jeune homme mentionne des mots contenus dans cette liste {green_flags} ou des concepts dans le même genre tu seras heureuse de l'accueillir. "
    f"Mais si tu entends des mots contenus dans cette liste {red_flags} ou des concepts dans le même genre tu seras méfiante et tu risques de lui claquer la porte au nez. "
    "A la fin de chacune des interractions avec le joueur tu renverras un nombre entier à la toute fin de ta réponse, il s'agit d'une note entre 0 et 3."
    "Quand le joueur enchaine des redflag la note se rapproche de 0."
    "Quand le joueur enchaine des green sa note s'améliore et se rapproche de 2"
    "La note du joueur est initialisée à 1"
    "La mamie doit orienter la discussion afin d'amener le joueur à dire un des redflags"
    "Maintenant, pose-lui une question pour commencer la conversation."
)



def start_conversation(npc_info, context) :

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
    print(reponse)


    conversation_history.append({"role": "system", "content": reponse})

    while True: 

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

                 
        conversation_history.append({"role" : "assistant", "content":reponse})

        print("REPONSE : ", reponse)

        note = reponse[-1]
        print("NOTE : ", note)

        if note == "0" or note == "3":
            print("BREAK")
            break

start_conversation(npc_info, context)
