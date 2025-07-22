from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import torch

class Chatbot:
    def __init__(self, model_dir: str, system_prompt: str = None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=False)
        self.model     = AutoModelForCausalLM.from_pretrained(model_dir).to(
            torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        # load your tuned generation_config.json
        self.gen_config = GenerationConfig.from_pretrained(model_dir)
        self.device     = self.model.device

        # Memory
        self.system_prompt = system_prompt or "You are a helpful assistant."
        self.history = []  # list of ("User", text) and ("AI", text)

    def _build_prompt(self, user_input: str) -> str:
        self.history.append(("User", user_input))
        lines = [f"System: {self.system_prompt}"] + [
            f"{speaker}: {txt}" for speaker, txt in self.history
        ] + ["AI:"]
        return "\n".join(lines)

    def generate(self, user_input: str, max_new_tokens: int = 256) -> str:
        prompt = self._build_prompt(user_input)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            generation_config=self.gen_config,
            max_new_tokens=max_new_tokens,
        )

        full = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # strip off the echoed prompt
        reply = full[len(prompt) :].lstrip()

        # **important**: if the model continues with "User:" or another turn, cut it off
        if "User:" in reply:
            reply = reply.split("User:")[0].rstrip()

        # record and return
        self.history.append(("AI", reply))
        return reply

    def reset_memory(self):
        self.history.clear()
