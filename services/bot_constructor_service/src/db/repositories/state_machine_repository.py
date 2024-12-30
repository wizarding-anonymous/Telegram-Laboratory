from typing import List, Dict, Any, Tuple, Optional
from fastapi import HTTPException
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.db.database import get_session
from src.db.models import StateMachine
from src.core.utils import handle_exceptions
from src.integrations.logging_client import LoggingClient


logging_client = LoggingClient(service_name="bot_constructor")


class StateMachineRepository:
    """
    Repository for managing state machine data in the database.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        logging_client.info("StateMachineRepository initialized")

    @handle_exceptions
    async def create(self, bot_id: int, state_machine_data: Dict[str, Any]) -> StateMachine:
        """Creates a new state machine block."""
        logging_client.info(f"Creating state machine block for bot_id: {bot_id}")
        state_machine = StateMachine(**state_machine_data, bot_id=bot_id)
        self.session.add(state_machine)
        await self.session.commit()
        await self.session.refresh(state_machine)
        logging_client.info(f"State machine block with id: {state_machine.id} created successfully")
        return state_machine

    @handle_exceptions
    async def get_by_id(self, state_machine_id: int) -> Optional[StateMachine]:
        """Gets a state machine block by its ID."""
        logging_client.info(f"Getting state machine block with id: {state_machine_id}")
        result = await self.session.execute(select(StateMachine).where(StateMachine.id == state_machine_id))
        state_machine = result.scalar_one_or_none()
        if state_machine:
            logging_client.info(f"State machine block with id: {state_machine_id} retrieved successfully")
        else:
            logging_client.warning(f"State machine block with id: {state_machine_id} not found")
        return state_machine

    @handle_exceptions
    async def list_by_bot_id(self, bot_id: int) -> List[StateMachine]:
        """Gets a list of state machine blocks for a specific bot."""
        logging_client.info(f"Getting list of state machine blocks for bot_id: {bot_id}")
        query = select(StateMachine).where(StateMachine.bot_id == bot_id)
        result = await self.session.execute(query)
        state_machines = list(result.scalars().all())
        logging_client.info(f"Found {len(state_machines)} state machine blocks for bot_id: {bot_id}")
        return state_machines

    @handle_exceptions
    async def update(self, state_machine_id: int, state_machine_data: Dict[str, Any]) -> StateMachine:
        """Updates an existing state machine block."""
        logging_client.info(f"Updating state machine block with id: {state_machine_id}")
        query = (
            update(StateMachine)
            .where(StateMachine.id == state_machine_id)
            .values(state_machine_data)
            .returning(StateMachine)
        )
        result = await self.session.execute(query)
        updated_state_machine = result.scalar_one_or_none()
        if not updated_state_machine:
             logging_client.warning(f"State machine block with id: {state_machine_id} not found")
             raise HTTPException(status_code=404, detail="State machine block not found")
        await self.session.commit()
        logging_client.info(f"State machine block with id: {state_machine_id} updated successfully")
        return updated_state_machine

    @handle_exceptions
    async def delete(self, state_machine_id: int) -> None:
        """Deletes a state machine block."""
        logging_client.info(f"Deleting state machine block with id: {state_machine_id}")
        query = delete(StateMachine).where(StateMachine.id == state_machine_id)
        await self.session.execute(query)
        await self.session.commit()
        logging_client.info(f"State machine block with id: {state_machine_id} deleted successfully")