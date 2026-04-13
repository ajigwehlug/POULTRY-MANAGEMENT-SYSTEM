from odoo import models, fields, api

class PoultryOperations(models.Model):
    _name = 'poultry.operations'
    _description = 'Daily Poultry Operations'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Operation', compute='_compute_name')
    farm_id = fields.Many2one('poultry.farm', 'Farm', required=True, ondelete='cascade', tracking=True)
    flock_id = fields.Many2one('poultry.flock', 'Flock', required=True, ondelete='cascade', tracking=True)
    
    operation_date = fields.Date('Date', required=True, default=fields.Date.today, tracking=True)
    
    # New: Link to accounting and manufacturing
    journal_entry_id = fields.Many2one('account.move', 'Journal Entry', readonly=True,
                                        help='Auto-created journal entry for costs')
    stock_move_id = fields.Many2one('stock.move', 'Stock Move',
                                     help='For egg collection and product movement')
    work_center_id = fields.Many2one('mrp.workcenter', 'Work Center',
                                      help='Which work center processed this')
    
    # Feed & Water
    feed_consumed_kg = fields.Float('Feed Consumed (kg)', tracking=True)
    feed_cost_per_kg = fields.Float('Feed Cost per kg (₵)', tracking=True)
    feed_cost_total = fields.Float('Total Feed Cost (₵)', compute='_compute_feed_cost')
    water_consumed_liters = fields.Float('Water Consumed (liters)', tracking=True)
    
    # Health
    mortality_count = fields.Integer('Mortality Count', default=0, tracking=True)
    sick_birds = fields.Integer('Sick Birds', tracking=True)
    treatment_notes = fields.Text('Treatment Notes')
    
    # Egg Production (for layers)
    eggs_collected = fields.Integer('Eggs Collected', default=0, tracking=True)
    eggs_damaged = fields.Integer('Damaged Eggs', default=0, tracking=True)
    egg_grade_a = fields.Integer('Grade A Eggs')
    egg_grade_b = fields.Integer('Grade B Eggs')
    
    # Maintenance
    maintenance_done = fields.Boolean('Maintenance Done', default=False)
    cleaning_done = fields.Boolean('Cleaning Done', default=False)
    maintenance_notes = fields.Text('Maintenance Notes')
    
    staff_on_duty = fields.Many2one('res.partner', 'Staff on Duty',
                                     domain=[('is_company', '=', False)],
                                     help='Select staff member from contacts')

    @api.depends('operation_date', 'flock_id')
    def _compute_name(self):
        for op in self:
            if op.flock_id and op.operation_date:
                op.name = f"{op.flock_id.name} - {op.operation_date}"
            else:
                op.name = "Operation"

    @api.depends('feed_consumed_kg', 'feed_cost_per_kg')
    def _compute_feed_cost(self):
        for op in self:
            op.feed_cost_total = op.feed_consumed_kg * op.feed_cost_per_kg

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-create journal entries for costs when operations are logged"""
        records = super().create(vals_list)
        for record in records:
            record._create_journal_entries()
        return records

    def write(self, vals):
        """Update journal entries if costs change"""
        result = super().write(vals)
        for record in self:
            # Delete old entry if costs changed
            if record.journal_entry_id and any(k in vals for k in ['feed_consumed_kg', 'feed_cost_per_kg', 
                                                                      'mortality_count', 'sick_birds']):
                record.journal_entry_id.unlink()
            # Create new entry
            record._create_journal_entries()
        return result

    def _create_journal_entries(self):
        """Create accounting journal entries for operation costs"""
        for op in self:
            if op.feed_consumed_kg or op.mortality_count or op.sick_birds:
                # Calculate total cost
                feed_cost = op.feed_consumed_kg * op.feed_cost_per_kg
                
                if feed_cost > 0:
                    # Create journal entry
                    move_vals = {
                        'move_type': 'entry',
                        'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
                        'date': op.operation_date,
                        'flock_id': op.flock_id.id,
                        'farm_id': op.farm_id.id,
                        'line_ids': [
                            # Debit: Feed Expense
                            (0, 0, {
                                'account_id': self.env['account.account'].search([('code', '=', '7000')], limit=1).id,
                                'debit': feed_cost,
                                'credit': 0,
                                'name': f'Feed for {op.flock_id.name}',
                            }),
                            # Credit: Accounts Payable
                            (0, 0, {
                                'account_id': self.env['account.account'].search([('code', '=', '2000')], limit=1).id,
                                'debit': 0,
                                'credit': feed_cost,
                                'name': f'Feed Payable for {op.flock_id.name}',
                            }),
                        ]
                    }
                    
                    try:
                        entry = self.env['account.move'].create(move_vals)
                        entry.action_post()
                        op.journal_entry_id = entry.id
                    except:
                        pass  # Silently fail if accounts not configured

    def action_view_journal_entry(self):
        """Link to view the journal entry"""
        if self.journal_entry_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Journal Entry',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.journal_entry_id.id,
            }