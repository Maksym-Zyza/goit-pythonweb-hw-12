from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
    Form,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from src.database.db import get_db
from src.schemas.users import (
    UserResponse,
    UserModel,
    TokenModel,
    RequestEmail,
)
from src.services.auth import auth_service
from src.repository.users import (
    get_user_by_email,
    create_user,
    change_confirmed_email,
)
from src.services.email import send_email, send_reset_password_email

router = APIRouter(prefix="/auth", tags=["auth"])

templates = Jinja2Templates(directory="src/templates")


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Register a new user and send confirmation email.

    Args:
        body (UserModel): The user registration data.
        background_tasks (BackgroundTasks): Background task handler.
        request (Request): FastAPI request object.
        db (Session): Database session.

    Raises:
        HTTPException: If user already exists.

    Returns:
        UserResponse: Registered user data.
    """
    exist_user = await get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, str(request.base_url)
    )
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token.

    Args:
        body (OAuth2PasswordRequestForm): Login credentials.
        db (Session): Database session.

    Raises:
        HTTPException: If credentials are invalid.

    Returns:
        TokenModel: Access token and token type.
    """
    user = await get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """Confirm user's email via token.

    Args:
        token (str): Email confirmation token.
        db (Session): Database session.

    Raises:
        HTTPException: If token is invalid or user doesn't exist.

    Returns:
        dict: Confirmation message.
    """
    email = auth_service.get_email_from_token(token)
    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await change_confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Request email confirmation link again.

    Args:
        body (RequestEmail): Email to send confirmation.
        background_tasks (BackgroundTasks): Background task handler.
        request (Request): FastAPI request.
        db (Session): Database session.

    Returns:
        dict: Message about confirmation status.
    """
    user = await get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "Check your email for confirmation."}


@router.post("/forgot-password")
async def forgot_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Request password reset email.

    Args:
        body (RequestEmail): User email.
        background_tasks (BackgroundTasks): Task runner.
        request (Request): FastAPI request.
        db (Session): Database session.

    Returns:
        dict: Password reset message.
    """
    user = await get_user_by_email(body.email, db)
    if user:
        token = auth_service.create_email_token({"sub": user.email})
        reset_link = f"{request.base_url}api/auth/reset-password/{token}"
        background_tasks.add_task(
            send_reset_password_email, user.email, user.username, reset_link
        )
    return {"message": "If the email exists, a password reset link will be sent."}


@router.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_form(token: str, request: Request):
    """Render password reset HTML form.

    Args:
        token (str): Reset token.
        request (Request): FastAPI request.

    Returns:
        TemplateResponse: HTML form.
    """
    return templates.TemplateResponse(
        "reset_password_form.html", {"request": request, "token": token}
    )


@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Submit new password via reset form.

    Args:
        token (str): Reset token.
        password (str): New password.
        db (Session): Database session.

    Raises:
        HTTPException: If token invalid or user not found.

    Returns:
        dict: Password reset success message.
    """
    try:
        email = auth_service.get_email_from_token(token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = auth_service.get_password_hash(password)
    user.password = hashed_password
    db.commit()
    return {"message": "Password reset successful"}
