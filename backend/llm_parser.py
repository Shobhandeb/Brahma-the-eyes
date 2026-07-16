import json
import requests
from typing import Dict, Any, Optional


class LLMRuleParser:
    def __init__(self, model_name: str = "qwen2.5:0.5b"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"

        # Supported YOLO COCO Classes
        self.valid_objects = {
            "person", "bicycle", "car", "motorcycle", "airplane",
            "bus", "train", "truck", "boat", "traffic light",
            "fire hydrant", "stop sign", "parking meter", "bench",
            "bird", "cat", "dog", "horse", "sheep", "cow",
            "elephant", "bear", "zebra", "giraffe", "backpack",
            "umbrella", "handbag", "tie", "suitcase", "frisbee",
            "skis", "snowboard", "sports ball", "kite",
            "baseball bat", "baseball glove", "skateboard",
            "surfboard", "tennis racket", "bottle",
            "wine glass", "cup", "fork", "knife", "spoon",
            "bowl", "banana", "apple", "sandwich", "orange",
            "broccoli", "carrot", "hot dog", "pizza",
            "donut", "cake", "chair", "couch",
            "potted plant", "bed", "dining table",
            "toilet", "tv", "laptop", "mouse",
            "remote", "keyboard", "cell phone",
            "microwave", "oven", "toaster", "sink",
            "refrigerator", "book", "clock", "vase",
            "scissors", "teddy bear", "hair drier",
            "toothbrush"
        }

        # Convert common words into YOLO labels
        self.synonyms = {
            "human": "person",
            "man": "person",
            "woman": "person",
            "boy": "person",
            "girl": "person",
            "employee": "person",
            "worker": "person",
            "people": "person",
            "mobile": "cell phone",
            "phone": "cell phone",
            "tv monitor": "tv",
            "sofa": "couch",
            "plant": "potted plant",
            "table": "dining table"
        }

    def parse_to_json(self, natural_language_input: str) -> Optional[Dict[str, Any]]:
        """
        Converts natural language into a structured JSON rule using a local Ollama LLM.
        """

        prompt = f"""
You are an AI Rule Compiler for a YOLOv8 Surveillance System.

Your ONLY job is to convert a user's request into ONE valid JSON object.

--------------------------------------------------
SUPPORTED OBJECTS
--------------------------------------------------

{", ".join(sorted(self.valid_objects))}

--------------------------------------------------
SUPPORTED CONDITIONS
--------------------------------------------------

exists
not exists
near
far
count
appears
disappears
inside zone
outside zone
duration

--------------------------------------------------
SYNONYMS
--------------------------------------------------

human -> person
man -> person
woman -> person
boy -> person
girl -> person
employee -> person
worker -> person
people -> person
phone -> cell phone
mobile -> cell phone
plant -> potted plant
table -> dining table
sofa -> couch

Always convert synonyms into supported object names.

--------------------------------------------------
RULES
--------------------------------------------------

1. Output ONLY JSON.

2. Never output markdown.

3. Never output explanations.

4. Never use ```.

5. Use lowercase object names.

6. object2 must be null when unused.

7. action is always "alert".

8. Distance defaults

near -> 250

far -> 500

everything else -> 0

9. If user specifies a distance,
use that value.

Example:

"person within 200 pixels of bottle"

distance = 200

10. If the request cannot be represented using the supported objects
or supported conditions, return

{{
    "error":"unsupported rule"
}}

--------------------------------------------------
JSON FORMAT
--------------------------------------------------

{{
    "object1":"string",
    "object2":"string or null",
    "condition":"exists | not exists | near | far | count | appears | disappears | inside zone | outside zone | duration",
    "distance":0,
    "action":"alert"
}}

--------------------------------------------------
EXAMPLES
--------------------------------------------------

Input:

Alert if a person is near a dog.

Output

{{
    "object1":"person",
    "object2":"dog",
    "condition":"near",
    "distance":250,
    "action":"alert"
}}

----------------------------

Input

Alert if a bottle appears.

Output

{{
    "object1":"bottle",
    "object2":null,
    "condition":"appears",
    "distance":250,
    "action":"alert"
}}

----------------------------

Input

Notify me if no person exists.

Output

{{
    "object1":"person",
    "object2":null,
    "condition":"not exists",
    "distance":0,
    "action":"alert"
}}

----------------------------

Input

Alert if a person comes within 250 pixels of a chair.

Output

{{
    "object1":"person",
    "object2":"chair",
    "condition":"near",
    "distance":250,
    "action":"alert"
}}

----------------------------

Input

Alert if a worker is close to a bottle.

Output

{{
    "object1":"person",
    "object2":"bottle",
    "condition":"near",
    "distance":250,
    "action":"alert"
}}

--------------------------------------------------
USER REQUEST
--------------------------------------------------

{natural_language_input}

--------------------------------------------------
RETURN ONLY JSON
--------------------------------------------------
"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=15
            )

            response.raise_for_status()

            result = response.json()

            json_string = result.get("response", "{}").strip()

            # Convert JSON string into Python dictionary
            rule_data = json.loads(json_string)

            # -------------------------------------------------
            # Check if the LLM rejected the rule
            # -------------------------------------------------

            if "error" in rule_data:
                print(f"[LLM] {rule_data['error']}")
                return None

            # -------------------------------------------------
            # Required fields
            # -------------------------------------------------

            required_fields = {
                "object1",
                "object2",
                "condition",
                "distance",
                "action"
            }

            missing = required_fields - rule_data.keys()

            if missing:
                print(f"[LLM ERROR] Missing fields: {missing}")
                return None

            # -------------------------------------------------
            # Normalize strings
            # -------------------------------------------------

            rule_data["object1"] = str(rule_data["object1"]).strip().lower()

            if rule_data["object2"] is not None:
                rule_data["object2"] = (
                    str(rule_data["object2"])
                    .strip()
                    .lower()
                )

            rule_data["condition"] = (
                str(rule_data["condition"])
                .strip()
                .lower()
            )

            rule_data["action"] = (
                str(rule_data["action"])
                .strip()
                .lower()
            )

            # -------------------------------------------------
            # Convert synonyms
            # -------------------------------------------------

            if rule_data["object1"] in self.synonyms:
                rule_data["object1"] = self.synonyms[rule_data["object1"]]

            if (
                rule_data["object2"] is not None and
                rule_data["object2"] in self.synonyms
            ):
                rule_data["object2"] = self.synonyms[rule_data["object2"]]

            # -------------------------------------------------
            # Validate supported objects
            # -------------------------------------------------

            if rule_data["object1"] not in self.valid_objects:
                print(
                    f"[LLM ERROR] Unsupported object: "
                    f"{rule_data['object1']}"
                )
                return None

            if (
                rule_data["object2"] is not None and
                rule_data["object2"] not in self.valid_objects
            ):
                print(
                    f"[LLM ERROR] Unsupported object: "
                    f"{rule_data['object2']}"
                )
                return None

            # -------------------------------------------------
            # Allowed conditions
            # -------------------------------------------------

            allowed_conditions = {
                "exists",
                "not exists",
                "near",
                "far",
                "count",
                "appears",
                "disappears",
                "inside zone",
                "outside zone",
                "duration"
            }

            if rule_data["condition"] not in allowed_conditions:
                print(
                    f"[LLM ERROR] Unsupported condition: "
                    f"{rule_data['condition']}"
                )
                return None

            # -------------------------------------------------
            # Distance validation
            # -------------------------------------------------

            try:
                distance = int(rule_data.get("distance", 0))
            except (ValueError, TypeError):
                distance = 0
            
            condition = rule_data["condition"]

            if condition == "near":
                if distance <= 0:
                    distance = 250

            elif condition == "far":
                if distance <=0:
                    distance = 500
            elif condition in ["exists", "not exists", "count", "appears", 
                               "disappears", "inside zone", "outside zone", "duration"]:
                distance =0
            else:
                distance = 0

            rule_data["distance"] = distance

            # -------------------------------------------------
            # Default values
            # -------------------------------------------------

            rule_data["enabled"] = True

            rule_data["action"] = "alert"

            return rule_data

        except requests.exceptions.ConnectionError:
            print("\n[LLM ERROR]")
            print("Cannot connect to Ollama.")
            print("Make sure Ollama is running.")
            print("Example:")
            print("    ollama serve")
            return None

        except requests.exceptions.Timeout:
            print("\n[LLM ERROR]")
            print("The request to Ollama timed out.")
            return None

        except json.JSONDecodeError:
            print("\n[LLM ERROR]")
            print("The model returned invalid JSON.")
            print("Try using a larger model like:")
            print("  qwen2.5:3b")
            print("  llama3.2:3b")
            print("  phi4-mini")
            return None

        except requests.exceptions.HTTPError as e:
            print(f"\n[HTTP ERROR] {e}")
            return None

        except Exception as e:
            print(f"\n[UNEXPECTED ERROR] {e}")
            return None


# ----------------------------------------------------------
# Local Testing
# ----------------------------------------------------------

if __name__ == "__main__":

    parser = LLMRuleParser(
        model_name="qwen2.5:0.5b"
    )

    test_cases = [
        "Alert if a person exists.",
        "Notify me if no person exists.",
        "Alert if a person is near a bottle.",
        "Alert if a worker is close to a chair.",
        "Alert if a person comes within 250 pixels of a dog.",
        "Notify me whenever a dog appears.",
        "Alert if a bottle disappears.",
        "Notify if a person is far from a chair.",
        "Count the number of people.",
        "Alert if a mobile phone is near a person.",
        "Alert if a human is close to a backpack.",
        "Alert if a unicorn is near a dragon.",
        "Alert if someone is smiling.",
        "Notify when a person is inside zone.",
        "Notify when a person is outside zone."
    ]

    print("=" * 70)
    print("LLM RULE PARSER TEST")
    print("=" * 70)

    for i, text in enumerate(test_cases, start=1):

        print("\n")
        print("-" * 70)
        print(f"Test #{i}")
        print("-" * 70)

        print("Input:")
        print(text)

        output = parser.parse_to_json(text)

        print("\nOutput:")

        if output is None:
            print("Rule rejected.")
        else:
            print(json.dumps(output, indent=4))

    print("\n")
    print("=" * 70)
    print("Testing Finished")
    print("=" * 70)