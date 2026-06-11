from api_client import APIClient
from owlready2 import *
import os
import json
import types
from datetime import datetime
import re

class OntologyBuilder:
    def __init__(self, client=None):
        self.client = client or APIClient()
        self.data_dir = "./data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.ontology_name = None
        self.current_ontology = None
        self.file_path = None
        self.initial_request = None
        self.request_history = []
        
    def get_ontology_name(self, user_input):
        """Generate ontology name from first user input"""
        response = self.client.generate_response(
            f"""Based on this ontology request, generate a short, descriptive name for the ontology file.
            Return ONLY the name in lowercase, using underscores for spaces, ending in '_ontology'.
            Example: 'library_system_ontology' or 'pet_care_ontology'
            Request: {user_input}"""
        )
        name = response.strip().lower()
        name = re.sub(r'[^a-z0-9_]', '', name)
        if not name.endswith('_ontology'):
            name += '_ontology'
        return name

    def initialize_ontology(self, user_input):
        """Initialize a new ontology with a generated name"""
        self.ontology_name = self.get_ontology_name(user_input)
        self.file_path = os.path.join(self.data_dir, f"{self.ontology_name}.owl")
        
        # Create new ontology
        base_iri = f"http://test.org/{self.ontology_name}"
        self.current_ontology = get_ontology(base_iri)
        self.initial_request = user_input.strip()
        self.request_history = []
        print(f"\nCreated new ontology: {self.ontology_name}")
        return True

    def execute_ontology_changes(self, response_text, user_message=None):
        """Execute ontology changes based on LLM response"""
        try:
            print("\nAI suggested changes:")
            print(response_text)
            changes = self.parse_changes_response(response_text)
            if self.changes_are_empty(changes):
                print("\nAI did not suggest any ontology changes.")
                return False
            self.validate_changes(changes, user_message)
            
            print("\nMaking changes to ontology...")
            with self.current_ontology:
                # Create classes
                print("\nCreating classes:")
                for class_name in changes["classes_to_add"]:
                    try:
                        existing_class = self.current_ontology[class_name]
                        if existing_class:
                            print(f"✓ Class already exists: {class_name}")
                        else:
                            types.new_class(class_name, (Thing,))
                            print(f"✓ Created class: {class_name}")
                    except Exception as e:
                        print(f"✗ Error creating class {class_name}: {str(e)}")

                # Create object properties
                print("\nCreating object properties:")
                for prop in changes["object_properties"]:
                    try:
                        prop_name = prop["name"]
                        NewProperty = self.current_ontology[prop_name]
                        if not NewProperty:
                            NewProperty = types.new_class(prop_name, (ObjectProperty,))
                        domain_class = self.current_ontology[prop["domain"]]
                        range_class = self.current_ontology[prop["range"]]
                        self.append_unique(NewProperty.domain, domain_class)
                        self.append_unique(NewProperty.range, range_class)
                        print(f"✓ Created object property: {prop_name} (domain: {prop['domain']}, range: {prop['range']})")
                    except Exception as e:
                        print(f"✗ Error creating object property {prop.get('name', 'unknown')}: {str(e)}")

                # Create data properties
                print("\nCreating data properties:")
                for prop in changes["data_properties"]:
                    try:
                        prop_name = prop["name"]
                        NewProperty = self.current_ontology[prop_name]
                        if not NewProperty:
                            NewProperty = types.new_class(prop_name, (DataProperty,))
                        domain_class = self.current_ontology[prop["domain"]]
                        self.append_unique(NewProperty.domain, domain_class)
                        type_map = {
                            "str": str,
                            "float": float,
                            "int": int,
                            "datetime": datetime,
                            "bool": bool
                        }
                        self.append_unique(NewProperty.range, type_map.get(prop["type"], str))
                        print(f"✓ Created data property: {prop_name} (domain: {prop['domain']}, type: {prop['type']})")
                    except Exception as e:
                        print(f"✗ Error creating data property {prop.get('name', 'unknown')}: {str(e)}")

                print("\nAll changes completed successfully!")
                return True
                
        except json.JSONDecodeError as e:
            print(f"\nError parsing ontology changes: {e}")
            print("Response text:", response_text)
            return False
        except ValueError as e:
            print(f"\nError validating ontology changes: {e}")
            print("Response text:", response_text)
            return False
        except Exception as e:
            print(f"\nError executing changes: {e}")
            return False

    def append_unique(self, values, item):
        if item not in values:
            values.append(item)

    def parse_changes_response(self, response_text):
        """Parse the model's ontology-change JSON, accepting Markdown fenced output."""
        text = response_text.strip()
        fenced_match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if fenced_match:
            text = fenced_match.group(1).strip()

        try:
            changes = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise
            changes = json.loads(text[start:end + 1])

        required_keys = ("classes_to_add", "object_properties", "data_properties")
        for key in required_keys:
            if key not in changes:
                changes[key] = []
            if not isinstance(changes[key], list):
                raise ValueError(f"Expected '{key}' to be a list")
        return changes

    def changes_are_empty(self, changes):
        return not (
            changes["classes_to_add"]
            or changes["object_properties"]
            or changes["data_properties"]
        )

    def validate_changes(self, changes, user_message=None):
        self.validate_change_shape(changes)
        self.validate_class_references(changes)
        self.validate_followup_relevance(changes, user_message)

    def validate_change_shape(self, changes):
        valid_type_names = {"str", "float", "int", "datetime", "bool"}

        for class_name in changes["classes_to_add"]:
            self.validate_symbol(class_name, "class")

        for prop in changes["object_properties"]:
            self.validate_property_shape(prop, ("name", "domain", "range"), "object property")
            self.validate_symbol(prop["name"], "object property")
            self.validate_symbol(prop["domain"], "object property domain")
            self.validate_symbol(prop["range"], "object property range")

        for prop in changes["data_properties"]:
            self.validate_property_shape(prop, ("name", "domain", "type"), "data property")
            self.validate_symbol(prop["name"], "data property")
            self.validate_symbol(prop["domain"], "data property domain")
            if prop["type"] not in valid_type_names:
                raise ValueError(
                    f"Unsupported data property type '{prop['type']}'. "
                    f"Use one of: {', '.join(sorted(valid_type_names))}"
                )

    def validate_property_shape(self, prop, required_keys, label):
        if not isinstance(prop, dict):
            raise ValueError(f"Expected each {label} to be an object")
        for key in required_keys:
            if key not in prop:
                raise ValueError(f"Expected each {label} to include '{key}'")
            if not isinstance(prop[key], str) or not prop[key].strip():
                raise ValueError(f"Expected {label} '{key}' to be a non-empty string")

    def validate_symbol(self, value, label):
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError(
                f"Invalid {label} name '{value}'. Use letters, numbers, and underscores, "
                "starting with a letter or underscore."
            )

    def validate_class_references(self, changes):
        existing_classes = {cls.name for cls in self.current_ontology.classes()}
        added_classes = set(changes["classes_to_add"])
        known_classes = existing_classes | added_classes
        missing_classes = set()

        for prop in changes["object_properties"]:
            for key in ("domain", "range"):
                if prop[key] not in known_classes:
                    missing_classes.add(prop[key])

        for prop in changes["data_properties"]:
            if prop["domain"] not in known_classes:
                missing_classes.add(prop["domain"])

        if missing_classes:
            raise ValueError(
                "AI response references classes that do not exist and were not added: "
                + ", ".join(sorted(missing_classes))
            )

    def validate_followup_relevance(self, changes, user_message=None):
        if not self.request_history:
            return

        added_classes = set(changes["classes_to_add"])
        generic_demo_classes = {"Person", "Organization", "Event", "Location", "Product"}
        generic_demo_properties = {
            "attends",
            "employs",
            "locatedAt",
            "produces",
            "sells",
            "participatesIn",
            "hosts",
        }
        requested_text = f"{self.initial_request or ''} {user_message or ''}".lower()
        allowed_generic_terms = {
            "person",
            "people",
            "organization",
            "company",
            "event",
            "location",
            "place",
            "product",
        }
        requested_generic_terms = any(term in requested_text for term in allowed_generic_terms)
        added_generic_properties = {prop["name"] for prop in changes["object_properties"]} & generic_demo_properties

        if generic_demo_classes.issubset(added_classes) and not requested_generic_terms:
            raise ValueError(
                "AI response appears to switch to a generic person/organization/product ontology "
                "instead of expanding the current ontology topic."
            )

        if len(added_generic_properties) >= 4 and not requested_generic_terms:
            raise ValueError(
                "AI response appears to add unrelated generic demo relationships instead of "
                "expanding the current ontology topic."
            )

        if self.is_vague_followup(user_message):
            existing_classes = {cls.name for cls in self.current_ontology.classes()}
            referenced_classes = set()
            for prop in changes["object_properties"]:
                referenced_classes.add(prop["domain"])
                referenced_classes.add(prop["range"])
            for prop in changes["data_properties"]:
                referenced_classes.add(prop["domain"])

            if existing_classes and not (referenced_classes & existing_classes):
                raise ValueError(
                    "Vague follow-up response did not connect any new properties to existing "
                    "ontology classes. Ask again with a more specific change, or retry."
                )

    def is_vague_followup(self, user_message):
        if not user_message:
            return False
        normalized = user_message.lower()
        vague_markers = (
            "more detail",
            "more detailed",
            "much more",
            "expand",
            "elaborate",
            "improve",
            "flesh out",
        )
        return any(marker in normalized for marker in vague_markers)

    def entity_name(self, entity):
        if isinstance(entity, type):
            return entity.__name__
        if hasattr(entity, "name"):
            return entity.name
        return str(entity)

    def entity_list(self, entities):
        names = [self.entity_name(entity) for entity in entities]
        return ", ".join(names) if names else "unspecified"

    def describe_current_ontology(self):
        if not self.current_ontology:
            return "No ontology has been initialized yet."

        classes = sorted(cls.name for cls in self.current_ontology.classes())
        object_properties = []
        data_properties = []

        for prop in self.current_ontology.object_properties():
            object_properties.append(
                f"{prop.name}: {self.entity_list(prop.domain)} -> {self.entity_list(prop.range)}"
            )

        for prop in self.current_ontology.data_properties():
            data_properties.append(
                f"{prop.name}: {self.entity_list(prop.domain)} -> {self.entity_list(prop.range)}"
            )

        return "\n".join([
            "Classes: " + (", ".join(classes) if classes else "none"),
            "Object properties: " + ("; ".join(sorted(object_properties)) if object_properties else "none"),
            "Data properties: " + ("; ".join(sorted(data_properties)) if data_properties else "none"),
        ])

    def build_change_prompt(self, user_message):
        history = "\n".join(f"- {request}" for request in self.request_history) or "- None yet"
        ontology_topic = self.initial_request or user_message

        return f"""You are editing one existing ontology. Do not start a new unrelated example ontology.

Ontology purpose:
{ontology_topic}

Previous successful user requests:
{history}

Current ontology summary:
{self.describe_current_ontology()}

Current user request:
{user_message}

Instructions:
- Interpret follow-up requests relative to the ontology purpose and current ontology summary.
- For vague follow-ups like "make it more detailed", add specific classes and properties inside the same topic.
- Do not add unrelated generic classes such as Person, Organization, Event, Location, or Product unless the ontology purpose or current request clearly asks for them.
- Every object property domain/range and data property domain must refer to an existing class in the summary or a class included in classes_to_add.
- Use valid Python-style identifiers for class and property names: letters, numbers, and underscores only, starting with a letter or underscore.
- Return raw JSON only. Do not wrap it in Markdown or code fences.
- The JSON object must use this exact structure:
{{
    "classes_to_add": ["Class1", "Class2"],
    "object_properties": [
        {{"name": "hasProperty", "domain": "Class1", "range": "Class2"}}
    ],
    "data_properties": [
        {{"name": "propertyName", "domain": "Class1", "type": "str"}}
    ]
}}"""

    def save_and_visualize(self):
        try:
            self.current_ontology.save(file=self.file_path, format="rdfxml")
            print(f"\nOntology saved to {self.file_path}")
            print("\nTo visualize:")
            print("1. Go to http://localhost:8081/webvowl")
            print("2. Click 'Ontology' in the menu")
            print("3. Select 'Upload ontology from file'")
            print("4. Choose the ontology file from the data directory")
        except Exception as e:
            print(f"Error saving ontology: {e}")

    def process_user_input(self, user_message, is_first_input=False):
        if is_first_input:
            if not self.initialize_ontology(user_message):
                return False
                
        print(f"\nProcessing request: {user_message}")
        response = self.client.generate_response(self.build_change_prompt(user_message))
        print("\nReceived response from AI. Processing changes...")
        changed = self.execute_ontology_changes(response, user_message)
        if changed:
            self.request_history.append(user_message.strip())
        return changed

def main():
    builder = OntologyBuilder()
    
    print("Ontology Chat Bot")
    print("Type 'quit' to exit")
    print("The first request creates a new ontology. Later requests add to that same ontology.")
    print("After each successful input, the ontology will be saved and can be visualized in WebVOWL.")
    
    try:
        is_first_input = True
        while True:
            prompt = "\nDescribe the ontology to create: " if is_first_input else "\nDescribe what to add or change: "
            user_input = input(prompt)
            if user_input.lower() == 'quit':
                break
            changed = builder.process_user_input(user_input, is_first_input)
            if changed:
                builder.save_and_visualize()
                is_first_input = False
            else:
                print("\nNo ontology changes were saved for that input.")
    except KeyboardInterrupt:
        print("\nExiting gracefully...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
