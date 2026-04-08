from odoo import models, fields

class Farm(models.Model):
    _name = 'poultry.farm'
    _description = 'Poultry Farm'

    name = fields.Char(string='Farm Name', required=True)
    farm_type = fields.Selection([
        ('small', 'Small Scale'),
        ('medium', 'Medium Scale'),
        ('large', 'Large Scale'),
        ('industrial', 'Industrial'),
    ], string='Farm Type', required=True)
    size = fields.Float(string='Farm Size (hectares)')
    total_capacity = fields.Integer(string='Total Bird Capacity')
    location = fields.Char(string='Location')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    created_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)