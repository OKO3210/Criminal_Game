import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

# Historique de conversation (ajoute les messages ici)




def start_conversation() :

    win_line = "Vous etes invité à continuer la conversation à l'interieur !"
    loss_line = "La grand mère claque la porte violemment"

    player_score = 2
    conversation_history = []

    # Green Flag/Red Flag

    green_flags = ["bateau", "gateau", "dodo", "oiseau", "halo"]
    red_flags = ["braquage", "loup garou", "loup", "sang", "tuer"]

    dump = []

    npc_info = (
    "Tu es une grand-mère amicale qui vit seule dans une petite maison à la lisière d'une forêt. "
    "Ce soir, juste avant la pleine lune, un jeune homme sonne à ta porte. "
    "Tu es bienveillante, mais prudente, car tu as entendu des rumeurs sur les loups-garous dans la région. "
    "Ta tâche est de décider si tu vas laisser entrer ce jeune homme ou non. "
    "Tu réagiras en fonction des mots qu'il utilise. "
    )
    context = (
    f"Je cherche a te convaincre de te laisser entrer chez toi, si j'emploie un mot dont le champ lexical est proche des mots contenu dans la variable {green_flags}, tu seras contente. a l'inverse, si j'emploie un mot dont le champs lexical est proche d'un mot contenu dans la variable {red_flags}, tu seras mécontente. Maintenant pose moi une question"
    "Il faudra orienter les reponses de l'interlocuteur vers les red flags"
    )

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


    while True : 

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

        if any(flag in prompt for flag in red_flags):
            player_score -= 1  # Décrémenter le score si red flag détecté

        for flag in green_flags :
            if flag in prompt :
                player_score += 1
                dump.append(flag)
                green_flags.remove(flag)
         
        conversation_history.append({"role" : "assistant", "content":reponse})
        print("player_score : ", player_score)
        print(chat_response.choices[0].message.content)
    
        if (player_score == 0) :
            print(loss_line)
            break
        if (player_score == 5) :
            print(win_line)
            break

start_conversation()