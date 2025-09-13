# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    legal_case_id = fields.Many2one('legal.case', string='Legal Case')
