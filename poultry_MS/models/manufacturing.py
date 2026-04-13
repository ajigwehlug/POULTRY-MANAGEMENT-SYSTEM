# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMoveInherit(models.Model):
    """Extend Account Move to link with flocks"""
    _inherit = 'account.move'

    flock_id = fields.Many2one('poultry.flock', 'Flock',
                                help='Which flock this cost/revenue is related to')
    farm_id = fields.Many2one('poultry.farm', 'Farm',
                              help='Which farm this cost/revenue is related to')


class MrpProductionInherit(models.Model):
    """Extend MRP Production to link with flocks"""
    _inherit = 'mrp.production'

    flock_id = fields.Many2one('poultry.flock', 'Flock',
                                help='Which flock is being processed in this manufacturing order')
    farm_id = fields.Many2one('poultry.farm', 'Farm', related='flock_id.farm_id', store=True)
    
    # Quality control
    quality_passed = fields.Boolean('Quality Check Passed', default=True)
    quality_notes = fields.Text('Quality Notes')
    
    # Traceability
    batch_number = fields.Char('Batch Number', help='For product traceability')

    def action_generate_batch_number(self):
        """Generate a batch number for traceability"""
        for mo in self:
            if not mo.batch_number:
                # Use date_start instead of date_planned
                date_str = mo.date_start.strftime('%Y%m%d') if mo.date_start else '99999999'
                mo.batch_number = f"BATCH/{mo.flock_id.code if mo.flock_id else 'NA'}/{date_str}"

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-generate batch number and link to flock"""
        records = super().create(vals_list)
        for record in records:
            record.action_generate_batch_number()
        return records


class StockMoveInherit(models.Model):
    """Extend stock moves to track flock origin"""
    _inherit = 'stock.move'

    flock_id = fields.Many2one('poultry.flock', 'Source Flock',
                                help='Which flock originated this stock move')
    farm_id = fields.Many2one('poultry.farm', 'Farm', related='flock_id.farm_id', store=True)


class ProductProductInherit(models.Model):
    """Extend products to mark livestock"""
    _inherit = 'product.product'

    is_livestock = fields.Boolean('Is Livestock', default=False,
                                  help='Check if this is a livestock product')
    livestock_type = fields.Selection([
        ('broiler', 'Broiler Bird'),
        ('layer', 'Layer Bird'),
        ('breeder', 'Breeder Bird'),
        ('egg', 'Egg Product'),
        ('byproduct', 'Byproduct'),
    ], 'Livestock Type', help='Type of livestock/poultry product')


class StockLocationInherit(models.Model):
    """Extend stock locations to link with farms"""
    _inherit = 'stock.location'

    farm_id = fields.Many2one('poultry.farm', 'Farm',
                              help='Which farm this location belongs to')
    location_type = fields.Selection([
        ('broiler_house', 'Broiler House'),
        ('layer_house', 'Layer House'),
        ('slaughterhouse', 'Slaughterhouse'),
        ('processing', 'Processing'),
        ('cold_storage', 'Cold Storage'),
        ('egg_collection', 'Egg Collection'),
        ('egg_sorting', 'Egg Sorting'),
        ('egg_storage', 'Egg Storage'),
        ('packaging', 'Packaging'),
    ], 'Location Type')


class MrpWorkcenterInherit(models.Model):
    """Extend work centers with poultry-specific info"""
    _inherit = 'mrp.workcenter'

    poultry_process = fields.Selection([
        ('slaughter', 'Slaughtering'),
        ('plucking', 'Feather Plucking'),
        ('evisceration', 'Evisceration'),
        ('cutting', 'Meat Cutting'),
        ('packaging', 'Packaging'),
        ('egg_collection', 'Egg Collection'),
        ('egg_washing', 'Egg Washing'),
        ('egg_grading', 'Egg Grading'),
    ], 'Poultry Process')
