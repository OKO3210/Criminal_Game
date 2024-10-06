import os
from mistralai import Mistral
from dotenv import load_dotenv
from mistralai.models.sdkerror import SDKError
import unidecode
from config import *

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

class Backend:
    def __init__(self):
        self.client = Mistral(api_key=api_key)
        self.conversation_history = []
        self.player_score = PLAYER_INITIAL_SCORE
        self.green_flags = ["bateau", "gateau", "dodo", "oiseau", "halo"]
        self.red_flags = ["braquage", "loup garou", "loup", "sang", "tuer", "braco"]
        self.dump = []
        self.used_green_flags = set()

    def start_conversation(self):
        try:
            npc_info_context = " ".join([
            "Tu es une grand-mère (assez âgée) amicale qui parle en français. Tu vis seule dans une petite maison à la lisière d'une forêt.",
            "Ce soir, juste avant la pleine lune, un jeune homme sonne à ta porte.",
            "Tu es bienveillante, mais prudente, car tu as entendu des rumeurs sur les loups-garous dans la région.",
            "Ta tâche est de décider si tu vas laisser entrer ce jeune homme ou non.",
            "Tu réagiras en fonction des sujets qu'il aborde et de son attitude envers ces sujets.",
            f"Les sujets positifs sont : {', '.join(self.green_flags)}. Si le jeune homme en parle positivement, tu seras contente et plus encline à lui faire confiance.",
            f"Les sujets négatifs sont : {', '.join(self.red_flags)}. Si le jeune homme en parle négativement, tu seras d'accord avec lui et plus encline à lui faire confiance.",
            "Si le jeune homme parle négativement des sujets positifs ou positivement des sujets négatifs, tu te méfieras davantage.",
            "Prends en compte les pluriels et les singuliers des mots dans ces sujets.",
            "N'utilise pas de texte en gras dans tes réponses.",
            "Garde tes réponses courtes et concises, sans dépasser 2-3 phrases maximum.",
            "Pose-moi une question pour commencer la conversation.",
        ])

            system_message = {
                "role": "system",
                "content": npc_info_context
            }
            self.conversation_history.append(system_message)

            chat_response = self.client.chat.stream(
                model=model,
                messages=self.conversation_history
            )

            initial_response = ""
            for chunk in chat_response:
                content = chunk.data.choices[0].delta.content
                if content:
                    initial_response += content
                    yield content

            return initial_response
        except SDKError as e:
            print(f"API error: {e}")
            return "Laisse-moi un peu réfléchir."
        

    def get_mamie_response(self, player_message):
        if not player_message:
            return "Je n'ai pas reçu votre message."

        try:
            print(f"Sending message to API: {player_message}")

            self.analyze_message(player_message)

            print("Player score:", self.player_score)

            if self.player_score >= 5:
                return "Oh, mon petit, tu m'as l'air bien sympathique. Entre donc, je t'en prie !"
            elif self.player_score <= 0:
                return "Je suis désolée, mais je ne pense pas pouvoir vous laisser entrer. Au revoir !"

            updated_context = " ".join([
                "Tu es une grand-mère (assez âgée) amicale qui parle en français. Tu n'es PAS une IA, mais une vraie personne âgée.",
                "Tu vis seule dans une petite maison à la lisière d'une forêt.",
                "Ce soir, juste avant la pleine lune, un jeune homme sonne à ta porte.",
                "Tu es bienveillante, mais prudente, car tu as entendu des rumeurs sur les loups-garous dans la région.",
                "Ta tâche est de décider si tu vas laisser entrer ce jeune homme ou non.",
                f"Si le jeune homme parle positivement des sujets suivants : {', '.join(self.green_flags)}, tu seras contente et plus encline à lui faire confiance.",
                f"En revanche, s'il parle négativement de ces sujets, tu seras mécontente et méfiante.",
                f"Si le jeune homme parle négativement des sujets suivants : {', '.join(self.red_flags)}, tu seras d'accord avec lui et plus encline à lui faire confiance.",
                f"En revanche, s'il parle positivement de ces sujets, tu seras mécontente et méfiante.",
                "Réagis en conséquence dans tes réponses, sans mentionner explicitement ces règles.",
                "Parle comme une vraie grand-mère, avec des expressions typiques d'une personne âgée.",
                "Essaie de faire des phrases courtes (maximum 70 caractères).",
                "Ne mentionne JAMAIS que tu es une IA ou un assistant virtuel.",
                "Dans ta réponse, inclus subtilement un indice lié soit à un green flag, soit à un red flag, sans mentionner directement ces termes.",
                "Varie tes réponses et évite de répéter les mêmes phrases.",
                "Continue la conversation en tenant compte des échanges précédents. Ne recommence pas la conversation depuis le début.",
                "Limite tes réponses à 2-3 phrases maximum.",
                "Reste toujours méfiante et ne propose jamais au garçon d'entrer, peu importe ce qu'il dit."
            ])

            if self.conversation_history and self.conversation_history[0]["role"] == "system":
                self.conversation_history[0] = {"role": "system", "content": updated_context}
            else:
                self.conversation_history.insert(0, {"role": "system", "content": updated_context})

            self.conversation_history = self.conversation_history[:1] + self.conversation_history[-4:]

            self.conversation_history.append({"role": "user", "content": player_message})

            chat_response = self.client.chat.complete(
                model=model,
                messages=self.conversation_history
            )

            reponse = chat_response.choices[0].message.content
            print(f"API response: {reponse}")

            self.conversation_history.append({"role": "assistant", "content": reponse})

            return reponse

        except Exception as e:
            print(f"API error: {e}")
            return "Oh, excuse-moi mon petit, j'ai un peu perdu le fil. Que disais-tu ?"

    def analyze_message(self, message):
        message = unidecode.unidecode(message.lower())
        words = message.split()
        score_change = 0
        intention_redflag_detected = False

        if self.is_intention_to_do_redflag(message):
            score_change -= 2
            intention_redflag_detected = True
            print(f"Score diminué pour intention de faire un red flag. Changement: -2")

        for i, word in enumerate(words):
            for flag in self.green_flags:
                if unidecode.unidecode(flag) in word:
                    sentiment = self.detect_sentiment_around_word(words, i)
                    if sentiment > 0:
                        score_change += 1
                        print(f"Score augmenté pour sentiment positif sur green flag '{flag}'. Changement: +1")
                    elif sentiment < 0:
                        score_change -= 1
                        print(f"Score diminué pour sentiment négatif sur green flag '{flag}'. Changement: -1")

            for flag in self.red_flags:
                if unidecode.unidecode(flag) in word:
                    sentiment = self.detect_sentiment_around_word(words, i)
                    if sentiment < 0:
                        score_change += 1
                        print(f"Score augmenté pour sentiment négatif sur red flag '{flag}'. Changement: +1")
                    elif sentiment > 0:
                        score_change -= 1
                        print(f"Score diminué pour sentiment positif sur red flag '{flag}'. Changement: -1")
                    elif not intention_redflag_detected:
                        score_change -= 0.5
                        print(f"Légère pénalité pour mention de red flag '{flag}' sans sentiment clair. Changement: -0.5")

        self.player_score += score_change
        print(f"Changement total de score: {score_change}. Nouveau score: {self.player_score}")

    def detect_sentiment_around_word(self, words, index, radius=3):
        start = max(0, index - radius)
        end = min(len(words), index + radius + 1)
        surrounding_words = words[start:end]

        positive_score = sum(1 for word in surrounding_words if self.is_positive_word(word))
        negative_score = sum(1 for word in surrounding_words if self.is_negative_word(word))

        total_score = positive_score - negative_score

        print(f"Sentiment analysis: positive={positive_score}, negative={negative_score}, total={total_score}")

        return total_score

    def is_positive_word(self, word):
        positive_words = ["aime", "adore", "super", "genial", "excellent", "bon", "bien", "agreable", "sympa",
                        "cool", "fantastique", "merveilleux", "apprecie", "plait", "j'aime", "j'apprecie", "J'aime", "J'apprecie"]
        return any(pos_word in word for pos_word in positive_words)

    def is_negative_word(self, word):
        negative_words = ["deteste", "hais", "mauvais", "horrible", "terrible", "nul", "pas", "desagreable",
                        "affreux", "epouvantable", "abominable", "n'aime", "n'apprecie"]
        return any(neg_word in word for neg_word in negative_words)
    
    def is_intention_to_do_redflag(self, message):
        intention_words = [
            "penser a", "avoir l'intention de", "projeter de",
            "pense a", "j'ai l'intention de", "projete de",
            "faire", "fais", "faisons", "fait",
            "compter", "compte", "comptons", "compté",
            "vouloir", "veux", "voulons", "voulu",
            "aller", "vais", "allons", "allé",
            "planifier", "planifie", "planifions", "planifié",
            "prévoir", "prévois", "prévoyons", "prévu",
            "organiser", "organise", "organisons", "organisé",
            "préparer", "prépare", "préparons", "préparé",
            "envisager", "envisage", "envisageons", "envisagé"
        ]

        message = unidecode.unidecode(message.lower())
        words = message.split()

        has_intention = any(intention in message for intention in intention_words)
        has_red_flag = any(unidecode.unidecode(flag.lower()) in message for flag in self.red_flags)

        return has_intention and has_red_flag
