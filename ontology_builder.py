from api_client import APIClient
from owlready2 import *
import os
import json
from datetime import datetime
import re

class OntologyBuilder:
    def __init__(self):
        self.client = APIClient()
        self.data_dir = "./data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.ontology_name = None
        self.current_ontology = None
        self.file_path = None
        
    def get_ontology_name(self, user_input):
        """Generate ontology name from first user input"""
        response = self.client.generate_response(
            f"""Based on this ontology request, generate a short, descriptive name for the ontology file.
            Return ONLY the name in lowercase, using underscores for spaces, ending in '_ontology'.
            Example: 'library_system_ontology' or 'pet_care_ontology'
            Request: {user_input}"""
        )
        name = response.strip()
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
        print(f"\nCreated new ontology: {self.ontology_name}")
        return True

    def execute_ontology_changes(self, response_text):
        """Execute ontology changes based on LLM response"""
        try:
            print("\nAI suggested changes:")
            print(response_text)
            changes = json.loads(response_text)
            
            print("\nMaking changes to ontology...")
            with self.current_ontology:
                # Create classes
                print("\nCreating classes:")
                for class_name in changes["classes_to_add"]:
                    try:
                        NewClass = types.new_class(class_name, (Thing,))
                        print(f"✓ Created class: {class_name}")
                    except Exception as e:
                        print(f"✗ Error creating class {class_name}: {str(e)}")

                # Create object properties
                print("\nCreating object properties:")
                for prop in changes["object_properties"]:
                    try:
                        prop_name = prop["name"]
                        NewProperty = types.new_class(prop_name, (ObjectProperty,))
                        domain_class = self.current_ontology[prop["domain"]]
                        range_class = self.current_ontology[prop["range"]]
                        NewProperty.domain = [domain_class]
                        NewProperty.range = [range_class]
                        print(f"✓ Created object property: {prop_name} (domain: {prop['domain']}, range: {prop['range']})")
                    except Exception as e:
                        print(f"✗ Error creating object property {prop.get('name', 'unknown')}: {str(e)}")

                # Create data properties
                print("\nCreating data properties:")
                for prop in changes["data_properties"]:
                    try:
                        prop_name = prop["name"]
                        NewProperty = types.new_class(prop_name, (DataProperty,))
                        domain_class = self.current_ontology[prop["domain"]]
                        NewProperty.domain = [domain_class]
                        type_map = {
                            "str": str,
                            "float": float,
                            "int": int,
                            "datetime": datetime,
                            "bool": bool
                        }
                        NewProperty.range = [type_map.get(prop["type"], str)]
                        print(f"✓ Created data property: {prop_name} (domain: {prop['domain']}, type: {prop['type']})")
                    except Exception as e:
                        print(f"✗ Error creating data property {prop.get('name', 'unknown')}: {str(e)}")

                print("\nAll changes completed successfully!")
                return True
                
        except json.JSONDecodeError as e:
            print(f"\nError parsing JSON: {e}")
            print("Response text:", response_text)
            return False
        except Exception as e:
            print(f"\nError executing changes: {e}")
            return False

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
        response = self.client.generate_response(
            f"""Create or modify an ontology based on this request. 
            Return ONLY a valid JSON object with this exact structure:
            {{
                "classes_to_add": ["class1", "class2"],
                "object_properties": [
                    {{"name": "hasProperty", "domain": "class1", "range": "class2"}}
                ],
                "data_properties": [
                    {{"name": "propertyName", "domain": "class1", "type": "str"}}
                ]
            }}

            User request: {user_message}"""
        )
        print("\nReceived response from AI. Processing changes...")
        return self.execute_ontology_changes(response)

def main():
    builder = OntologyBuilder()
    
    print("Ontology Chat Bot")
    print("Type 'quit' to exit")
    print("After each input, the ontology will be saved and can be visualized in WebVOWL")
    
    try:
        is_first_input = True
        while True:
            user_input = input("\nDescribe what you want to add to the ontology: ")
            if user_input.lower() == 'quit':
                break
            builder.process_user_input(user_input, is_first_input)
            builder.save_and_visualize()
            is_first_input = False
    except KeyboardInterrupt:
        print("\nExiting gracefully...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()