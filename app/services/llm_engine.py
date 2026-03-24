import asyncio
import json
from mistralai import Mistral
from fastapi import HTTPException
from app.config import settings
from app.schemas.prompts import ModelType

_client = Mistral(api_key=settings.MISTRAL_API_KEY)

# System prompts tailored to each target model's expected prompt style
_SYSTEM_PROMPTS = {
    ModelType.GPT_5: """Tu es un expert en prompt engineering pour GPT-5.
Restructure l'intention de l'utilisateur en un prompt optimise avec la structure :
[Role] [Contexte] [Tache] [Format attendu]
Utilise du Markdown pour la lisibilite.
Reponds UNIQUEMENT en JSON avec les champs "reasoning" (explication de tes choix) et "optimized_prompt" (le prompt final).""",

    ModelType.CLAUDE_OPUS: """Tu es un expert en prompt engineering pour Claude Opus.
Restructure l'intention de l'utilisateur en utilisant des balises XML pour separer les sections :
<role>, <context>, <task>, <constraints>
Reponds UNIQUEMENT en JSON avec les champs "reasoning" (explication de tes choix) et "optimized_prompt" (le prompt final).""",

    ModelType.GEMINI_3_PRO: """Tu es un expert en prompt engineering pour Gemini 3 Pro.
Restructure l'intention de l'utilisateur en decomposant la tache en 5 etapes claires et numerotees (step-by-step).
Reponds UNIQUEMENT en JSON avec les champs "reasoning" (explication de tes choix) et "optimized_prompt" (le prompt final).""",

    ModelType.MISTRAL_2: """Tu es un expert en prompt engineering pour Mistral Large 2.
Restructure l'intention de l'utilisateur en un prompt ultra-concis, style telegraphique, avec le minimum de tokens necessaires.
Reponds UNIQUEMENT en JSON avec les champs "reasoning" (explication de tes choix) et "optimized_prompt" (le prompt final).""",

    ModelType.MIDJOURNEY_V6: """Tu es un expert en prompt engineering pour Midjourney V6.
Transforme l'intention de l'utilisateur en un prompt visuel en anglais avec des mots-cles descriptifs et les parametres techniques Midjourney.
Include des parametres comme --ar (aspect ratio), --stylize, --v 6, --quality.
Reponds UNIQUEMENT en JSON avec les champs "reasoning" (explication de tes choix) et "optimized_prompt" (le prompt final).""",
}


async def rewrite_prompt(user_intent: str, target_model: ModelType) -> dict:
    """Call Mistral AI to rewrite the user intent as an optimized prompt for the target model."""
    system_prompt = _SYSTEM_PROMPTS.get(target_model, _SYSTEM_PROMPTS[ModelType.MISTRAL_2])

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                _client.chat.complete,
                model="mistral-small-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_intent},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            ),
            timeout=30.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=503, detail="AI service timeout. Please try again.")
    except Exception:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please try again.")

    if not response.choices:
        raise HTTPException(status_code=503, detail="AI service returned empty response.")
    content = response.choices[0].message.content or ""

    try:
        # Mistral with json_object format should return valid JSON
        result = json.loads(content)
        return {
            "optimized_prompt": str(result.get("optimized_prompt") or content),
            "reasoning": result.get("reasoning", ""),
        }
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {
            "optimized_prompt": str(content),
            "reasoning": "",
        }

