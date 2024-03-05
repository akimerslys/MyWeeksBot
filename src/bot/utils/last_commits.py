from loguru import logger
from src.core.config import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass


async def get_changelog(num_commits: int = 1) -> list:
    """logger.info(f"generated changelog:")
    commits = list(repo.iter_commits(all=True, max_count=num_commits))
    changelog = []
    for commit in commits:
        changelog.append(f"{commit.authored_datetime.strftime('%d.%m.%Y %H:%M')}, by {commit.author}:\n-{commit.message.strip()}\n\n")
    """
    return []


