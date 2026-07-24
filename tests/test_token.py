from unittest.mock import patch

from app.config import settings
from app.services.auth_services import create_access_token


@patch("app.services.auth_services.jwt.encode")
def test_create_access_token(mock_encode):
    mock_encode.return_value = "fake.jwt.token"

    data = {"sub": "user@example.com"}
    token = create_access_token(data)

    assert token == "fake.jwt.token"
    mock_encode.assert_called_once()

    payload, secret = mock_encode.call_args.args[:2]
    assert payload["sub"] == "user@example.com"
    assert "exp" in payload
    assert secret == settings.SECRET_KEY
    assert mock_encode.call_args.kwargs["algorithm"] == settings.ALGORITHM
