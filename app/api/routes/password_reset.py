from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.password_reset import (
    PasswordResetRequest,
    PasswordResetTokenResponse,
    PasswordResetConfirm,
    PasswordResetResult,
    UserRegisteredEvent
)
from app.services.password_reset_service import password_reset_service
from app.services.event_service import event_service

router = APIRouter()


@router.post("/reset-request", response_model=PasswordResetTokenResponse)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset email
    """
    try:
        result = await password_reset_service.request_password_reset(db, reset_request.email)
        
        # Always return success to prevent email enumeration attacks
        return PasswordResetTokenResponse(
            message="If your email is registered, you will receive a password reset link.",
            email=reset_request.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.post("/reset-confirm", response_model=PasswordResetResult)
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token
    """
    try:
        success, message = await password_reset_service.reset_password(
            db, reset_confirm.token, reset_confirm.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )
        
        return PasswordResetResult(
            success=success,
            message=message
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok", "service": "reset-password-service"}


@router.post("/events/user-registered", status_code=status.HTTP_201_CREATED)
async def handle_user_registered_event(
    event: UserRegisteredEvent,
    db: Session = Depends(get_db)
):
    """
    Handle user registered event
    """
    try:
        result = await event_service.log_user_event(db, event)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to log event",
            )
        return {"status": "success", "message": "Event logged successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
