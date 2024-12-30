from typing import List, Dict, Any, Optional
from src.core.utils import handle_exceptions
from src.db.repositories import DatabaseRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.core.logic_manager.utils import get_template
from src.integrations.logging_client import LoggingClient
from src.core.utils.validators import validate_database_data
import json


logging_client = LoggingClient(service_name="bot_constructor")


class DatabaseHandler:
    """
    Handler for processing database-related blocks.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.database_repository = DatabaseRepository(session)

    @handle_exceptions
    async def handle_database_connect(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any]
    ) -> None:
        """
        Connects to a database.

        Args:
           block (dict): The database connect block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.
        """
        logging_client.info(f"Handling connect to database block for chat_id: {chat_id}")
        validate_database_data(block.get("content", {}))
        connection_params = block.get("content", {}).get("connection_params", {})
        db_uri = block.get("content", {}).get("db_uri")
        
        if connection_params:
            rendered_params = {
                k: get_template(str(v)).render(variables=variables)
                for k, v in connection_params.items()
            }
            await self.database_repository.create(bot_id = None, connection_params = rendered_params, type = "database_connect")

        elif db_uri:
            rendered_db_uri = get_template(db_uri).render(variables=variables)
            await self.database_repository.create(bot_id = None, db_uri = rendered_db_uri, type = "database_connect")

        else:
          logging_client.warning("Database connection params or url is not provided")
          return None
        
    @handle_exceptions
    async def handle_database_query(
        self,
        block: Dict[str, Any],
        chat_id: int,
        user_message: str,
        bot_logic: Dict[str, Any],
        variables: Dict[str, Any],
    ) -> Optional[int]:
        """
        Executes a database query.

        Args:
           block (dict): The execute query block details from the database.
           chat_id (int): Telegram chat ID where the interaction is happening.
           variables (dict): Dictionary of variables.

        Returns:
            Optional[int]: The query results, or None if no result or error.
        """
        content = block.get("content", {})
        logging_client.info(
            f"Handling execute database query block for chat_id: {chat_id}"
        )
        validate_database_data(content)
        query_template = content.get("query")
        if not query_template:
            logging_client.warning("Database query not defined for database block")
            return None
        db_block_id = content.get("db_block_id")
        if not db_block_id:
            logging_client.warning("Database block id is not defined")
            return None

        db_block = await self.database_repository.get_by_id(db_block_id)
        if not db_block:
              logging_client.warning(f"Database block with id {db_block_id} not found")
              return None
            
        connection_params = db_block.connection_params
        db_uri = db_block.db_uri
        query = get_template(query_template).render(variables=variables)
        try:
            if connection_params:
               rendered_params = {
                    k: get_template(str(v)).render(variables=variables)
                    for k, v in connection_params.items()
                }
               results = await self.database_repository.execute_query(
                    query=query, connection_params=rendered_params
                )
            elif db_uri:
                rendered_db_uri = get_template(db_uri).render(variables=variables)
                results = await self.database_repository.execute_query(
                  query=query, db_uri=rendered_db_uri
                  )
            else:
               logging_client.warning(f"Database parameters are not properly configured for block id: {block.get('id')}")
               return None
            
            if results:
                formatted_result = [dict(row) for row in results]
                logging_client.info(
                   f"Database query successful, result: {formatted_result}"
                )
                response_block_id = content.get("response_block_id")
                if response_block_id:
                    from src.core.logic_manager import LogicManager
                    logic_manager = LogicManager()
                    from src.db.repositories import BlockRepository
                    block_repository = BlockRepository()
                    response_block = await block_repository.get_by_id(response_block_id)
                    if response_block:
                         await logic_manager._process_block(
                                Block(**response_block.model_dump()),
                                  chat_id,
                                  str({"result": formatted_result}),
                                  bot_logic,
                                  variables,
                              )
                         return None
                    else:
                           logging_client.warning(
                                f"Response block with id: {response_block_id} was not found"
                            )
                else:
                  logging_client.warning(f"No response block was configured for block id: {block.get('id')}")
            else:
                logging_client.info("Database query successful, no results found.")

        except Exception as e:
            logging_client.error(f"Database query failed: {e}")
            raise

        return None

    @handle_exceptions
    async def handle_fetch_data(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any], bot_logic: Dict[str, Any], user_message: str
    ) -> Optional[Any]:
        """
        Fetches data from the database.

       Args:
            block (dict): The fetch data block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
         Returns:
            Optional[Any]: The fetched data, or None if no result.
        """
        content = block.get("content", {})
        logging_client.info(
            f"Handling fetch data block for chat_id: {chat_id}. User message was: {user_message}"
        )
        validate_database_data(content)
        query_template = content.get("query")
        if not query_template:
            logging_client.warning("Database query not defined for database block")
            return None
        db_block_id = content.get("db_block_id")
        if not db_block_id:
            logging_client.warning("Database block id is not defined")
            return None
        db_block = await self.database_repository.get_by_id(db_block_id)

        if not db_block:
              logging_client.warning(f"Database block with id {db_block_id} not found")
              return None

        connection_params = db_block.connection_params
        db_uri = db_block.db_uri
        query = get_template(query_template).render(variables=variables)
        try:
            if connection_params:
                rendered_params = {
                  k: get_template(str(v)).render(variables=variables)
                   for k, v in connection_params.items()
                }
                results = await self.database_repository.fetch_data(
                    query=query, connection_params=rendered_params
               )
            elif db_uri:
                rendered_db_uri = get_template(db_uri).render(variables=variables)
                results = await self.database_repository.fetch_data(
                    query=query, db_uri=rendered_db_uri
                  )
            else:
                 logging_client.warning(f"Database parameters are not properly configured for block id: {block.get('id')}")
                 return None
            if results:
               if len(results) == 1:
                 return results[0]
               return results
            return None
        except Exception as e:
            logging_client.error(f"Database fetch data failed: {e}")
            raise
        return None

    @handle_exceptions
    async def handle_insert_data(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any], bot_logic: Dict[str, Any], user_message: str
    ) -> Optional[int]:
        """
        Inserts data into the database.

        Args:
          block (dict): The insert data block details from database.
          chat_id (int): Telegram chat ID where the interaction is happening.
          variables (dict): Dictionary of variables.
        """
        content = block.get("content", {})
        logging_client.info(f"Handling insert data block for chat_id: {chat_id}. User message was: {user_message}")
        validate_database_data(content)
        query_template = content.get("query")
        if not query_template:
            logging_client.warning("Database query not defined for insert data block")
            return None
        db_block_id = content.get("db_block_id")
        if not db_block_id:
            logging_client.warning("Database block id is not defined")
            return None

        db_block = await self.database_repository.get_by_id(db_block_id)
        if not db_block:
           logging_client.warning(f"Database block with id {db_block_id} not found")
           return None
           
        query = get_template(query_template).render(variables=variables)
        connection_params = db_block.connection_params
        db_uri = db_block.db_uri
        try:
            if connection_params:
                rendered_params = {
                    k: get_template(str(v)).render(variables=variables)
                    for k, v in connection_params.items()
                }
                await self.database_repository.insert_data(
                    query=query, connection_params=rendered_params
                )
            elif db_uri:
                 rendered_db_uri = get_template(db_uri).render(variables=variables)
                 await self.database_repository.insert_data(
                    query=query, db_uri=rendered_db_uri
                 )
            else:
                logging_client.warning(f"Database parameters are not properly configured for block id: {block.get('id')}")
                return None

            logging_client.info(f"Database insert query successful")
            next_blocks = await self.database_repository._get_next_blocks(block.id, bot_logic)
            if next_blocks:
                return next_blocks[0].get("id")
        except Exception as e:
            logging_client.error(f"Database insert failed: {e}")
            raise
        return None

    @handle_exceptions
    async def handle_update_data(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any], bot_logic: Dict[str, Any], user_message: str
    ) -> Optional[int]:
        """
        Updates data in the database.

        Args:
            block (dict): The update data block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        content = block.get("content", {})
        logging_client.info(f"Handling update data block for chat_id: {chat_id}. User message was: {user_message}")
        validate_database_data(content)
        query_template = content.get("query")
        if not query_template:
            logging_client.warning("Database query not defined for update data block")
            return None
        db_block_id = content.get("db_block_id")
        if not db_block_id:
             logging_client.warning("Database block id is not defined")
             return None

        db_block = await self.database_repository.get_by_id(db_block_id)
        if not db_block:
             logging_client.warning(f"Database block with id {db_block_id} not found")
             return None
        
        connection_params = db_block.connection_params
        db_uri = db_block.db_uri
        query = get_template(query_template).render(variables=variables)
        try:
            if connection_params:
                rendered_params = {
                    k: get_template(str(v)).render(variables=variables)
                     for k, v in connection_params.items()
                  }
                await self.database_repository.update_data(
                    query=query, connection_params=rendered_params
                 )
            elif db_uri:
                 rendered_db_uri = get_template(db_uri).render(variables=variables)
                 await self.database_repository.update_data(
                     query=query, db_uri=rendered_db_uri
                  )
            else:
                 logging_client.warning(f"Database parameters are not properly configured for block id: {block.get('id')}")
                 return None

            logging_client.info(f"Database update query successful")
            next_blocks = await self.database_repository._get_next_blocks(block.id, bot_logic)
            if next_blocks:
               return next_blocks[0].get("id")
        except Exception as e:
            logging_client.error(f"Database update failed: {e}")
            raise
        return None


    @handle_exceptions
    async def handle_delete_data(
        self, block: Dict[str, Any], chat_id: int, variables: Dict[str, Any], bot_logic: Dict[str, Any], user_message: str
    ) -> Optional[int]:
        """
        Deletes data from the database.

        Args:
            block (dict): The delete data block details from the database.
            chat_id (int): Telegram chat ID where the interaction is happening.
            variables (dict): Dictionary of variables.
        """
        content = block.get("content", {})
        logging_client.info(f"Handling delete data block for chat_id: {chat_id}. User message was: {user_message}")
        validate_database_data(content)
        query_template = content.get("query")
        if not query_template:
            logging_client.warning("Database query not defined for delete data block")
            return None
        db_block_id = content.get("db_block_id")
        if not db_block_id:
            logging_client.warning("Database block id is not defined")
            return None

        db_block = await self.database_repository.get_by_id(db_block_id)
        if not db_block:
             logging_client.warning(f"Database block with id {db_block_id} not found")
             return None

        connection_params = db_block.connection_params
        db_uri = db_block.db_uri
        query = get_template(query_template).render(variables=variables)
        try:
           if connection_params:
              rendered_params = {
                   k: get_template(str(v)).render(variables=variables)
                    for k, v in connection_params.items()
                 }
              await self.database_repository.delete_data(
                   query=query, connection_params=rendered_params
                  )
           elif db_uri:
              rendered_db_uri = get_template(db_uri).render(variables=variables)
              await self.database_repository.delete_data(
                    query=query, db_uri=rendered_db_uri
                 )
           else:
                 logging_client.warning(f"Database parameters are not properly configured for block id: {block.get('id')}")
                 return None

           logging_client.info(f"Database delete query successful")
           next_blocks = await self.database_repository._get_next_blocks(block.id, bot_logic)
           if next_blocks:
                return next_blocks[0].get("id")
        except Exception as e:
            logging_client.error(f"Database delete failed: {e}")
            raise
        return None