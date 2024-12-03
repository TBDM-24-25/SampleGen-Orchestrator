from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError
from typing import Optional, Dict, Any
from models import SchemaData


class SchemaService:
    def __init__(self, template_dir: str = "templates/"):
        self.environment = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.environment.get_template("schema.json")

    def render_template(self, data: Dict[str, Any]) -> Optional[str]:
        try:
            content = self.template.render(data)
            return content
        except Exception as e:
            print(f"Error rendering template: {e}")
            return None

    def validate_schema(self, data: Dict[str, Any]) -> bool:
        try:
            SchemaData(**data)
            return True
        except ValidationError as e:
            print("Validation error:", e)
            return False

    def create_schema(self, data: Dict[str, Any]) -> str:
        if self.validate_schema(data):
            rendered_yaml = self.render_template(data)
            if rendered_yaml is None:
                raise Exception("Error rendering template")
            return rendered_yaml
        else:
            raise Exception("Data validation failed")


