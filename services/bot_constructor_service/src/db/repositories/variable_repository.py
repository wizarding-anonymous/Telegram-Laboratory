from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils import handle_exceptions
from src.db.models.variable_model import Variable
from src.integrations.logging_client import LoggingClient

logging_client = LoggingClient(service_name="bot_constructor")


class VariableRepository:
    """
    Repository for performing database operations on variable entities.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the VariableRepository with a database session."""
        self.session = session
        logging_client.info("VariableRepository initialized")

    @handle_exceptions
    async def create(self, variable_data: dict) -> Variable:
        """Creates a new variable in the database."""
        logging_client.info(f"Creating new variable with data: {variable_data}")
        variable = Variable(**variable_data)
        self.session.add(variable)
        await self.session.commit()
        await self.session.refresh(variable)
        logging_client.info(f"Variable with id: {variable.id} created successfully")
        return variable

    @handle_exceptions
    async def get_by_id(self, variable_id: int) -> Optional[Variable]:
        """Retrieves a variable by its ID."""
        logging_client.info(f"Getting variable by id: {variable_id}")
        variable = await self.session.get(Variable, variable_id)
        if variable:
            logging_client.info(f"Variable with id: {variable_id} retrieved successfully")
        else:
            logging_client.warning(f"Variable with id: {variable_id} not found")
        return variable

    @handle_exceptions
    async def get_all_by_bot_id(self, bot_id: int) -> List[Variable]:
        """Retrieves all variables for a specific bot."""
        logging_client.info(f"Getting all variables for bot_id: {bot_id}")
        query = select(Variable).where(Variable.bot_id == bot_id)
        result = await self.session.execute(query)
        variables = result.scalars().all()
        logging_client.info(f"Found {len(variables)} variables for bot_id: {bot_id}")
        return list(variables)

    @handle_exceptions
    async def update(self, variable_id: int, variable_data: dict) -> Optional[Variable]:
        """Updates an existing variable."""
        logging_client.info(f"Updating variable with id: {variable_id} with data: {variable_data}")
        variable = await self.session.get(Variable, variable_id)
        if variable:
            for key, value in variable_data.items():
                setattr(variable, key, value)
            await self.session.commit()
            await self.session.refresh(variable)
            logging_client.info(f"Variable with id: {variable_id} updated successfully")
            return variable
        logging_client.warning(f"Variable with id: {variable_id} not found for update")
        return None

    @handle_exceptions
    async def delete(self, variable_id: int) -> bool:
        """Deletes a variable by its ID."""
        logging_client.info(f"Deleting variable with id: {variable_id}")
        variable = await self.session.get(Variable, variable_id)
        if variable:
            await self.session.delete(variable)
            await self.session.commit()
            logging_client.info(f"Variable with id: {variable_id} deleted successfully")
            return True
        logging_client.warning(f"Variable with id: {variable_id} not found for delete")
        return False