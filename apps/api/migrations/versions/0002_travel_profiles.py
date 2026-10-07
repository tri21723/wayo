"""Owner-scoped explicit travel preferences."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    namespace = "wayo" if op.get_bind().dialect.name == "postgresql" else None
    op.create_table(
        "travel_profiles",
        sa.Column("owner_id", sa.Uuid(), primary_key=True),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"], [f"{namespace + '.' if namespace else ''}users.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint("revision >= 1", name="ck_profiles_revision"),
        sa.CheckConstraint("schema_version = 1", name="ck_profiles_schema_version"),
        schema=namespace,
    )
    if namespace:
        op.execute("ALTER TABLE wayo.travel_profiles ENABLE ROW LEVEL SECURITY")
        op.execute("REVOKE ALL ON wayo.travel_profiles FROM PUBLIC")


def downgrade():
    namespace = "wayo" if op.get_bind().dialect.name == "postgresql" else None
    op.drop_table("travel_profiles", schema=namespace)
