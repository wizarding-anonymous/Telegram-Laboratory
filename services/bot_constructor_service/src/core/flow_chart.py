# services\bot_constructor_service\src\core\flow_chart.py
from typing import List, Dict
from loguru import logger


class FlowChartManager:
    """
    Manager for generating and managing Flow Charts for bot logic.
    """

    def __init__(self):
        """Initialize the FlowChartManager."""
        logger.info("FlowChartManager initialized")

    def generate_flow_chart(self, blocks: List[Dict], connections: List[Dict]) -> Dict:
        """
        Generate a Flow Chart structure from blocks and connections.

        Args:
            blocks (List[Dict]): List of blocks representing bot logic.
            connections (List[Dict]): List of connections between blocks.

        Returns:
            Dict: A dictionary representing the Flow Chart structure.
        """
        logger.info("Generating flow chart")
        nodes = self._generate_nodes(blocks)
        edges = self._generate_edges(connections)
        flow_chart = {"nodes": nodes, "edges": edges}
        logger.info(f"Flow chart generated: {flow_chart}")
        return flow_chart

    def _generate_nodes(self, blocks: List[Dict]) -> List[Dict]:
        """
        Generate nodes for the Flow Chart from blocks.

        Args:
            blocks (List[Dict]): List of blocks representing bot logic.

        Returns:
            List[Dict]: A list of nodes.
        """
        logger.info("Generating nodes for flow chart")
        nodes = []
        for block in blocks:
            nodes.append({
                "id": str(block["id"]),
                "type": block["type"],
                "data": block["content"],
                "position": block.get("position", {"x": 0, "y": 0}),  # Default position
            })
        logger.debug(f"Nodes generated: {nodes}")
        return nodes

    def _generate_edges(self, connections: List[Dict]) -> List[Dict]:
        """
        Generate edges for the Flow Chart from connections.

        Args:
            connections (List[Dict]): List of connections between blocks.

        Returns:
            List[Dict]: A list of edges.
        """
        logger.info("Generating edges for flow chart")
        edges = []
        for connection in connections:
            edges.append({
                "id": f"{connection['source_block_id']}-{connection['target_block_id']}",
                "source": str(connection["source_block_id"]),
                "target": str(connection["target_block_id"]),
                "type": "default",  # Type of edge (can be extended)
            })
        logger.debug(f"Edges generated: {edges}")
        return edges

    def update_node_position(self, node_id: int, new_position: Dict[str, int]) -> None:
        """
        Update the position of a node in the Flow Chart.

        Args:
            node_id (int): ID of the node to update.
            new_position (Dict[str, int]): New position as a dictionary with x and y coordinates.
        """
        logger.info(f"Updating position of node {node_id} to {new_position}")
        # Example: Update position in the database or in-memory structure

    def validate_flow_chart(self, flow_chart: Dict) -> bool:
        """
        Validate the Flow Chart structure.

        Args:
            flow_chart (Dict): The Flow Chart structure to validate.

        Returns:
            bool: True if the Flow Chart is valid, False otherwise.
        """
        logger.info("Validating flow chart")
        if "nodes" not in flow_chart or "edges" not in flow_chart:
            logger.error("Flow chart validation failed: Missing nodes or edges")
            return False
        # Add more validation logic as needed
        logger.info("Flow chart validated successfully")
        return True
