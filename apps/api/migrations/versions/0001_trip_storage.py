"""Private application users and revisioned trip drafts."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def schema():
    return "wayo" if op.get_bind().dialect.name == "postgresql" else None


def upgrade():
    namespace = schema()
    if namespace:
        op.execute("CREATE SCHEMA wayo")
        op.execute("REVOKE ALL ON SCHEMA wayo FROM PUBLIC")
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False, primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema=namespace,
    )
    op.create_table(
        "trips",
        sa.Column("id", sa.Uuid(), nullable=False, primary_key=True),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("request_id", sa.Uuid(), nullable=False),
        sa.Column("create_hash", sa.String(64), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("trip_data", sa.JSON(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"], [f"{namespace + '.' if namespace else ''}users.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("owner_id", "request_id", name="uq_trips_owner_request"),
        sa.CheckConstraint("revision >= 1", name="ck_trips_revision"),
        schema=namespace,
    )
    op.create_index(
        "ix_trips_owner_updated", "trips", ["owner_id", "updated_at", "id"], schema=namespace
    )
    if namespace:
        # Backend connects as the table-owning role; browser roles get no direct access.
        op.execute("ALTER TABLE wayo.users ENABLE ROW LEVEL SECURITY")
        op.execute("ALTER TABLE wayo.trips ENABLE ROW LEVEL SECURITY")
        op.execute("REVOKE ALL ON ALL TABLES IN SCHEMA wayo FROM PUBLIC")


def downgrade():
    namespace = schema()
    op.drop_table("trips", schema=namespace)
    op.drop_table("users", schema=namespace)
    if namespace:
        op.execute("DROP SCHEMA wayo")
