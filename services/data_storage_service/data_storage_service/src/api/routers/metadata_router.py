from fastapi import APIRouter, Depends, status

from src.api.controllers import MetadataController
from src.api.schemas import (
    MetadataCreate,
    MetadataResponse,
    MetadataUpdate,
    SuccessResponse
)
from src.api.middleware.auth import auth_required


router = APIRouter(prefix="/metadata", tags=["Metadata"])


@router.post(
    "/",
    response_model=MetadataResponse,
    status_code=status.HTTP_201_CREATED,
     dependencies=[Depends(auth_required())]
)
async def create_metadata(
    metadata_data: MetadataCreate, controller: MetadataController = Depends()
) -> MetadataResponse:
    """
    Creates new metadata.
    """
    return await controller.create_metadata(metadata_data=metadata_data)


@router.get(
    "/{metadata_id}",
    response_model=MetadataResponse,
    dependencies=[Depends(auth_required())]
)
async def get_metadata(
    metadata_id: int, controller: MetadataController = Depends()
) -> MetadataResponse:
    """
    Retrieves metadata by its ID.
    """
    return await controller.get_metadata(metadata_id=metadata_id)


@router.put(
    "/{metadata_id}",
    response_model=MetadataResponse,
    dependencies=[Depends(auth_required())]
)
async def update_metadata(
    metadata_id: int, metadata_data: MetadataUpdate, controller: MetadataController = Depends()
) -> MetadataResponse:
    """
    Updates existing metadata.
    """
    return await controller.update_metadata(metadata_id=metadata_id, metadata_data=metadata_data)


@router.delete(
    "/{metadata_id}",
    response_model=SuccessResponse,
     dependencies=[Depends(auth_required())]
)
async def delete_metadata(
    metadata_id: int, controller: MetadataController = Depends()
) -> SuccessResponse:
    """
    Deletes metadata by its ID.
    """
    return await controller.delete_metadata(metadata_id=metadata_id)