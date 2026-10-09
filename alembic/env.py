from logging.config import fileConfig
import os
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from dotenv import load_dotenv

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context


load_dotenv()


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)



DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")


config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%")
)



from src.configs.model import Base

from src.modules.admin.models import Admin
from src.modules.users.models import User


target_metadata = Base.metadata


def run_migrations_offline() -> None:

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:

    connectable = async_engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:

        await connection.run_sync(
            do_run_migrations
        )

    await connectable.dispose()


if context.is_offline_mode():

    run_migrations_offline()

else:

    asyncio.run(
        run_migrations_online()
    )