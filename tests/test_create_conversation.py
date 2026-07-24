import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.services.conversation_service import create_conversation


@pytest.mark.asyncio
async def test_create_conversation_success():
    user_id = uuid4()
    title = "Test Conversation"

    db = Mock()
    db.add = Mock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    # The conversation object returned by refresh should be the same object passed to add
    created_conversation = Mock()
    created_conversation.user_id = user_id
    created_conversation.title = title
    db.refresh.return_value = created_conversation

    result = await create_conversation(db, user_id, title)

    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(db.add.call_args.args[0])

    assert result.user_id == user_id
    assert result.title == title
