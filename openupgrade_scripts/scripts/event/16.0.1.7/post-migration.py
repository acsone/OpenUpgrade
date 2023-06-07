# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_column_drops = [
    ("event_event", "seats_available"),
    ("event_event", "seats_reserved"),
    ("event_event", "seats_unconfirmed"),
    ("event_event", "seats_used"),
    ("event_event_ticket", "seats_available"),
    ("event_event_ticket", "seats_reserved"),
    ("event_event_ticket", "seats_unconfirmed"),
    ("event_event_ticket", "seats_used"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.drop_columns(env.cr, _column_drops)
