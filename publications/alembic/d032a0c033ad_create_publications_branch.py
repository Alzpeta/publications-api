#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create publications branch."""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd032a0c033ad'
down_revision = None
branch_labels = ('publications-alembic',)
depends_on = None


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
