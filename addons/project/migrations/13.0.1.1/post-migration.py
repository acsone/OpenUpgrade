# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_project_task_company_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE project_task pt
        SET company_id = pp.company_id
        FROM project_project pp
        WHERE pp.id = pt.project_id AND pt.company_id IS NULL
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_project_task_company_id(env.cr)
    openupgrade.load_data(env.cr, 'project', 'migrations/13.0.1.1/noupdate_changes.xml')
