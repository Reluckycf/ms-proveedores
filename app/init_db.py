from app.config import init_db
from app.models.models import create_tables


def create_all_tables() -> None:
    init_db()
    create_tables()


if __name__ == "__main__":
    create_all_tables()
