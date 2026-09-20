from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.models import Application
from backend.app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationSummaryResponse,
)


def create_application(db: Session, app_in: ApplicationCreate, user_id: int) -> Application:
    """Create a new job application record owned by user_id."""
    db_obj = Application(
        company=app_in.company,
        job_title=app_in.job_title,
        job_description=app_in.job_description,
        application_date=app_in.application_date,
        status=app_in.status,
        interview_date=app_in.interview_date,
        notes=app_in.notes,
        user_id=user_id,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_applications(
    db: Session, user_id: int, status_filter: Optional[str] = None, skip: int = 0, limit: int = 100
) -> List[Application]:
    """Retrieve a list of applications belonging to user_id with optional status filtering."""
    query = db.query(Application).filter(Application.user_id == user_id)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    return query.order_by(Application.updated_at.desc()).offset(skip).limit(limit).all()


def get_application_by_id(db: Session, application_id: int, user_id: int) -> Optional[Application]:
    """Retrieve a single application by ID, scoped to user_id."""
    return (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == user_id)
        .first()
    )


def update_application(
    db: Session, application_id: int, update_in: ApplicationUpdate, user_id: int
) -> Optional[Application]:
    """Update an existing application record scoped to user_id."""
    db_obj = get_application_by_id(db, application_id, user_id)
    if not db_obj:
        return None

    update_data = update_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_application(db: Session, application_id: int, user_id: int) -> bool:
    """Delete an application record scoped to user_id."""
    db_obj = get_application_by_id(db, application_id, user_id)
    if not db_obj:
        return False

    db.delete(db_obj)
    db.commit()
    return True


def get_dashboard_summary(db: Session, user_id: int) -> ApplicationSummaryResponse:
    """Calculate application statistics for user_id only."""
    total = db.query(func.count(Application.id)).filter(Application.user_id == user_id).scalar() or 0

    status_counts = (
        db.query(Application.status, func.count(Application.id))
        .filter(Application.user_id == user_id)
        .group_by(Application.status)
        .all()
    )

    counts_dict = {status: count for status, count in status_counts}

    return ApplicationSummaryResponse(
        total=total,
        saved=counts_dict.get("saved", 0),
        applied=counts_dict.get("applied", 0),
        screening=counts_dict.get("screening", 0),
        interview=counts_dict.get("interview", 0),
        offer=counts_dict.get("offer", 0),
        rejected=counts_dict.get("rejected", 0),
        withdrawn=counts_dict.get("withdrawn", 0),
    )
