from alembic import context

from app.database import engine_for
from app.models import Base
from app.settings import get_settings

url = get_settings().database_url
if not url:
    raise RuntimeError("Set WAYO_DATABASE_URL before running migrations.")


def include_name(name, type_, _parent_names):
    # Never let autogenerate propose changes to Supabase-managed auth/storage schemas.
    return name == (None if url.startswith("sqlite:") else "wayo") if type_ == "schema" else True


if context.is_offline_mode():
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        include_schemas=True,
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    with engine_for(url).connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            include_schemas=True,
            include_name=include_name,
        )
        with context.begin_transaction():
            context.run_migrations()
