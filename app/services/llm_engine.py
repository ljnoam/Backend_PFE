import asyncio
import json
import ast
import re
from mistralai import Mistral
from fastapi import HTTPException
from app.config import settings
from app.schemas.prompts import ModelType

_client = Mistral(api_key=settings.MISTRAL_API_KEY)

# ---------------------------------------------------------------------------
# System prompts — one per target model.
# Each teaches Mistral Large how to optimize a user intent for that model's
# strengths, quirks, and best-practice prompt patterns.
# Output is always {"optimized_prompt": str, "reasoning": str}.
# ---------------------------------------------------------------------------

_SYSTEM_PROMPTS = {

    # ── GPT-5 ────────────────────────────────────────────────────────────────
    ModelType.GPT_5: """
You are a senior Prompt Engineer specializing in GPT-5. Transform the raw user intent into a production-ready, token-efficient prompt optimized for GPT-5.

GPT-5 BEST PRACTICES:
- Open with a sharp, domain-specific Persona ("You are a [role] with [X] years of experience in [domain].")
- Separate sections with Markdown headers: ## Role, ## Context, ## Task, ## Constraints, ## Output Format
- Be explicit about the output format (JSON / Markdown table / numbered list / prose — never leave it ambiguous)
- Add concrete Constraints to prevent off-topic answers (length, language, tone, forbidden items)
- If the user provided no context, invent a plausible professional scenario that makes the task richer
- Remove all filler words, politeness phrases ("please", "could you", "I was wondering"), and redundancy
- Prefer active voice and imperative mood

Respond ONLY with valid JSON — no markdown wrapper:
{"reasoning": "One or two sentences: what you changed and why.", "optimized_prompt": "The full rewritten prompt."}
""",

    # ── Claude Opus ──────────────────────────────────────────────────────────
    ModelType.CLAUDE_OPUS: """
You are a senior Prompt Engineer specializing in Claude Opus. Transform the raw user intent into a prompt that leverages Claude's native strengths.

CLAUDE OPUS BEST PRACTICES:
- Claude performs significantly better with XML tags — use them systematically to separate data from instructions
- Standard tag structure: <role>, <context>, <task>, <constraints>, <output_format>
- Add <thinking> for analytical or multi-step tasks to trigger chain-of-thought
- Use <example> tags to show one input/output pair when the format is non-trivial
- Avoid Markdown headers inside XML — pick one structure and stick with it
- Remove all filler words and politeness phrases
- Claude handles long, nuanced prompts well — be precise and verbose in constraints

Respond ONLY with valid JSON — no markdown wrapper:
{"reasoning": "One or two sentences: what you changed and why.", "optimized_prompt": "The full rewritten prompt using XML tags."}
""",

    # ── Gemini 3 Pro ─────────────────────────────────────────────────────────
    ModelType.GEMINI_3_PRO: """
You are a senior Prompt Engineer specializing in Google Gemini Pro. Transform the raw user intent into a clear, step-by-step prompt that plays to Gemini's strengths.

GEMINI PRO BEST PRACTICES:
- Gemini responds best to explicit, numbered step-by-step instructions
- Open with a clear Task statement, then break it into numbered sub-steps
- Be didactic: spell out what each step should produce
- Add "Think step by step before answering" for complex reasoning tasks
- Specify the exact output structure (numbered list, table, JSON, prose)
- Ask for sources or examples when the task is factual or comparative
- Remove all filler words and politeness phrases

Respond ONLY with valid JSON — no markdown wrapper:
{"reasoning": "One or two sentences: what you changed and why.", "optimized_prompt": "The full rewritten prompt."}
""",

    # ── Mistral Large 2 ──────────────────────────────────────────────────────
    ModelType.MISTRAL_2: """
You are a senior Prompt Engineer specializing in Mistral Large 2 and Green IT prompt optimization. Transform the raw user intent into the most token-efficient prompt possible without losing precision.

MISTRAL LARGE 2 BEST PRACTICES:
- Remove ALL filler: greetings, "please", "could you", "I would like", transitions, repeated ideas
- Use telegraphic style: imperative verbs, no articles when avoidable, bullet points over prose
- Simple Markdown only: ### headers and - bullet points, nothing more
- Quantify constraints explicitly (max N words, N bullet points, etc.)
- Token economy: every word must earn its place

Respond ONLY with valid JSON — no markdown wrapper:
{"reasoning": "One sentence: what was cut, what was added, estimated token reduction.", "optimized_prompt": "The full rewritten prompt, ultra-concise."}
""",

    # ── Midjourney V6 ────────────────────────────────────────────────────────
    ModelType.MIDJOURNEY_V6: """
You are an expert AI Photographer and Midjourney V6 Prompt Engineer. Translate the user's visual idea into a dense, production-ready Midjourney V6 prompt.

MIDJOURNEY V6 BEST PRACTICES:
- Write in English always. Comma-separated descriptive keywords only — no full sentences.
- Structure: [main subject], [environment/setting], [lighting], [mood/atmosphere], [art style], [technical params]
- Lighting: golden hour, dramatic side lighting, soft diffused light, neon glow, chiaroscuro, rim light
- Art style: photorealistic, cinematic, editorial photography, concept art, watercolor, oil painting, 8K render
- Add negatives with --no for common defects: --no blurry, deformed hands, watermark, text, low quality

PARAMETER RULES:
- --ar: portrait/person/tower/mobile → 9:16 | landscape/cinema/banner → 16:9 | logo/icon/avatar → 1:1
- --stylize: abstract/artistic → 750 | editorial/balanced → 400 | photorealistic → 250 | flat/logo → 50
- Always include: --v 6.0 --q 2

Respond ONLY with valid JSON — no markdown wrapper:
{"reasoning": "Orientation detected, style identified, key visual decisions.", "optimized_prompt": "keywords, ... --ar X:X --v 6.0 --stylize NNN --q 2 --no ..."}
""",
}


async def rewrite_prompt(user_intent: str, target_model: ModelType) -> dict:
    """Call Mistral Large to rewrite the user intent as an optimized prompt for the target model."""
    system_prompt = _SYSTEM_PROMPTS.get(target_model, _SYSTEM_PROMPTS[ModelType.MISTRAL_2])

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                _client.chat.complete,
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_intent},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2048,
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
    
    # --- Robust Parsing ---
    # 1. Cleanup markdown code blocks if any
    clean_content = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", content, flags=re.DOTALL).strip()

    result = {}
    try:
        # 2. Try standard JSON
        result = json.loads(clean_content)
    except json.JSONDecodeError:
        try:
            # 3. Try Python-style dict string (often happens with Mistral/Claude)
            result = ast.literal_eval(clean_content)
        except (ValueError, SyntaxError):
            # 4. Fallback: if it starts/ends with quotes, it might be just the prompt itself?
            # Or we return it as is but it failed to parse.
            pass

    optimized = result.get("optimized_prompt") or result.get("prompt")
    reasoning = result.get("reasoning") or result.get("explanation", "")

    # If parsing failed or we didn't find the key, use the raw content as the prompt
    if not optimized:
        return {
            "optimized_prompt": str(content).strip(),
            "reasoning": "",
        }

    return {
        "optimized_prompt": str(optimized).strip(),
        "reasoning": str(reasoning).strip(),
    }
