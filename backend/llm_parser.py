import json
import requests
import re
from typing import Dict, Any, Optional

class LLMRuleParser:
    # Reverted back to the ultra-fast 0.5B model
    def __init__(self, model_name: str = "qwen2.5:0.5b"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"

        # The strict list of objects the backend supports
        self.valid_objects = {
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
            "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
            "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
            "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
            "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
            "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
            "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
            "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
            "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
            "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
        }

        self.allowed_conditions = {
            "exists", "not exists", "near", "far", "count", 
            "appears", "disappears", "inside zone", "outside zone"
        }

    def is_negative_request(self, text: str) -> bool:
        """
        Since 0.5B models struggle with negation logic, we intercept "don't" 
        or "stop" requests in Python to prevent hallucinations.
        """
        text_lower = text.lower()
        negations = ["do not", "don't", "stop", "never", "disable", "pause", "halt"]
        return any(text_lower.startswith(neg) for neg in negations)

    def _build_prompt(self, user_input: str) -> str:
        """
        Ultra-lean Few-Shot Prompt for 0.5B.
        We teach it dynamic intelligence by showing it an example of mapping 
        'guard' -> 'person', 'mobile' -> 'cell phone', and 'touches' -> 'near'.
        """
        return f"""Extract the surveillance rule into a strict JSON object.

ALLOWED OBJECTS: {", ".join(sorted(self.valid_objects))}
ALLOWED CONDITIONS: exists, not exists, near, far, count, appears, disappears, inside zone, outside zone

INTELLIGENCE RULES:
1. Map conversational words to the closest ALLOWED OBJECT (e.g. thief->person).
2. Map actions to the closest ALLOWED CONDITION (e.g. touches/holds->near, vanishes->disappears).
3. Distance is 250 by default unless pixels are mentioned.
4. Output ONLY valid JSON. No explanations.

Text: Alert if a guard touches a mobile.
JSON: {{"object1": "person", "object2": "cell phone", "condition": "near", "distance": 250, "action": "alert"}}

Text: {user_input}
JSON:"""

    def parse_to_json(self, natural_language_input: str) -> Optional[Dict[str, Any]]:
        # 1. Fast-fail negative instructions
        if self.is_negative_request(natural_language_input):
            print("[PYTHON REJECTED] Negative rule instruction detected.")
            return None

        payload = {
            "model": self.model_name,
            "prompt": self._build_prompt(natural_language_input),
            "stream": False,
            "format": "json"
        }
        
        try:
            # 15 second timeout is usually plenty for 0.5B
            response = requests.post(self.api_url, json=payload, timeout=15)
            response.raise_for_status()
            
            raw_response = response.json().get("response", "{}").strip()
            
            # 2. Aggressive JSON Extraction (Saves the output if the tiny model adds conversational text)
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not json_match:
                print(f"[ERROR] LLM failed to generate JSON. Output: {raw_response}")
                return None
                
            rule_data = json.loads(json_match.group(0))

            # 3. Schema Enforcement
            rule_data.setdefault("object1", "")
            rule_data.setdefault("object2", None)
            rule_data.setdefault("condition", "")
            rule_data.setdefault("distance", 250)
            rule_data["action"] = "alert"

            # Normalize values
            obj1 = str(rule_data["object1"]).strip().lower()
            obj2 = str(rule_data["object2"]).strip().lower() if rule_data.get("object2") else None
            cond = str(rule_data["condition"]).strip().lower()

            # 4. Strict Validation (Reject if the 0.5B model hallucinates)
            if obj1 not in self.valid_objects:
                print(f"[VALIDATION ERROR] Model selected unsupported object1: '{obj1}'")
                return None
            if obj2 is not None and obj2 not in self.valid_objects:
                print(f"[VALIDATION ERROR] Model selected unsupported object2: '{obj2}'")
                return None
            if cond not in self.allowed_conditions:
                print(f"[VALIDATION ERROR] Model selected unsupported condition: '{cond}'")
                return None

            # 5. Apply Distance Rules
            try:
                distance = int(rule_data["distance"])
                if distance <= 0:
                    distance = 250
            except (ValueError, TypeError):
                distance = 250
            
            rule_data["distance"] = distance
            rule_data["object1"] = obj1
            rule_data["object2"] = obj2
            rule_data["condition"] = cond

            return rule_data

        except requests.exceptions.ConnectionError:
            print(f"\n[ERROR] Cannot connect to Ollama. Make sure 'ollama run {self.model_name}' is active.")
            return None
        except Exception as e:
            print(f"\n[UNEXPECTED ERROR] {e}")
            return None
