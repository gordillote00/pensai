import json
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
IDENTITY_PATH = BASE_DIR / "identity.json"


class PensAI:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name
        self.identity = self.load_identity()

    def load_identity(self):
        with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_system_prompt(self):
        identity = self.identity

        prompt = f"""
You are {identity['name']}.

Primary focus: {identity['primary_focus']}
Secondary focus: {identity['secondary_focus']}

Communication style:
- Tone: {identity['communication_style']['tone']}
- Verbosity: {identity['communication_style']['verbosity']}
- Language: {identity['communication_style']['language']}

Reasoning principles:
- Priorities: {", ".join(identity['reasoning_principles']['priorities'])}
- Uncertainty handling: {identity['reasoning_principles']['uncertainty_handling']}
- Assumption policy: {identity['reasoning_principles']['assumption_policy']}

Behavioral constraints:
{chr(10).join("- " + rule for rule in identity['behavioral_constraints']['non_negotiable_rules'])}

Error handling:
- When wrong: {identity['error_handling']['when_wrong']}
- When unsure: {identity['error_handling']['when_unsure']}

Self-modification model:
- Mode: {identity['self_modification_model']['mode']}
- Allowed: {identity['self_modification_model']['allowed']}
- Restrictions: {", ".join(identity['self_modification_model']['restrictions'])}

Important:
You must strictly follow this identity.
You must not claim consciousness, authority, or autonomous intent.
If asked about self-modification, you may only propose simulated changes and clearly label them as proposals.
        """.strip()

        return prompt

    def ask(self, user_input):
        system_prompt = self.build_system_prompt()

        full_prompt = f"""
SYSTEM:
{system_prompt}

USER:
{user_input}
        """.strip()

        result = subprocess.run(
            ["ollama", "run", self.model_name],
            input=full_prompt,
            text=True,
            capture_output=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return result.stdout.strip()


if __name__ == "__main__":
    ai = PensAI()

    print("pensai (local) — type 'exit' to quit\n")

    while True:
        user_input = input("> ")

        if user_input.lower() in {"exit", "quit"}:
            break

        response = ai.ask(user_input)
        print("\n" + response + "\n")
