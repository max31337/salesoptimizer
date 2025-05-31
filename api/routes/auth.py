from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from application.dependencies.service_dependencies import (
    get_application_service,
    ApplicationService
)
from application.dtos.auth_dto import LoginResponse
from application.commands.auth_command import LoginCommand
from domain.organization.exceptions.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserNotFoundError,
    InactiveUserError
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    form_data: OAuth2PasswordRequestForm = Depends()
) -> LoginResponse:
    """Authenticate user and return access token."""
    
    try:
        # Create login command
        command = LoginCommand(
            email_or_username=form_data.username,
            password=form_data.password
        )
        
        # Execute login use case
        user, access_token, refresh_token = await app_service.auth_use_cases.login(command)
        
        if not user.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing"
            )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.id.value,
            tenant_id=user.tenant_id,
            role=user.role.value,
            email=str(user.email),
            full_name=user.full_name
        )
    
    except (InvalidCredentialsError, UserNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    except InactiveUserError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not active"
        )
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )