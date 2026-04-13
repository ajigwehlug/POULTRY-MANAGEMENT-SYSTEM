# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class PoultryFlock(models.Model):
    _name = 'poultry.flock'
    _description = 'Poultry Flock'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Flock ID', required=True, tracking=True)
    farm_id = fields.Many2one('poultry.farm', 'Farm', required=True, ondelete='cascade', tracking=True)
    
    breed = fields.Char('Breed', required=True, help='e.g., ISA Brown, Broiler, Local')
    
    purpose = fields.Selection([
        ('layers', 'Egg Layers'),
        ('broilers', 'Meat Production'),
        ('breeders', 'Breeding Stock'),
        ('mixed', 'Mixed Purpose'),
    ], 'Purpose', required=True, tracking=True)
    
    initial_bird_count = fields.Integer('Initial Birds', required=True, tracking=True)
    bird_count = fields.Integer('Current Birds', compute='_compute_bird_count')
    
    # New: Stock location
    stock_location_id = fields.Many2one('stock.location', 'Farm Location', 
                                         domain=[('farm_id', '!=', False)])
    
    start_date = fields.Date('Start Date', required=True, tracking=True)
    age_in_weeks = fields.Integer('Age (weeks)', compute='_compute_age')
    expected_end_date = fields.Date('Expected End Date', help='For broilers ~8 weeks, layers ~18 months')
    
    status = fields.Selection([
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('terminated', 'Terminated'),
    ], 'Status', default='planning', tracking=True)
    
    # New: Relations to manufacturing (inverse relationships)
    manufacturing_order_ids = fields.One2many('mrp.production', 'flock_id', 'Manufacturing Orders')
    
    operation_ids = fields.One2many('poultry.operations', 'flock_id', 'Daily Operations')
    
    # Computed fields
    total_eggs_produced = fields.Integer('Total Eggs Produced', compute='_compute_statistics')
    total_mortality = fields.Integer('Total Mortality', compute='_compute_statistics')
    total_feed_consumed = fields.Float('Total Feed Consumed (kg)', compute='_compute_statistics')
    total_feed_cost = fields.Float('Total Feed Cost (₵)', compute='_compute_statistics')

    @api.depends('initial_bird_count', 'operation_ids.mortality_count')
    def _compute_bird_count(self):
        for flock in self:
            total_mortality = sum(op.mortality_count for op in flock.operation_ids)
            flock.bird_count = flock.initial_bird_count - total_mortality

    @api.depends('start_date')
    def _compute_age(self):
        for flock in self:
            if flock.start_date:
                delta = fields.Date.today() - flock.start_date
                flock.age_in_weeks = delta.days // 7
            else:
                flock.age_in_weeks = 0

    @api.depends('operation_ids.eggs_collected', 'operation_ids.feed_consumed_kg', 
                 'operation_ids.feed_cost_per_kg', 'operation_ids.mortality_count')
    def _compute_statistics(self):
        for flock in self:
            flock.total_eggs_produced = sum(op.eggs_collected for op in flock.operation_ids)
            flock.total_mortality = sum(op.mortality_count for op in flock.operation_ids)
            flock.total_feed_consumed = sum(op.feed_consumed_kg for op in flock.operation_ids)
            flock.total_feed_cost = sum(op.feed_consumed_kg * op.feed_cost_per_kg 
                                       for op in flock.operation_ids)

    def action_create_manufacturing_order(self):
        """Quick action to create a manufacturing order for this flock"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Manufacturing Order',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'context': {'default_flock_id': self.id},
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-create stock location when flock is created"""
        records = super().create(vals_list)
        for record in records:
            # Create stock location if not provided
            if not record.stock_location_id and record.farm_id:
                location = self.env['stock.location'].create({
                    'name': f'{record.name} Location',
                    'farm_id': record.farm_id.id,
                    'location_id': record.farm_id.location_ids[0].id if record.farm_id.location_ids else None,
                })
                record.stock_location_id = location.id
        return records
