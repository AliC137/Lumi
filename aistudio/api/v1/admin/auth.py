"""
api/v1/admin/auth.py

Admin authentication and verification endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from aistudio.api.v1.admin.schemas import AdminInfo, AdminVerifyResponse
from aistudio.services.user_service import UserService
from aistudio.utils.role_checker import admin_required

router = APIRouter()


@router.get("/verify", response_model=AdminVerifyResponse)
def verify_admin_token(user=Depends(admin_required)):
    """
    Verify that the current token belongs to an admin user.
    Returns verification status and admin information.
    """
    try:
        user_id = user.get('user_id')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id not found"
            )
        
        # Get full user information from database
        service = UserService()
        db_user = service.get_user_by_id(user_id)
        
        # Verify user is admin
        if db_user.role != "admin":
            return AdminVerifyResponse(
                valid=False,
                message="User is not an admin",
                admin_info=None
            )
        
        # Create admin info
        admin_info = AdminInfo(
            user_id=db_user.id,
            login=db_user.login,
            name=db_user.name,
            role=db_user.role,
            created_dt=db_user.created_dt
        )
        
        return AdminVerifyResponse(
            valid=True,
            message="Admin token verified successfully",
            admin_info=admin_info
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying admin token: {str(e)}"
        )


@router.get("/me", response_model=AdminInfo)
def get_current_admin(user=Depends(admin_required)):
    """
    Get current admin user information.
    Returns detailed information about the authenticated admin.
    """
    try:
        user_id = user.get('user_id')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id not found"
            )
        
        # Get full user information from database
        service = UserService()
        db_user = service.get_user_by_id(user_id)
        
        # Verify user is admin
        if db_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admin role required"
            )
        
        # Return admin info
        return AdminInfo(
            user_id=db_user.id,
            login=db_user.login,
            name=db_user.name,
            role=db_user.role,
            created_dt=db_user.created_dt
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting admin information: {str(e)}"
        )

