from fastapi import APIRouter, Depends, HTTPException, Query, Request
from schemas.reminder_schema import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse,
    ReminderLogCreate,
    ReminderLogResponse,
    UpcomingReminderResponse,
)
from repositories.reminder_repository import ReminderRepository
from auth.dependency import get_current_user
from utils.rate_limit import limiter

router = APIRouter()


@router.post("/reminders", response_model=ReminderResponse)
@limiter.limit("10/minute")
async def create_reminder(
    request: Request,
    input_data: ReminderCreate,
    user_id: str = Depends(get_current_user),
    reminder_repository: ReminderRepository = Depends(),
):
    reminder = await reminder_repository.create(
        user_id, input_data.model_dump()
    )
    rid = str(reminder.pop("_id"))
    return ReminderResponse(
        _id=rid,
        user_id=reminder["userId"],
        medicine_name=reminder["medicine_name"],
        dosage=reminder["dosage"],
        frequency=reminder["frequency"],
        schedule_details=reminder.get("schedule_details", {}),
        duration_days=reminder["duration_days"],
        start_time=reminder["start_time"],
        status=reminder["status"],
        email_reminder=reminder.get("email_reminder", False),
        linked_prediction_id=reminder.get("linked_prediction_id"),
        next_due_at=reminder.get("nextDueAt"),
        created_at=reminder["createdAt"],
        updated_at=reminder["updatedAt"],
    )


@router.get("/reminders", response_model=ReminderListResponse)
@limiter.limit("10/minute")
async def list_reminders(
    request: Request,
    status: str | None = Query(None, pattern="^(active|paused|completed)$"),
    user_id: str = Depends(get_current_user),
    reminder_repository: ReminderRepository = Depends(),
):
    reminders = await reminder_repository.find_by_user(user_id, status=status)
    results = [
        ReminderResponse(
            _id=str(r.pop("_id")),
            user_id=r["userId"],
            medicine_name=r["medicine_name"],
            dosage=r["dosage"],
            frequency=r["frequency"],
            schedule_details=r.get("schedule_details", {}),
            duration_days=r["duration_days"],
            start_time=r["start_time"],
            status=r["status"],
            email_reminder=r.get("email_reminder", False),
            linked_prediction_id=r.get("linked_prediction_id"),
            next_due_at=r.get("nextDueAt"),
            created_at=r["createdAt"],
            updated_at=r["updatedAt"],
        )
        for r in reminders
    ]
    return ReminderListResponse(reminders=results, total=len(results))


@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
@limiter.limit("10/minute")
async def update_reminder(
    request: Request,
    reminder_id: str,
    input_data: ReminderUpdate,
    user_id: str = Depends(get_current_user),
    reminder_repository: ReminderRepository = Depends(),
):
    existing = await reminder_repository.find_by_id(reminder_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if existing.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    update_data = {k: v for k, v in input_data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = await reminder_repository.update(reminder_id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")

    rid = str(updated.pop("_id"))
    return ReminderResponse(
        _id=rid,
        user_id=updated["userId"],
        medicine_name=updated["medicine_name"],
        dosage=updated["dosage"],
        frequency=updated["frequency"],
        schedule_details=updated.get("schedule_details", {}),
        duration_days=updated["duration_days"],
        start_time=updated["start_time"],
        status=updated["status"],
        email_reminder=updated.get("email_reminder", False),
        linked_prediction_id=updated.get("linked_prediction_id"),
        next_due_at=updated.get("nextDueAt"),
        created_at=updated["createdAt"],
        updated_at=updated["updatedAt"],
    )


@router.delete("/reminders/{reminder_id}")
@limiter.limit("10/minute")
async def delete_reminder(
    request: Request,
    reminder_id: str,
    user_id: str = Depends(get_current_user),
    reminder_repository: ReminderRepository = Depends(),
):
    existing = await reminder_repository.find_by_id(reminder_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if existing.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    deleted = await reminder_repository.delete(reminder_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Delete failed")
    return {"detail": "Reminder deleted"}


@router.post(
    "/reminders/{reminder_id}/log", response_model=ReminderLogResponse
)
@limiter.limit("10/minute")
async def log_reminder_status(
    request: Request,
    reminder_id: str,
    input_data: ReminderLogCreate,
    user_id: str = Depends(get_current_user),
    reminder_repository: ReminderRepository = Depends(),
):
    existing = await reminder_repository.find_by_id(reminder_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if existing.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    log_entry = await reminder_repository.log_status(
        reminder_id, user_id, input_data.status, input_data.note
    )
    lid = str(log_entry.pop("_id"))
    return ReminderLogResponse(
        _id=lid,
        reminder_id=log_entry["reminderId"],
        status=log_entry["status"],
        timestamp=log_entry["timestamp"],
        note=log_entry.get("note"),
    )


@router.get(
    "/reminders/upcoming", response_model=UpcomingReminderResponse
)
@limiter.limit("10/minute")
async def get_upcoming_reminder(
    request: Request,
    user_id: str = Depends(get_current_user),
    reminder_repository: ReminderRepository = Depends(),
):
    upcoming = await reminder_repository.find_upcoming(user_id)
    if not upcoming:
        return UpcomingReminderResponse(reminder=None, has_upcoming=False)

    uid = str(upcoming.pop("_id"))
    reminder_resp = ReminderResponse(
        _id=uid,
        user_id=upcoming["userId"],
        medicine_name=upcoming["medicine_name"],
        dosage=upcoming["dosage"],
        frequency=upcoming["frequency"],
        schedule_details=upcoming.get("schedule_details", {}),
        duration_days=upcoming["duration_days"],
        start_time=upcoming["start_time"],
        status=upcoming["status"],
        email_reminder=upcoming.get("email_reminder", False),
        linked_prediction_id=upcoming.get("linked_prediction_id"),
        next_due_at=upcoming.get("nextDueAt"),
        created_at=upcoming["createdAt"],
        updated_at=upcoming["updatedAt"],
    )
    return UpcomingReminderResponse(
        reminder=reminder_resp, has_upcoming=True
    )
