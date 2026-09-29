import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    SessionInfoResponse
)
from app.services.storage_service import storage
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_optional,
    get_current_user_required
)

router = APIRouter(tags=['Authentication & Session'])

def build_user_response(user_dict: dict) -> UserResponse:
    return UserResponse(
        id=user_dict['id'],
        username=user_dict['username'],
        email=user_dict['email'],
        full_name=user_dict.get('full_name'),
        created_at=user_dict.get('created_at', '')
    )

@router.post('/register', response_model=TokenResponse)
async def register(req: UserRegisterRequest, response: Response):
    if storage.get_user_by_username(req.username):
        raise HTTPException(status_code=400, detail='Username is already registered')
    if storage.get_user_by_email(req.email):
        raise HTTPException(status_code=400, detail='Email is already registered')
    
    user_id = str(uuid.uuid4())
    user_data = {
        'id': user_id,
        'username': req.username,
        'email': req.email,
        'password_hash': hash_password(req.password),
        'full_name': req.full_name or req.username,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    storage.save_user(user_data)
    token = create_access_token({'sub': user_id, 'username': req.username})
    
    # Set session cookie
    response.set_cookie(
        key='session_token',
        value=token,
        httponly=True,
        max_age=86400 * 7,
        samesite='lax'
    )
    
    return TokenResponse(
        access_token=token,
        token_type='bearer',
        user=build_user_response(user_data)
    )

@router.post('/login', response_model=TokenResponse)
async def login(req: UserLoginRequest, response: Response):
    user = storage.get_user_by_username(req.username)
    if not user:
        user = storage.get_user_by_email(req.username)
        
    if not user or not verify_password(req.password, user.get('password_hash', '')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )
        
    token = create_access_token({'sub': user['id'], 'username': user['username']})
    
    response.set_cookie(
        key='session_token',
        value=token,
        httponly=True,
        max_age=86400 * 7,
        samesite='lax'
    )
    
    return TokenResponse(
        access_token=token,
        token_type='bearer',
        user=build_user_response(user)
    )

@router.post('/token', response_model=TokenResponse)
async def token_endpoint(form_data: OAuth2PasswordRequestForm = Depends()):
    user = storage.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.get('password_hash', '')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password'
        )
    token = create_access_token({'sub': user['id'], 'username': user['username']})
    return TokenResponse(
        access_token=token,
        token_type='bearer',
        user=build_user_response(user)
    )

@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie(key='session_token')
    return {'message': 'Logged out successfully'}

@router.get('/session-info', response_model=SessionInfoResponse)
async def session_info(request: Request):
    user = get_current_user_optional(request)
    if user:
        return SessionInfoResponse(
            authenticated=True,
            user=build_user_response(user),
            session_id=user['id']
        )
    return SessionInfoResponse(authenticated=False, user=None, session_id=None)

@router.get('/session-data')
async def session_data(request: Request):
    user = get_current_user_optional(request)
    if not user:
        return {
            'authenticated': False,
            'preferences': {
                'currency': 'INR',
                'recent_searches': []
            },
            'saved_plans_count': 0
        }
    
    plans = storage.get_history(user_id=user['id'])
    return {
        'authenticated': True,
        'user': build_user_response(user).model_dump(),
        'saved_plans_count': len(plans),
        'preferences': {
            'currency': 'INR',
            'default_city': 'Bengaluru',
            'preferred_sources': ['Amazon', 'IKEA', 'Swiggy', 'Zomato', 'OYO', 'Flipkart']
        },
        'recent_history_preview': [
            {
                'id': p['id'],
                'title': p['title'],
                'planner_type': p['planner_type'],
                'budget': p['budget'],
                'created_at': p['created_at']
            }
            for p in plans[:5]
        ]
    }
