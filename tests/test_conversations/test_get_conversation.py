import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from app.services.conversation_service import get_conversation


@pytest.mark.asyncio
async def test_get_conversation_returns_user_conversations():
    user_id = uuid4()

    db = Mock()
    db.execute = AsyncMock()

    conversations = [Mock(), Mock()]#list of conversation
    fake_scalars = Mock()
    fake_scalars.all.return_value = conversations
    fake_result = Mock()
    fake_result.scalars.return_value = fake_scalars
    db.execute.return_value = fake_result

    result = await get_conversation(db, user_id)

    db.execute.assert_awaited_once()
    assert result == conversations
    assert fake_scalars.all.called
