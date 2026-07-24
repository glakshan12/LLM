import pytest
from app.services.auth_services import login_user
from app.schemas.user import UserRegister
from unittest.mock import  AsyncMock,Mock,patch
from fastapi import HTTPException


"""successful registeration"""

@pytest.mark.asyncio
@patch("app.services.auth_services.verify_password")
async def test_login_user(mock_verify_password):

#arrange
    db=Mock()
    db.execute=AsyncMock()
    fake_result=Mock() #returned by db
    fake_user=Mock()
    fake_user.email="lakshan@gmail.com"
    fake_user.password="hashed_password"
    fake_user.is_active=True #return user is active
    fake_result.scalar_one_or_none.return_value=fake_user#returned by scalar after check in db
    mock_verify_password.return_value=True
    db.execute.return_value=fake_result #return by db

#act
    result=await login_user(db,"lakshan@gmail.com","password123")

    assert result == fake_user

    db.execute.assert_awaited_once()

    mock_verify_password.assert_called_once_with("password123",fake_user.password)

    assert result.email == fake_user.email

    assert result.is_active is True


"""check email does not exist"""

@pytest.mark.asyncio
@patch("app.services.auth_services.verify_password")
async def test_login_email_not_exist(mock_verify_password):

    db=Mock()
    db.execute=AsyncMock()
    fake_result=Mock()
    fake_result.scalar_one_or_none.return_value=None
    db.execute.return_value=fake_result

    with pytest.raises(HTTPException) as exc:
        await login_user(db,"wrongmail@gmail.com","password123")

    assert exc.value.status_code == 401

    assert exc.value.detail == "Incorrect email or password"

    db.execute.assert_awaited_once()

    mock_verify_password.assert_not_called()


"""test wrong password"""

@pytest.mark.asyncio
@patch("app.services.auth_services.verify_password")
async def test_login_wrong_password(mock_verify_password):
    db=Mock()
    db.execute=AsyncMock()
    fake_result=Mock() #returned by db
    fake_user=Mock()
    fake_user.email="lakshan@gmail.com"
    fake_user.password=Mock()
    fake_result.scalar_one_or_none.return_value=fake_user
    mock_verify_password.return_value = False
    db.execute.return_value=fake_result

    with pytest.raises(HTTPException) as exc:
        await login_user(db,"lakshan@gmail.com","password123")

    assert exc.value.status_code == 401
    
    assert exc.value.detail == "Incorrect email or password"

    db.execute.assert_awaited_once()

    mock_verify_password.assert_called_once_with("password123", fake_user.password)#user password and hash_password


"""user is not active"""

@pytest.mark.asyncio
@patch("app.services.auth_services.verify_password")
async def test_login_account_not_active(mock_verify_password):

#arrange
    db=Mock()
    db.execute=AsyncMock()
    fake_result=Mock() #returned by db
    fake_user=Mock()
    fake_user.email="lakshan@gmail.com"
    fake_user.password="hashed_password"
    fake_user.is_active=False #return user is active
    fake_result.scalar_one_or_none.return_value=fake_user#returned by scalar after check in db
    mock_verify_password.return_value=True
    db.execute.return_value=fake_result #return by db

#act
    with pytest.raises(HTTPException) as exc:
            await login_user(db,"lakshan@gmail.com","password123")
    
    assert exc.value.status_code == 403
        
    assert exc.value.detail == "Account is deactivated"

    db.execute.assert_awaited_once()

    mock_verify_password.assert_called_once_with("password123",fake_user.password)
