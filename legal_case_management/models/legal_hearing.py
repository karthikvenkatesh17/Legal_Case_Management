# -*- coding: utf-8 -*-
from odoo import models, fields

class LegalHearing(models.Model):
    _name = 'legal.hearing'
    _description = 'Legal Hearing'
    _rec_name = 'name'
    _order = 'date_start desc'

    case_id = fields.Many2one('legal.case', string='Case', ondelete='cascade', required=True)
    name = fields.Char('Title', required=True)
    date_start = fields.Datetime('Start', required=True)
    date_end = fields.Datetime('End')
    location = fields.Char('Location')
    status = fields.Selection([
        ('planned', 'Planned'),
        ('held', 'Held'),
        ('adjourned', 'Adjourned'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='planned')
    notes = fields.Text('Notes')
