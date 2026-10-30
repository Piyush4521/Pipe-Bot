"""audit_safe_retention_and_utc_timestamps

Revision ID: d4d255efae0c
Revises: 88f24fc2264d
Create Date: 2026-10-30 21:12:19.265105

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4d255efae0c'
down_revision: Union[str, None] = '88f24fc2264d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

naming_convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


def upgrade() -> None:
    # 1. Update defects foreign key from CASCADE to RESTRICT in SQLite batch mode
    with op.batch_alter_table('defects', schema=None, naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint('fk_defects_inspection_id_inspections', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_defects_inspection_id_inspections',
            'inspections',
            ['inspection_id'],
            ['id'],
            ondelete='RESTRICT',
        )

    # 2. Add is_archived column with server_default=False to inspections in batch mode
    with op.batch_alter_table('inspections', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'is_archived',
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
                comment='Archival flag preserving inspection records for historical compliance without destroying defect evidence',
            )
        )
        batch_op.create_index(batch_op.f('ix_inspections_is_archived'), ['is_archived'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('inspections', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_inspections_is_archived'))
        batch_op.drop_column('is_archived')

    with op.batch_alter_table('defects', schema=None, naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint('fk_defects_inspection_id_inspections', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_defects_inspection_id_inspections',
            'inspections',
            ['inspection_id'],
            ['id'],
            ondelete='CASCADE',
        )
