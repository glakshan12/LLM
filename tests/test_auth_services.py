import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.auth_services import hash_password, verify_password, register_user, login_user
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserRegister
from app.models.users import User
@patch("app.services.auth_services.password_hashing.hash")
def test_hash_password(mock_hash):
    mock_hash.return_value="fakehash"
    result=hash_password("admin123")
    mock_hash.assert_called_once_with("admin123")
    assert result == "fakehash"

@patch("app.services.auth_services.password_hashing.verify")
def test_verify_correct_password(mock_hash):
    mock_hash.return_value=True
    result=verify_password("admin123", "hello123")
    mock_hash.assert_called_once_with("admin123","hello123")
    assert result is True

@patch("app.services.auth_services.password_hashing.verify")#if need to test real wrong password dont mock it 
def test_verify_wrong_password(mock_hash):
    mock_hash.return_value=False
    result=verify_password("welcome","hell")
    mock_hash.assert_called_once_with("welcome","hell")
    assert result is False




@pytest.mark.asyncio
async def test_register_user_success():
    """Positive case: new email + username → user created"""
    
    # Mock the db.execute() calls and all async calls
    fake_db = AsyncMock(spec=AsyncSession)
    
    # When db.execute(select(User).where is called, return a mock result
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None  # no existing user
    
    #when db.executes is called it returns mock_result
    fake_db.execute.return_value = mock_result
    
    # Create test input
    user_data = UserRegister(
        email="lakshan@test.com",
        username="lakshan",
        password="admin123"
    )
    
    # Call register function
    result = await register_user(user_data, fake_db)
    
    # Assertions
    assert result.email == "lakshan@test.com"
    assert result.username == "lakshan"
    
    fake_db.add.assert_called_once()       
    fake_db.flush.assert_called_once()      
    fake_db.commit.assert_called_once()    
    fake_db.refresh.assert_called_once()    


@pytest.mark.asyncio
async def test_register_email_already_exists():
    
    fake_db = AsyncMock(spec=AsyncSession)
    
    # First execute call (checking email) returns an existing user
    mock_result_email = AsyncMock()
    mock_result_email.scalar_one_or_none.return_value = {"id": 1, "email": "lakshan@test.com"}
    
    fake_db.execute.return_value = mock_result_email
    
    user_data = UserRegister(
        email="lakshan@test.com",
        username="newuser",
        password="admin123"
    )
    
    # Expect HTTPException to be raised
    with pytest.raises(HTTPException) as exc_info:
        await register_user(user_data, fake_db)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in exc_info.value.detail
    
    # Should NOT proceed to add/commit
    fake_db.add.assert_not_called()
    fake_db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_register_username_already_exists():
    fake_db=AsyncMock(spec=AsyncSession)

    mock_result_username=AsyncMock()
    mock_result_username.scalar_one_or_more.return_value={
        "id":2,"username":"lakshan"
    }

    fake_db.execute.return_value=mock_result_username
    
    user_data=UserRegister(
        email="lakshan@gmail.com",
        username="newuser",
        password="admin123"
    )

    with pytest.raises(HTTPException) as exc_info:
        await register_user(user_data,fake_db)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "username already existed" in exc_info.value.detail

    fake_db.add.assert_not_called() 
    fake_db.commit.assert_not_called()



