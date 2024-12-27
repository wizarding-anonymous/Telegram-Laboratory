from typing import Dict, Any, Optional
from fastapi import HTTPException
from loguru import logger

from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class TemplateManager:
    """
    Manages bot templates.
    """

    def __init__(self):
        """Initializes the TemplateManager."""
        # In a real scenario, templates would be loaded from a database
        # or external storage, but for this example, they are stored as dictionaries
        self.templates: Dict[int, Dict[str, Any]] = {
            1: {
                "name": "Greeting Bot",
                "description": "A simple bot that greets the user.",
                "logic": {
                    "start_block": {
                        "type": "send_text",
                        "content": {"text": "Hello, there!"},
                        "connections": [2],
                    },
                    "blocks": {
                        2: {
                             "type": "text_message",
                            "content": {"text": "Hello, there!"},
                            "connections": [],
                        }
                    },
                },
            },
            2: {
                "name": "Poll Bot",
                "description": "A bot that allows user to create polls.",
                "logic": {
                    "start_block": {
                            "type": "send_text",
                             "content": {"text": "Create poll with text"},
                            "connections": [2],
                        },
                   "blocks": {
                        2: {
                             "type": "text_message",
                             "content": {"text": "What is your favorite color?"},
                            "connections": [3],
                        },
                       3: {
                             "type": "keyboard",
                             "content": {
                                 "keyboard_type":"reply",
                                 "buttons":["Red", "Green", "Blue"]
                             },
                              "connections": []
                        }
                    },
                },
            },
        }
        logging_client.info("TemplateManager initialized with default templates")


    @handle_exceptions
    async def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a template by its ID."""
        logging_client.info(f"Getting template with id: {template_id}")

        if template_id not in self.templates:
             logging_client.warning(f"Template with id: {template_id} not found")
             raise HTTPException(status_code=404, detail="Template not found")

        template = self.templates.get(template_id)
        logging_client.info(f"Template with id: {template_id} retrieved successfully")
        return template

    @handle_exceptions
    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new template."""
        logging_client.info(f"Creating new template with name: {template_data.get('name')}")

        # In a real implementation, it would generate an id from database.
        template_id = len(self.templates) + 1
        self.templates[template_id] = template_data
        logging_client.info(f"Template with id: {template_id} created successfully")
        return template_data

    @handle_exceptions
    async def update_template(
        self, template_id: int, template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Updates an existing template."""
        logging_client.info(f"Updating template with id: {template_id}")
        if template_id not in self.templates:
             logging_client.warning(f"Template with id: {template_id} not found")
             raise HTTPException(status_code=404, detail="Template not found")

        self.templates[template_id] = template_data
        logging_client.info(f"Template with id: {template_id} updated successfully")
        return template_data
    
    @handle_exceptions
    async def delete_template(self, template_id: int) -> None:
        """Deletes a template."""
        logging_client.info(f"Deleting template with id: {template_id}")
        if template_id not in self.templates:
            logging_client.warning(f"Template with id: {template_id} not found")
            raise HTTPException(status_code=404, detail="Template not found")

        del self.templates[template_id]
        logging_client.info(f"Template with id: {template_id} deleted successfully")

    @handle_exceptions
    async def list_templates(self) -> List[Dict[str, Any]]:
        """Lists all available templates"""
        logging_client.info("Listing all templates")
        templates = list(self.templates.values())
        logging_client.info(f"Found {len(templates)} templates")
        return templates