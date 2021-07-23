#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create unique index on pid_values."""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e21dab3f9fe'
down_revision = '03965caf4a05'
branch_labels = ()
depends_on = ['999c62899c20']


def upgrade():
    """Upgrade database."""
    op.create_unique_constraint('pidvalue_unique', 'pidstore_pid', ['pid_value'], schema='public')


def downgrade():
    """Downgrade database."""
    pass
