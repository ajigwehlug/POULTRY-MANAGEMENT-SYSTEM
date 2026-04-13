from odoo import models, fields

class MrpProductionExtend(models.Model):
    _inherit = 'mrp.production'
    
    flock_id = fields.Many2one('poultry.flock', string='Flock', help='Link to poultry flock')
    farm_id = fields.Many2one('poultry.farm', string='Farm', related='flock_id.farm_id', readonly=True)
    batch_number = fields.Char('Batch Number', help='Batch identifier for traceability')
    quality_passed = fields.Boolean('Quality Check Passed', default=False)
    quality_notes = fields.Text('Quality Notes')
