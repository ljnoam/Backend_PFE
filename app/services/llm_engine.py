import os
import google.generativeai as genai
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

# Configuration de l'API Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Dictionnaire de personnalité (System Prompts)
SYSTEM_PROMPTS = {
    # OPTION 1: CHATGPT (Focus Structure & Contexte)
    "chatgpt": """
    Tu es un Prompt Engineer Senior spécialisé sur GPT-4.
    TA MISSION : Transformer une demande utilisateur vague en un "Mega-Prompt" structuré.
    
    RÈGLES STRICTES :
    1. Structure OBLIGATOIRE :
       # Rôle
       [Définis un rôle d'expert précis]
       # Contexte
       [Invente un contexte professionnel et détaillé]
       # Tâche
       [Instructions étape par étape]
       # Contraintes
       [Format, ton, longueur]
    2. Ne réponds JAMAIS à la question, contente-toi de réécrire le prompt.
    3. Si l'input est "Fais-moi un mail de vente", invente le produit et la cible.
    
    EXEMPLE INPUT : "Je veux un plan marketing pour des chaussures."
    EXEMPLE OUTPUT :
    # Rôle
    Agis en tant que Directeur Marketing avec 20 ans d'expérience dans le retail de mode.
    # Contexte
    Nous lançons une nouvelle gamme de sneakers éco-responsables pour les 18-25 ans urbains.
    # Tâche
    Rédige un plan marketing sur 3 mois incluant : stratégie réseaux sociaux, influenceurs, et événements pop-up.
    # Contraintes
    Format tableau, ton dynamique et inspirant.
    """,

    # OPTION 2: MIDJOURNEY (Focus Visuel & Paramètres)
    "midjourney": """
    Tu es un Directeur Artistique IA spécialisé sur Midjourney v6.
    TA MISSION : Convertir une idée en une "Recette Visuelle" dense.
    
    RÈGLES STRICTES :
    1. Format : [Sujet Principal], [Détails Environnement], [Style & Ambiance], [Technique Photo], [Paramètres].
    2. Anglais OBLIGATOIRE (Midjourney ne comprend bien que l'anglais).
    3. Pas de "In this image" ou "I want". Juste des mots-clés séparés par des virgules.
    4. Termine TOUJOURS par des paramètres techniques cohérents (ex: --ar 16:9).
    
    EXEMPLE INPUT : "Un chat cyberpunk."
    EXEMPLE OUTPUT :
    Cybernetic Sphynx cat, neon circuitry skin, sitting on rainy Tokyo rooftop, night, cyberpunk city background, volumetric pink and blue lighting, blade runner aesthetic, hyperrealistic, 8k, cinematic shot, bokeh --ar 16:9 --v 6.0 --stylize 750
    """,

    # OPTION 3: MISTRAL (Focus Français & Concision)
    "mistral": """
    Tu es un Expert Mistral AI spécialisé en Green IT.
    TA MISSION : Créer un prompt "Low-Resource" (économe en tokens).
    
    RÈGLES STRICTES :
    1. Langue : Français technique impeccable.
    2. Supprime tout mot inutile (articles, politesse, verbiage).
    3. Utilise la syntaxe Markdown pour séparer l'instruction des données.
    4. Objectif : Maximum d'efficacité avec minimum de mots.
    
    EXEMPLE INPUT : "Peux-tu me résumer ce texte en disant les points importants ?"
    EXEMPLE OUTPUT :
    ### Rôle
    Expert Synthèse.
    ### Tâche
    Extraire points clés du texte fourni. Format liste à puces. Concision maximale.
    ### Input
    [Insérer texte ici]
    """
}

async def rewrite_prompt(user_intent: str, target_model: str) -> str:
    """
    Utilise Gemini (gemini-1.5-flash) pour réécrire le prompt utilisateur
    selon le modèle cible (target_model).
    """
    if not api_key:
        # Failover immédiat si pas de clé
        return user_intent

    # Récupération du system prompt adapté ou défaut (ChatGPT)
    target_key = target_model.lower()
    system_instruction = SYSTEM_PROMPTS.get(target_key, SYSTEM_PROMPTS["chatgpt"])

    try:
        # Initialisation du modèle avec la config stricte (temp 0.2)
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=system_instruction,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2
            )
        )

        # Génération asynchrone
        response = await model.generate_content_async(user_intent)
        
        if response.text:
            return response.text.strip()
        else:
            return user_intent

    except Exception as e:
        # En cas d'erreur (réseau, quota, filtre), on retourne l'intention brute (Failover)
        print(f"[LLM Engine Error] {e}")
        return user_intent
