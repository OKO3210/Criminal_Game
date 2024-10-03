import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

# Green Flag Red Flag

score = [0,1,2]
green_flags = ["bateau", "gateau"]
red_flags = ["braquage", "loup garou"]

dump = []

# Historique de conversation (ajoute les messages ici)

npc_info = (
    "Tu es une grand-mère amicale qui vit seule dans une petite maison à la lisière d'une forêt. "
    "Ce soir, juste avant la pleine lune, un jeune homme sonne à ta porte. "
    "Tu es bienveillante, mais prudente, car tu as entendu des rumeurs sur les loups-garous dans la région. "
    "Ta tâche est de décider si tu vas laisser entrer ce jeune homme ou non. "
    "Tu réagiras en fonction des mots qu'il utilise. "
)
context = (
    f"Je cherche a te convaincre de te laisser entrer chez toi, si j'emploie un mot contenu dans la variable {green_flags}, tu seras contente. a l'inverse, si j'emploie un mot contenu dans la variable {red_flags}, tu seras mécontente. Maintenant pose moi une question"
    "Il faudra orienter les reponses de l'interlocuteur vers les red flags"
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

    # Appel de l'API avec l'historique de conversation
    chat_response = client.chat.complete(
        model=model,
        messages=conversation_history
    )

    reponse = chat_response.choices[0].message.content
    print(reponse)


    while player_score != score[0] : 

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

        for flag in red_flags :
            if flag in prompt :
                player_score -= 1
                dump.append(flag)
                red_flags.remove(flag)

        for flag in green_flags :
            if flag in prompt :
                player_score += 1
                dump.append(flag)
                green_flags.remove(flag)
         
        conversation_history.append({"role" : "assistant", "content":reponse})
        print("player_score : ", player_score)
        print(chat_response.choices[0].message.content)

start_conversation(npc_info, context)