"""Private curated catalog with versioned JSON records and embedded evidence."""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    namespace = "wayo" if op.get_bind().dialect.name == "postgresql" else None
    op.create_table(
        "places",
        sa.Column("slug", sa.String(100), primary_key=True),
        sa.Column("destination_id", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("record", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("destination_id = 'da-lat'", name="ck_places_destination"),
        sa.CheckConstraint(
            "status IN ('draft','verified','stale','disabled')", name="ck_places_status"
        ),
        schema=namespace,
    )
    op.create_index(
        "ix_places_destination_status", "places", ["destination_id", "status"], schema=namespace
    )
    if namespace:
        op.execute("ALTER TABLE wayo.places ENABLE ROW LEVEL SECURITY")
        op.execute("REVOKE ALL ON wayo.places FROM PUBLIC")


def downgrade():
    namespace = "wayo" if op.get_bind().dialect.name == "postgresql" else None
    op.drop_table("places", schema=namespace)
