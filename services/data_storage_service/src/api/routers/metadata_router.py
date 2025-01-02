from fastapi import APIRouter, Depends, status

from src.api.controllers import MetadataController
from src.api.schemas import (
    MetaCreate,
    MetaResponse,
    MetaUpdate,
    MetaListResponse,
    SuccessResponse
)
from src.api.middleware.auth import auth_required


router = APIRouter(prefix="/metadata", tags=["Metadata"])


@router.post(
    "/",
    response_model=MetaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_required())]
)
async def create_metadata(
    metadata_data: MetaCreate, controller: MetadataController = Depends()
) -> MetaResponse:
    """
    Creates new metadata.
    """
    return await controller.create_metadata(metadata_data=metadata_data)


@router.get(
    "/{metadata_id}",
    response_model=MetaResponse,
    dependencies=[Depends(auth_required())]
)
async def get_metadata(
    metadata_id: int, controller: MetadataController = Depends()
) -> MetaResponse:
    """
    Retrieves metadata by its ID.
    """
    return await controller.get_metadata(metadata_id=metadata_id)

@router.get(
    "/bot/{bot_id}",
    response_model=MetaListResponse,
    dependencies=[Depends(auth_required())]
)
async def get_all_metadata_by_bot_id(
    bot_id: int, controller: MetadataController = Depends()
) -> MetaListResponse:
    """
    Retrieves all metadata for a specific bot ID.
    """
    return await controller.get_all_metadata_by_bot_id(bot_id=bot_id)


@router.put(
    "/{metadata_id}",
    response_model=MetaResponse,
    dependencies=[Depends(auth_required())]
)
async def update_metadata(
    metadata_id: int, metadata_data: MetaUpdate, controller: MetadataController = Depends()
) -> MetaResponse:
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