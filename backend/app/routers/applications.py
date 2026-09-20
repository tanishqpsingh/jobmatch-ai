from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.dependencies import get_current_user
from backend.app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationSummaryResponse,
    ApplicationUpdate,
)
from backend.app.services import application_service

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job application",
)
def create_application_endpoint(
    app_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Create a new job application owned by the authenticated user."""
    return application_service.create_application(db, app_in, user_id=current_user.id)


@router.get(
    "",
    response_model=List[ApplicationResponse],
    status_code=status.HTTP_200_OK,
    summary="List authenticated user applications",
)
def list_applications_endpoint(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ApplicationResponse]:
    """Return only the authenticated user application records."""
    return application_service.get_applications(
        db, user_id=current_user.id, status_filter=status_filter, skip=skip, limit=limit
    )


@router.get(
    "/summary",
    response_model=ApplicationSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard summary for authenticated user",
)
def get_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationSummaryResponse:
    """Return summary statistics scoped to the authenticated user."""
    return application_service.get_dashboard_summary(db, user_id=current_user.id)


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single application by ID",
)
def get_application_endpoint(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Return a single application record owned by the authenticated user."""
    app_obj = application_service.get_application_by_id(db, application_id, user_id=current_user.id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found.",
        )
    return app_obj


@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing application",
)
def update_application_endpoint(
    application_id: int,
    update_in: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Update an application record owned by the authenticated user."""
    updated_obj = application_service.update_application(db, application_id, update_in, user_id=current_user.id)
    if not updated_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found.",
        )
    return updated_obj


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an application",
)
def delete_application_endpoint(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an application record owned by the authenticated user."""
    success = application_service.delete_application(db, application_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found.",
        )
    return None
