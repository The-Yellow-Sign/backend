
import pytest

from src.infrastructure.db.repositories.sqlalchemy_gitlab_repo import SqlAlchemyGitLabRepository


@pytest.fixture(scope="function")
def gitlab_repo(session):
    """Return SqlAlchemyJobRepository's fixture for tests."""
    return SqlAlchemyGitLabRepository(session)


@pytest.mark.asyncio
async def test_save_config_creates_new(gitlab_repo):
    """Test that service creates new config if it doesn't configured yet."""
    url = "https://gitlab.com"
    token = "encrypted_token_123"

    result = await gitlab_repo.save_config(url, token)

    assert result.id == 1
    assert str(result.url) == url + "/"
    assert result.private_token_encrypted == token

    saved_config = await gitlab_repo.get_config()
    assert saved_config is not None
    assert str(saved_config.url) == url + "/"


@pytest.mark.asyncio
async def test_save_config_updates_existing(gitlab_repo):
    """Test that service updates old config."""
    await gitlab_repo.save_config("https://old.com", "old_token")

    new_url = "https://new-gitlab.com"
    new_token = "new_secret_token"

    result = await gitlab_repo.save_config(new_url, new_token)

    assert result.id == 1 # singleton
    assert str(result.url) == new_url + "/"
    assert result.private_token_encrypted == new_token

    saved_config = await gitlab_repo.get_config()
    assert str(saved_config.url) == new_url + "/"
    assert saved_config.private_token_encrypted == new_token


@pytest.mark.asyncio
async def test_get_config_success(gitlab_repo):
    """Test that service returns created config."""
    url = "https://exist.com"
    await gitlab_repo.save_config(url, "token")

    result = await gitlab_repo.get_config()

    assert result is not None
    assert result.id == 1
    assert str(result.url) == url + "/"


@pytest.mark.asyncio
async def test_get_config_not_found(gitlab_repo):
    """Test that service returns None if config isn't configured yet."""
    result = await gitlab_repo.get_config()
    assert result is None
