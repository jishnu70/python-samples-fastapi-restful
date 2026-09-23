"""
Test cases for the PlayerService.
"""

from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from models.player_model import PlayerRequestModel
from schemas.player_schema import Player
from services.player_service import (
    create_async,
    retrieve_all_async,
    retrieve_by_id_async,
    retrieve_by_squad_number_async,
)
from tests.player_fake import existing_player, nonexistent_player, unknown_player


@pytest.fixture
def existing_player_request_model():
    """
    Fixture for an existing PlayerRequestModel.
    """
    existing_player_data = existing_player()
    return PlayerRequestModel(
        first_name=existing_player_data.first_name
        if existing_player_data.first_name
        else "",
        middle_name=existing_player_data.middle_name,
        last_name=existing_player_data.last_name
        if existing_player_data.last_name
        else "",
        date_of_birth=existing_player_data.date_of_birth,
        squad_number=existing_player_data.squad_number
        if existing_player_data.squad_number
        else 0,
        position=existing_player_data.position if existing_player_data.position else "",
        abbr_position=existing_player_data.abbr_position,
        team=existing_player_data.team,
        league=existing_player_data.league,
        starting11=existing_player_data.starting11,
    )


@pytest.fixture
def existing_player_schema():
    """
    Fixture for an existing Player schema.
    """
    existing_player_data = existing_player()
    return Player(
        id=UUID(existing_player_data.id),
        first_name=existing_player_data.first_name,
        middle_name=existing_player_data.middle_name,
        last_name=existing_player_data.last_name,
        date_of_birth=existing_player_data.date_of_birth,
        squad_number=existing_player_data.squad_number,
        position=existing_player_data.position,
        abbr_position=existing_player_data.abbr_position,
        team=existing_player_data.team,
        league=existing_player_data.league,
        starting11=existing_player_data.starting11,
    )


@pytest.mark.anyio
async def test_create_async_success(existing_player_request_model):
    """
    Test the successful creation of a Player.
    """
    mock_session = AsyncMock(spec=AsyncSession)

    result = await create_async(mock_session, existing_player_request_model)

    assert result is not None
    mock_session.add.assert_called_once_with(result)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.anyio
async def test_create_async_database_error(existing_player_request_model):
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.commit.side_effect = SQLAlchemyError("Connection timeout")

    result = await create_async(mock_session, existing_player_request_model)

    assert result is None
    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_awaited_once()
    mock_session.refresh.assert_not_awaited()


@pytest.mark.anyio
async def test_retrieve_all_async():
    """
    Test the retrieval of all players.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = Mock()
    mock_players = [existing_player(), nonexistent_player(), unknown_player()]
    mock_result.scalars.return_value.all.return_value = mock_players

    mock_session.execute.return_value = mock_result

    result = await retrieve_all_async(mock_session)

    assert result == mock_players
    mock_session.execute.assert_awaited_once()


@pytest.mark.anyio
async def test_retrieve_all_async_empty():
    """
    Test the retrieval of all players when no players exist.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []

    mock_session.execute.return_value = mock_result

    result = await retrieve_all_async(mock_session)

    assert result == []
    mock_session.execute.assert_awaited_once()


@pytest.mark.anyio
async def test_retrieve_by_id_async(existing_player_schema):
    """
    Test the retrieval of a player by ID.
    """
    mock_session = AsyncMock(spec=AsyncSession)

    mock_session.get.return_value = existing_player_schema

    result = await retrieve_by_id_async(mock_session, existing_player_schema.id)  # type: ignore

    assert result == existing_player_schema
    mock_session.get.assert_awaited_once_with(Player, existing_player_schema.id)


@pytest.mark.anyio
async def test_retrieve_by_id_async_not_found():
    """
    Test the retrieval of a player by ID when the player does not exist.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    non_existent_id = UUID("00000000-0000-0000-0000-000000000000")

    mock_session.get.return_value = None

    result = await retrieve_by_id_async(mock_session, non_existent_id)

    assert result is None
    mock_session.get.assert_awaited_once_with(Player, non_existent_id)


@pytest.mark.anyio
async def test_retrieve_by_squad_number_async(existing_player_schema):
    """
    Test the retrieval of a player by Squad Number.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = existing_player_schema

    mock_session.execute.return_value = mock_result

    result = await retrieve_by_squad_number_async(
        mock_session,
        existing_player_schema.squad_number,  # type: ignore
    )

    assert result == existing_player_schema
    mock_session.execute.assert_awaited_once()

@pytest.mark.anyio
async def test_retrieve_by_squad_number_async_not_found():
    """
    Test the retrieval of a player by Squad Number when the player does not exist.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    non_existent_squad_number = 99

    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute.return_value = mock_result

    result = await retrieve_by_squad_number_async(
        mock_session, non_existent_squad_number
    )

    assert result is None
    mock_session.execute.assert_awaited_once()
