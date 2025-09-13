# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LegalCase(models.Model):
    _name = 'legal.case'
    _description = 'Legal Case'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Reference', required=True, copy=False, default=lambda self: _('New'))
    client_id = fields.Many2one('res.partner', string='Client', domain=[('is_client', '=', True)], required=True, tracking=True)
    responsible_lawyer_id = fields.Many2one('res.partner', string='Responsible Lawyer', domain=[('is_lawyer', '=', True)], tracking=True)
    member_ids = fields.Many2many('res.users', 'legal_case_user_rel', 'case_id', 'user_id', string='Members')
    case_type = fields.Selection([
        ('civil', 'Civil'),
        ('criminal', 'Criminal'),
        ('family', 'Family'),
    ], string='Case Type', default='civil', tracking=True)
    stage = fields.Selection([
        ('intake', 'Intake'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ], string='Stage', default='intake', tracking=True)
    open_date = fields.Date('Open Date', default=fields.Date.context_today)
    close_date = fields.Date('Close Date', copy=False)
    description = fields.Text('Description')
    fixed_fee_amount = fields.Monetary('Fixed Fee')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency', readonly=True)
    hearing_ids = fields.One2many('legal.hearing', 'case_id', string='Hearings')
    hearing_count = fields.Integer(string='Hearings', compute='_compute_hearing_count')
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')

    @api.model
    def create(self, vals):
        # Assign sequence
        if vals.get('name', _('New')) in (False, None, _('New')):
            vals['name'] = self.env['ir.sequence'].next_by_code('legal.case') or _('New')
        return super(LegalCase, self).create(vals)

    def write(self, vals):
        res = super(LegalCase, self).write(vals)
        if 'stage' in vals:
            for rec in self:
                if rec.stage == 'closed' and not rec.close_date:
                    rec.close_date = fields.Date.context_today(rec)
        return res

    def _compute_hearing_count(self):
        for rec in self:
            rec.hearing_count = len(rec.hearing_ids)

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['account.move'].search_count([
                ('legal_case_id', '=', rec.id),
                ('move_type', '=', 'out_invoice')
            ])

    def action_open_hearings(self):
        self.ensure_one()
        return {
            'name': _('Hearings'),
            'type': 'ir.actions.act_window',
            'res_model': 'legal.hearing',
            'view_mode': 'tree,form,calendar',
            'domain': [('case_id', '=', self.id)],
            'context': {'default_case_id': self.id},
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('legal_case_id', '=', self.id), ('move_type', '=', 'out_invoice')],
        }

    def action_create_invoice(self):
        self.ensure_one()
        if not self.client_id:
            raise UserError(_('Please set a client on the case before creating an invoice.'))
        # Prevent multiple invoices for same case (MVP: one invoice per case)
        existing = self.env['account.move'].search([('legal_case_id', '=', self.id), ('move_type', '=', 'out_invoice')], limit=1)
        if existing:
            raise UserError(_('An invoice already exists for this case: %s') % existing.name)
        # Prepare invoice values
        price = self.fixed_fee_amount or 0.0
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.client_id.id,
            'invoice_origin': self.name,
            'legal_case_id': self.id,
            'invoice_line_ids': [],
        }
        # Try to reference or create a product named "Legal Services" if product module exists
        product = None
        try:
            Product = self.env['product.product']
            product = Product.search([('name', '=', 'Legal Services')], limit=1)
            if not product:
                # create a basic product; guard in case product model is not installed
                product = Product.create({'name': 'Legal Services', 'type': 'service'})
        except Exception:
            product = None

        line_vals = {
            'name': 'Legal Services',
            'quantity': 1,
            'price_unit': price,
        }
        if product:
            line_vals['product_id'] = product.id
            try:
                # Set product UoM if available
                if product.uom_id:
                    line_vals['product_uom_id'] = product.uom_id.id
            except Exception:
                pass
        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))
        invoice = self.env['account.move'].create(invoice_vals)
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }
