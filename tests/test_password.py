import pytest
from unittest.mock import Mock,AsyncMock,patch
from app.services.auth_services import hash_password,verify_password

#hash_password
@patch("app.services.auth_services.password_hashing.hash")
def test_hash_password(mock_hash):

    mock_hash.return_value="hashed_password"
    result=hash_password("password123")#function call
    mock_hash.assert_called_once_with("password123")
    assert result == mock_hash.return_value

#verify password
@patch("app.services.auth_services.password_hashing.verify")
def test_verify_password(mock_hash):

    mock_hash.return_value=True
    result=verify_password("password123","hashed_password")
    assert result is True
    mock_hash.assert_called_once_with("password123","hashed_password")

#wrong password
@patch("app.services.auth_services.password_hashing.verify")
def test_verify_wrong_password(mock_hash):

    mock_hash.return_value=False
    result=verify_password("password123","hashed_password")
    assert result is False
    mock_hash.assert_called_once_with("password123","hashed_password")