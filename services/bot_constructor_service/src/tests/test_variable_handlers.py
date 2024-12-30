import pytest
from typing import Dict, Any
from src.core.logic_manager.handlers.control_handlers import ControlHandler


@pytest.mark.asyncio
async def test_handle_variable_block_define():
    """Test defining a variable."""
    handler = ControlHandler()
    variables = {}
    test_block = {
        "id": 1,
        "type": "variable",
        "content": {"action": "define", "name": "test_var", "value": "test_value"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "test_value"


@pytest.mark.asyncio
async def test_handle_variable_block_assign():
    """Test assigning a value to a variable."""
    handler = ControlHandler()
    variables = {"test_var": "old_value"}
    test_block = {
        "id": 1,
        "type": "variable",
        "content": {"action": "assign", "name": "test_var", "value": "new_value"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "new_value"


@pytest.mark.asyncio
async def test_handle_variable_block_retrieve():
    """Test retrieving a variable's value (no change to variables)."""
    handler = ControlHandler()
    variables = {"test_var": "existing_value"}
    test_block = {
        "id": 1,
        "type": "variable",
        "content": {"action": "retrieve", "name": "test_var"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "existing_value"

@pytest.mark.asyncio
async def test_handle_variable_block_update():
    """Test updating a variable's value."""
    handler = ControlHandler()
    variables = {"test_var": "old_value"}
    test_block = {
      "id": 1,
      "type": "variable",
        "content": {"action": "update", "name": "test_var", "value": "updated_value"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "updated_value"

@pytest.mark.asyncio
async def test_handle_variable_block_invalid_action():
    """Test with an invalid action."""
    handler = ControlHandler()
    variables = {"test_var": "old_value"}
    test_block = {
        "id": 1,
        "type": "variable",
        "content": {"action": "invalid_action", "name": "test_var"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "old_value"
    

@pytest.mark.asyncio
async def test_handle_variable_block_template_value():
    """Test defining a variable with jinja template in value."""
    handler = ControlHandler()
    variables = {"test": "test_value"}
    test_block = {
         "id": 1,
        "type": "variable",
        "content": {"action": "define", "name": "test_var", "value": "The {{test}}"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "The test_value"
    

@pytest.mark.asyncio
async def test_handle_variable_block_no_name():
    """Test defining a variable without name."""
    handler = ControlHandler()
    variables = {}
    test_block = {
       "id": 1,
        "type": "variable",
        "content": {"action": "define",  "value": "test_value"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert not variables

@pytest.mark.asyncio
async def test_handle_variable_block_no_value_assign():
    """Test assign a variable without value."""
    handler = ControlHandler()
    variables = {"test_var": "old_value"}
    test_block = {
      "id": 1,
        "type": "variable",
        "content": {"action": "assign", "name": "test_var"},
    }
    await handler.handle_variable_block(
        block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "old_value"
    
@pytest.mark.asyncio
async def test_handle_variable_block_no_value_update():
    """Test update a variable without value."""
    handler = ControlHandler()
    variables = {"test_var": "old_value"}
    test_block = {
        "id": 1,
        "type": "variable",
        "content": {"action": "update", "name": "test_var"},
    }
    await handler.handle_variable_block(
       block=test_block, chat_id=123, variables=variables
    )
    assert variables["test_var"] == "old_value"