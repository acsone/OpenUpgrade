# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def run_dropshipping_functions(env):
    # we nullify the company of the dropship sequence, picking_type, and rule
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_sequence seq
        SET company_id = NULL
        FROM ir_model_data imd
        WHERE imd.res_id = seq.id AND imd.module = 'stock_dropshipping'
            AND imd.name = 'seq_picking_type_dropship'"""
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_picking_type spt
        SET company_id = NULL
        FROM ir_model_data imd
        WHERE imd.res_id = spt.id AND imd.module = 'stock_dropshipping'
            AND imd.name = 'picking_type_dropship'"""
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_rule sr
        SET company_id = NULL
        FROM ir_model_data imd
        WHERE imd.res_id = sr.id AND imd.module = 'stock_dropshipping'
            AND imd.name = 'stock_rule_drop_shipping'"""
    )

    # force execute this functions (they are noupdate=1 in xml data)
    env['res.company'].create_missing_dropship_sequence()
    env['res.company'].create_missing_dropship_picking_type()
    env['res.company'].create_missing_dropship_rule()

    # xml_id = stock_dropshipping.seq_picking_type_dropship
    model = "ir.sequence"
    conditions = {
        'seq_picking_type_dropship': "WHERE xml_tab2.code = 'stock.dropshipping'",
    }
    affected_models = {
        'stock.picking.type': ['sequence_id'],
    }
    redirect_affected_models(env, model, affected_models, conditions)

    # xml_id = stock_dropshipping.picking_type_dropship
    model = "stock.picking.type"
    conditions = {
        'picking_type_dropship': "WHERE xml_tab2.sequence_code = 'DS'",
    }
    affected_models = {
        'stock.picking.type': ['return_picking_type_id'],
        'stock.picking': ['picking_type_id'],
        'stock.rule': ['picking_type_id'],
        'stock.warehouse': ['pick_type_id', 'pack_type_id',
                            'out_type_id', 'in_type_id', 'int_type_id'],
    }
    redirect_affected_models(env, model, affected_models, conditions)

    # xml_id = stock_dropshipping.stock_rule_drop_shipping
    model = "stock.rule"
    conditions = {
        'stock_rule_drop_shipping': "JOIN stock_picking_type spt ON xml_tab2.picking_type_id = spt.id "
                                    "WHERE spt.sequence_code = 'DS'",
    }
    affected_models = {
        'stock.move': ['rule_id'],
        'stock.warehouse': ['mto_pull_id'],
    }
    redirect_affected_models(env, model, affected_models, conditions)


def redirect_affected_models(env, xmlid_model, affected_models, conditions):
    xmlid_table = env[xmlid_model]._table
    for model, fields in affected_models.items():
        table = env[model]._table
        for field in fields:
            for xmlid_name, condition in conditions.items():
                openupgrade.logged_query(
                    env.cr, """
        UPDATE {table} tab
        SET {field} = (
            SELECT xml_tab2.id
            FROM {xmlid_table} xml_tab2
            LEFT JOIN ir_model_data imd2 ON (
                imd2.module = 'stock_dropshipping' AND
                imd2.model = '{xmlid_model}' AND imd2.res_id = xml_tab2.id)
            LEFT JOIN res_users ru2 ON ru2.id = xml_tab2.create_uid
            {condition}
                AND imd2.name IS NULL AND
                COALESCE(xml_tab2.company_id, ru2.company_id) =
                    COALESCE(tab.company_id, ru.company_id)
            LIMIT 1
            )
        FROM {xmlid_table} xml_tab
        JOIN ir_model_data imd ON (imd.module = 'stock_dropshipping' AND
            imd.model = 'xmlid_model' AND imd.res_id = xml_tab.id)
        LEFT JOIN res_users ru ON xml_tab.create_uid = ru.id
        WHERE tab.{field} = xml_tab.id AND
            imd.name = '{xmlid_name}'
                    """.format(table=table, field=field,
                               xmlid_table=xmlid_table, xmlid_model=xmlid_model,
                               xmlid_name=xmlid_name, condition=condition)
                )


@openupgrade.migrate()
def migrate(env, version):
    run_dropshipping_functions(env)
    # openupgrade.delete_records_safely_by_xml_id(
    #     env, [
    #         "stock_dropshipping.stock_rule_drop_shipping",
    #         "stock_dropshipping.picking_type_dropship",
    #         "stock_dropshipping.seq_picking_type_dropship",
    #     ]
    # )
    env["ir.model.data"].search([
        ("module", "=", "stock_dropshipping"),
        ("name", "IN", ("seq_picking_type_dropship",
                        "picking_type_dropship", "stock_rule_drop_shipping")),
    ]).unlink()
