# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_lawyer = fields.Boolean('Lawyer', default=False, help='Is this partner a lawyer?')
    is_client = fields.Boolean('Client', default=False, help='Is this partner a client?')
    bar_number = fields.Char('Bar Number')
