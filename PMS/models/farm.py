# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PoultryFarm(models.Model):
    _name = 'poultry.farm'
    _description = 'Poultry Farm'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Farm Name', required=True, tracking=True)
    code = fields.Char('Farm Code', required=True, tracking=True)
    
    # Changed from String to Many2One (Contacts)
    manager_id = fields.Many2one('res.partner', 'Farm Manager', required=True, 
                                  domain=[('is_company', '=', False)], tracking=True,
                                  help="Select a contact to be the farm manager")
    main_contact_id = fields.Many2one('res.partner', 'Main Contact', 
                                       domain=[('is_company', '=', False)], tracking=True)
    
    scale = fields.Selection([
        ('small', 'Small Scale (< 2,000 birds)'),
        ('medium', 'Medium Scale (2,000 - 10,000 birds)'),
        ('large', 'Large Scale (> 10,000 birds)'),
    ], 'Farm Scale', required=True, tracking=True)
    
    location = fields.Char('Location', required=True, tracking=True)
    region = fields.Char('Region')
    
    # New: Link to stock location
    location_ids = fields.One2many('stock.location', 'farm_id', 'Farm Locations')
    
    total_capacity = fields.Integer('Total Capacity (Birds)', required=True, tracking=True)
    current_bird_count = fields.Integer('Current Bird Count', compute='_compute_bird_count')
    
    is_active = fields.Boolean('Is Active', default=True, tracking=True)
    
    # Relations
    flock_ids = fields.One2many('poultry.flock', 'farm_id', 'Flocks')
    operation_ids = fields.One2many('poultry.operations', 'farm_id', 'Operations')

    @api.depends('flock_ids.initial_bird_count', 'flock_ids.status')
    def _compute_bird_count(self):
        for farm in self:
            farm.current_bird_count = sum(flock.bird_count for flock in farm.flock_ids if flock.status == 'active')

    def action_view_flocks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Flocks',
            'res_model': 'poultry.flock',
            'view_mode': 'tree,form',
            'domain': [('farm_id', '=', self.id)],
        }

    def action_view_operations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Operations',
            'res_model': 'poultry.operations',
            'view_mode': 'tree,form',
            'domain': [('farm_id', '=', self.id)],
        }
