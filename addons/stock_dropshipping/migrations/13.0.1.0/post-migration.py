# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "stock_dropshipping.seq_picking_type_dropship",
            "stock_dropshipping.picking_type_dropship",
            "stock_dropshipping.stock_rule_drop_shipping",
        ]
    )
