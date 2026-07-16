import json
import os
from typing import List, Optional
from backend.models import Rule
from backend.llm_parser import LLMRuleParser

class RuleManager:
    def __init__(self, rules_file: str = "rules/rules.json"):
        self.rules_file = rules_file
        self.llm_parser = LLMRuleParser()
        
        # Ensure the rules directory and file exist on startup
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        if not os.path.exists(self.rules_file):
            with open(self.rules_file, "w") as f:
                json.dump([], f)

    def get_rules(self) -> List[Rule]:
        """Reads rules from JSON and parses them into strict Pydantic objects."""
        try:
            with open(self.rules_file, "r") as f:
                data = json.load(f)
                return [Rule(**rule) for rule in data]
        except Exception as e:
            print(f"[RuleManager Error] Failed to load rules: {e}")
            return []

    def save_rules(self, rules: List[Rule]):
        """Converts Pydantic objects back to JSON and saves them."""
        with open(self.rules_file, "w") as f:
            json.dump([rule.model_dump() for rule in rules], f, indent=4)

    def add_rule(self, rule: Rule) -> Rule:
        """Assigns a new ID and appends the rule to the database."""
        rules = self.get_rules()
        # Auto-increment ID safely
        rule.id = max([r.id for r in rules], default=0) + 1
        rules.append(rule)
        self.save_rules(rules)
        return rule

    def update_rule(self, rule_id: int, updated_rule: Rule) -> Optional[Rule]:
        """Finds an existing rule and overwrites it."""
        rules = self.get_rules()
        for i, r in enumerate(rules):
            if r.id == rule_id:
                updated_rule.id = rule_id  # Prevent accidental ID reassignment
                rules[i] = updated_rule
                self.save_rules(rules)
                return updated_rule
        return None

    def delete_rule(self, rule_id: int) -> bool:
        """Removes a rule by ID. Returns True if successful."""
        rules = self.get_rules()
        filtered = [r for r in rules if r.id != rule_id]
        if len(rules) == len(filtered):
            return False  # Rule ID wasn't found
        self.save_rules(filtered)
        return True

    def generate_rule_from_text(self, natural_language_text: str) -> Optional[Rule]:
        """
        The Master NLP Pipeline:
        1. Passes text to LLM.
        2. Retrieves JSON.
        3. Validates it through Pydantic.
        4. Saves it to the database.
        """
        parsed_data = self.llm_parser.parse_to_json(natural_language_text)
        
        if not parsed_data:
            print("[RuleManager Error] LLM failed to return data.")
            return None
        
        try:
            # We must assign a temporary ID of 0 so Pydantic doesn't crash during validation.
            # add_rule() will overwrite this with the real ID.
            parsed_data["id"] = 0
            
            # This is where Pydantic checks if distance is an int, condition is a string, etc.
            new_rule = Rule(**parsed_data)
            
            # Save it to the JSON file
            return self.add_rule(new_rule)
            
        except Exception as e:
            print(f"[RuleManager Error] Generated JSON failed Pydantic validation: {e}")
            print(f"Raw data from LLM: {parsed_data}")
            return None

# --- Quick Local Testing ---
if __name__ == "__main__":
    manager = RuleManager()
    
    print("1. Testing LLM Integration...")
    test_text = "Please alert me if a person exists in the camera frame."
    new_ai_rule = manager.generate_rule_from_text(test_text)
    
    if new_ai_rule:
        print(f"\nSUCCESS! Rule saved with ID #{new_ai_rule.id}")
        print(f"Rule Details: {new_ai_rule.model_dump()}")
    else:
        print("\nFAILURE. Rule was not created.")
        
    print("\n2. Checking rules.json contents...")
    all_rules = manager.get_rules()
    for r in all_rules:
        print(f" - [{r.id}] {r.object1} {r.condition} {r.object2 or ''}")