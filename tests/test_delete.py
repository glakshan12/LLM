import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.services.auth_services import delete_account

#for succesful user delete
@pytest.mark.asyncio
async def test_delete_account_success():
    user_id = uuid4()#user id

    db = Mock()
    db.execute = AsyncMock()
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    fake_result = Mock()#return by db.execute
    fake_user = Mock()
    fake_result.scalar_one_or_none.return_value = fake_user
    db.execute.return_value = fake_result

    await delete_account(db, user_id)

    db.execute.assert_awaited_once()
    db.delete.assert_awaited_once_with(fake_user)
    db.commit.assert_awaited_once()


#for user not found
@pytest.mark.asyncio
async def test_delete_account_user_not_found():
    user_id = uuid4()#user id

    db = Mock()
    db.execute = AsyncMock()
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    fake_result = Mock()
    fake_result.scalar_one_or_none.return_value = None
    db.execute.return_value = fake_result

    with pytest.raises(Exception):
        await delete_account(db, user_id)

    db.execute.assert_awaited_once()
    db.delete.assert_not_awaited()
    db.commit.assert_not_awaited()
