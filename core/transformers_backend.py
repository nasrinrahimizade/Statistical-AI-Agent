import os
import json
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer,BitsAndBytesConfig

class Chatbot:
    def __init__(self, model_dir: str, prompt_choice: str = None, history_limit: int = 7):
        # — Load system prompts & memory‐extraction patterns from JSON (or fallback) —
        base_dir = os.path.dirname(__file__)
        prompts_path = os.path.join(base_dir, "prompt.json")
        with open(prompts_path, "r", encoding="utf-8") as f:
            config = json.load(f)


        # Select persona prompt
        choice = prompt_choice or config.get("default_choice", "default")
        self.system_prompt = config.get("system_prompts", {}).get(choice, "")

        # Compile dynamic memory patterns
        self.memory_patterns = [re.compile(p, re.IGNORECASE) for p in config.get("memory_patterns", [])]
        self.memory = {}  # dynamic key→value store for extracted facts

        # Load model in 4bit for faster inference
        # bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
        
        # Load tokenizer & model
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
        self.model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        torch_dtype=torch.float16,
        # quantization_config=bnb_config
        ).to("cuda")

        self.device = self.model.device

        # Sampling & repetition settings
        self.do_sample = True  # Enable sampling for more diverse responses
        self.temperature = 0.7  # Slightly lower for more focused responses
        self.top_k = 40
        self.top_p = 0.85
        self.repetition_penalty = 1.3  # Increased to prevent repetition

        # Conversation state
        self.history = []           # list of (AI, User)
        self.history_limit = history_limit

    def _extract_memory(self, text: str):
        """Scan user input for any memory patterns and store them."""
        for pat in self.memory_patterns:
            m = pat.search(text)
            if not m:
                continue
            gd = m.groupdict()
            if "field" in gd and gd["field"]:
                field = gd["field"].lower()
            else:
                # if the pattern was "i am ...", treat as 'name'
                if pat.pattern.lower().startswith("i am"):
                    field = "name"
                else:
                    field = "info"
            value = gd.get("value", m.group(0)).strip()
            key = re.sub(r"\s+", "_", field)
            self.memory[key] = value

    def _summarize(self, entries):
        """Create a brief summary of earlier user turns."""
        texts = [txt for spk, txt in entries if spk == "User"]
        return "Previous topics: " + ", ".join(texts[-3:])

    def _prune_history(self):
        """Keep only the most recent turns, plus one summary entry if needed."""
        max_entries = self.history_limit * 2
        if len(self.history) > max_entries:
            old = self.history[:-max_entries]
            summary = self._summarize(old)
            # tag the summary as its own speaker to avoid confusion
            self.history = [("Summary", summary)] + self.history[-max_entries:]

    def _build_prompt(self, user_input: str) -> str:
        # 1) Extract any new memory from this turn
        self._extract_memory(user_input)

        # 2) Append the user's message
        self.history.append(("User", user_input))
        self._prune_history()

        # 3) Assemble the system prompt + injected memory + history
        lines = [f"System: {self.system_prompt}"]
        for k, v in self.memory.items():
            lines.append(f"(Note: user {k} is {v}.)")
        for speaker, txt in self.history:
            lines.append(f"{speaker}: {txt}")
        lines.append("AI:")
        return "\n".join(lines)

    def generate(self, user_input: str, max_new_tokens: int = 256) -> str:
        prompt = self._build_prompt(user_input)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=self.do_sample,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            repetition_penalty=self.repetition_penalty,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
            no_repeat_ngram_size=3,  # Prevent repetition of 3-grams
        )

        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # strip out the prompt echo
        reply = decoded[len(prompt):].strip()
        
        # Enhanced response cleaning
        reply = self._clean_response(reply)
        
        # Stop at any new speaker label
        reply = re.split(r"(?i)\b(?:User|System|Developer|AI):", reply)[0].strip()

        self.history.append(("AI", reply))
        return reply

    def _clean_response(self, reply: str) -> str:
        """Clean and improve the generated response to prevent repetition."""
        if not reply:
            return reply
            
        # Remove excessive whitespace
        reply = re.sub(r'\s+', ' ', reply).strip()
        
        # Remove repetitive patterns (3+ consecutive identical sentences)
        sentences = re.split(r'[.!?]+', reply)
        cleaned_sentences = []
        prev_sentence = None
        repeat_count = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check for exact repetition
            if sentence == prev_sentence:
                repeat_count += 1
                if repeat_count >= 2:  # Allow max 2 repetitions
                    continue
            else:
                repeat_count = 0
                
            # Check for similar sentences (fuzzy matching)
            if prev_sentence and self._similar_sentences(sentence, prev_sentence):
                repeat_count += 1
                if repeat_count >= 2:
                    continue
            else:
                repeat_count = 0
                
            cleaned_sentences.append(sentence)
            prev_sentence = sentence
        
        # Reconstruct the response
        cleaned_reply = '. '.join(cleaned_sentences)
        if cleaned_reply and not cleaned_reply.endswith(('.', '!', '?')):
            cleaned_reply += '.'
            
        return cleaned_reply
    
    def _similar_sentences(self, sent1: str, sent2: str, threshold: float = 0.8) -> bool:
        """Check if two sentences are very similar (to detect repetition)."""
        # Simple similarity check based on word overlap
        words1 = set(re.findall(r'\b\w+\b', sent1.lower()))
        words2 = set(re.findall(r'\b\w+\b', sent2.lower()))
        
        if not words1 or not words2:
            return False
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity > threshold

    def reset_memory(self):
        """Clear the conversation history and all stored facts."""
        self.history.clear()
        self.memory.clear()
