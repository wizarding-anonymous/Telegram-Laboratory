from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.db.repositories import DatabaseRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
import json

class DatabaseHandler:
    """
    Handler for processing database-related blocks.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
       self.session = session
       self.database_repository = DatabaseRepository(session)


    @handle_exceptions
    async def handle_connect_to_database(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Connects to a database.
        Args:
           block (dict): The database connect block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """

        connection_params = block.get("content", {}).get("connection_params")
        if connection_params:
             await self.database_repository.create(bot_id = None, connection_params = connection_params, type = "database_connect")
        else:
           db_uri = block.get("content", {}).get("db_uri")
           await self.database_repository.create(bot_id = None, db_uri = db_uri, type = "database_connect")
    


    @handle_exceptions
    async def handle_execute_query(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Executes a database query.

        Args:
           block (dict): The execute query block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.

        Returns:
            Optional[List[Dict[str, Any]]]: The query results, or None if no result or error.
        """
        query = block.get("content", {}).get("query")
        if not query:
            return None
        
        db_block_id = block.get("content", {}).get("db_block_id")

        db_block = await self.database_repository.get(db_block_id)

        if not db_block:
            raise Exception(f"Database block with id {db_block_id} not found")

        connection_params = db_block.connection_params
        db_uri = db_block.db_uri
        if connection_params:
           results = await self.database_repository.execute_query(query=query, connection_params = connection_params)
        elif db_uri:
           results = await self.database_repository.execute_query(query=query, db_uri = db_uri)
        else:
            raise Exception("Please setup connection parameters or db_uri first")
        
        return results



    @handle_exceptions
    async def handle_fetch_data(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> Optional[Any]:
        """
        Fetches data from the database.

       Args:
            block (dict): The fetch data block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
         Returns:
            Optional[Any]: The fetched data, or None if no result.
        """
        query = block.get("content", {}).get("query")
        if not query:
            return None

        db_block_id = block.get("content", {}).get("db_block_id")
        db_block = await self.database_repository.get(db_block_id)
        if not db_block:
            raise Exception(f"Database block with id {db_block_id} not found")

        connection_params = db_block.connection_params
        db_uri = db_block.db_uri

        if connection_params:
            results = await self.database_repository.fetch_data(query=query, connection_params=connection_params)
        elif db_uri:
            results = await self.database_repository.fetch_data(query=query, db_uri=db_uri)
        else:
            raise Exception("Please setup connection parameters or db_uri first")
        if results:
           if len(results) == 1:
             return results[0]
           return results
        return None
    

    @handle_exceptions
    async def handle_insert_data(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Inserts data into the database.

        Args:
          block (dict): The insert data block details from database.
          chat_id (int): Telegram chat ID where the interaction is happening.
          variables (dict): Dictionary of variables.
        """
        query = block.get("content", {}).get("query")
        if not query:
            return None
        db_block_id = block.get("content", {}).get("db_block_id")

        db_block = await self.database_repository.get(db_block_id)
        if not db_block:
            raise Exception(f"Database block with id {db_block_id} not found")
        
        connection_params = db_block.connection_params
        db_uri = db_block.db_uri
        if connection_params:
           await self.database_repository.insert_data(query=query, connection_params = connection_params)
        elif db_uri:
           await self.database_repository.insert_data(query=query, db_uri = db_uri)
        else:
            raise Exception("Please setup connection parameters or db_uri first")

    @handle_exceptions
    async def handle_update_data(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Updates data in the database.

         Args:
            block (dict): The update data block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        query = block.get("content", {}).get("query")
        if not query:
            return None

        db_block_id = block.get("content", {}).get("db_block_id")
        db_block = await self.database_repository.get(db_block_id)
        if not db_block:
             raise Exception(f"Database block with id {db_block_id} not found")
        connection_params = db_block.connection_params
        db_uri = db_block.db_uri
        if connection_params:
           await self.database_repository.update_data(query=query, connection_params = connection_params)
        elif db_uri:
           await self.database_repository.update_data(query=query, db_uri = db_uri)
        else:
             raise Exception("Please setup connection parameters or db_uri first")


    @handle_exceptions
    async def handle_delete_data(self, block: Dict[str, Any], chat_id: int, variables: Dict[str,Any]) -> None:
        """
        Deletes data from the database.

        Args:
            block (dict): The delete data block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        query = block.get("content", {}).get("query")
        if not query:
            return None
            
        db_block_id = block.get("content", {}).get("db_block_id")
        db_block = await self.database_repository.get(db_block_id)
        if not db_block:
             raise Exception(f"Database block with id {db_block_id} not found")

        connection_params = db_block.connection_params
        db_uri = db_block.db_uri
        if connection_params:
             await self.database_repository.delete_data(query=query, connection_params = connection_params)
        elif db_uri:
             await self.database_repository.delete_data(query=query, db_uri = db_uri)
        else:
            raise Exception("Please setup connection parameters or db_uri first")