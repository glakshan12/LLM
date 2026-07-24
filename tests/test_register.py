import pytest
from fastapi import HTTPException
from app.schemas.user import UserRegister
from unittest.mock import  AsyncMock,Mock,patch
from app.services.auth_services import register_user
from pydantic import ValidationError

#if own object mock, if imported external library patch it
@pytest.mark.asyncio
@patch("app.services.auth_services.hash_password")
async def test_register_user_success(mock_hash_password):

    user_data = UserRegister(
        email="lakshan@gmail.com",
        username="lakshan",     #userregister and db object
        password="password123"
    )

    db = Mock()

    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    fake_email_result = Mock()
    fake_email_result.scalar_one_or_none.return_value = None

    fake_username_result = Mock()
    fake_username_result.scalar_one_or_none.return_value = None

    db.execute.side_effect = [ #call the db.execute one by one 
        fake_email_result,
        fake_username_result
    ]
    mock_hash_password.return_value = "hashed_password"

#act
    result = await register_user(user_data, db)

#assert
    assert result.email == user_data.email
    assert result.username == user_data.username
    assert result.password == "hashed_password"

    mock_hash_password.assert_called_once_with("password123")

    db.add.assert_called_once()

    saved_user = db.add.call_args.args[0]#return the object that is called when db.add called

    assert saved_user.password == "hashed_password"
    assert saved_user.password != user_data.password #check the user password is not plain password

    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(saved_user)


#email check
@pytest.mark.asyncio
@patch("app.services.auth_services.hash_password")
async def test_register_user_email_exists(user_data):

    user_data = UserRegister(
        email="lakshan@gmail.com",
        username="lakshan",
        password="password123"
    )

    db = Mock()

    db.execute = AsyncMock()

    fake_email_result = Mock()#result of database query

    fake_email_result.scalar_one_or_none.return_value = Mock()

    db.execute.return_value = fake_email_result


#username check
@pytest.mark.asyncio
@patch("app.services.auth_services.hash_password")
async def test_register_username_exists(user_data):

    user_data = UserRegister(
        email="lakshan@gmail.com",
        username="lakshan",
        password="password123"
    )

    db = Mock()

    db.execute = AsyncMock()

    fake_email_result = Mock()#result of database query

    fake_email_result.scalar_one_or_none.return_value = None

    fake_username_result=Mock()

    fake_username_result.scalar_one_or_none.return_value=Mock()

    db.execute.side_effect=[fake_email_result, fake_username_result]

    db.execute.return_value = fake_username_result

@pytest.mark.asyncio
@patch("app.services.auth_services.hash_password")
async def test_register_user_success(mock_hash_password):

    user_data = UserRegister(
        email="lakshan@gmail.com",
        username="lakshan",     #userregister and db object
        password="password123"
    )

    db = Mock()

    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    fake_email_result = Mock()
    fake_email_result.scalar_one_or_none.return_value = None

    fake_username_result = Mock()
    fake_username_result.scalar_one_or_none.return_value = None

    db.execute.side_effect = [ #call the db.execute one by one 
        fake_email_result,
        fake_username_result
    ]
    mock_hash_password.return_value = "hashed_password"


#db error
#user not return here so dont need to check assert
@pytest.mark.asyncio
@patch("app.services.auth_services.hash_password")
async def test_db_not_commit(mock_hash_password):

    user_data = UserRegister(
        email="lakshan@gmail.com",
        username="lakshan",     #userregister and db object
        password="password123"
    )

    db=Mock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.commit.side_effect=Exception("Database Error")
    db.refresh = AsyncMock()

    fake_email_result=Mock()
    fake_email_result.scalar_one_or_none.return_value=None

    fake_username_result=Mock()
    fake_username_result.scalar_one_or_none.return_value=None

    db.execute.side_effect = [ 
        fake_email_result,
        fake_username_result
    ]

    mock_hash_password.return_value="hashed_password"

    with pytest.raises(Exception):
        await register_user(user_data,db)

    db.add.assert_called_once()
    db.flush.assert_awaited_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_not_awaited()