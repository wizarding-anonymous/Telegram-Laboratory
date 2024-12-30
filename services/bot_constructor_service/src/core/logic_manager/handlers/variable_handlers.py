from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.integrations.redis_client import redis_client
import json
from src.core.logic_manager.handlers.utils import get_template

class VariableHandler:
    """
    Handler for processing variable-related blocks.
    """
    
    @handle_exceptions
    async def handle_define_variable(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Defines a new variable or updates existing one in variables dictionary.

        Args:
            block (dict): The define variable block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        name = block.get("content", {}).get("name")
        value = block.get("content", {}).get("value")
        
        if name:
          variables[name] = value

    
    @handle_exceptions
    async def handle_assign_value(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Assigns a new value to an existing variable.

        Args:
           block (dict): The assign value block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
        name = block.get("content", {}).get("name")
        value = block.get("content", {}).get("value")

        if name and name in variables:
           if value:
              template = get_template(value)
              rendered_value = template.render(variables=variables)
              variables[name] = rendered_value
           else:
             variables[name] = value

    @handle_exceptions
    async def handle_retrieve_value(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
       """
        Retrieves a value of a variable and sets in another variable.

        Args:
           block (dict): The retrieve value block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
       source_name = block.get("content", {}).get("source_name")
       target_name = block.get("content", {}).get("target_name")
       
       if source_name and target_name and source_name in variables:
         variables[target_name] = variables.get(source_name)
        

    @handle_exceptions
    async def handle_update_value(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Updates value of a variable in variables dictionary.

        Args:
           block (dict): The update value block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
        name = block.get("content", {}).get("name")
        value = block.get("content", {}).get("value")
        if name and name in variables and value:
              template = get_template(value)
              rendered_value = template.render(variables=variables)
              variables[name] = rendered_value
from src.core.logic_manager.handlers.utils import get_template