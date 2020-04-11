# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_renames = {
    'hr_recruitment_stage': [
        ('job_id', None),
    ],
}


def alter_hr_applicant_email_cc_type(cr):
    openupgrade.logged_query(
        cr, """
        ALTER TABLE hr_applicant
        ALTER COLUMN email_cc
        TYPE varchar
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    alter_hr_applicant_email_cc_type(env.cr)
