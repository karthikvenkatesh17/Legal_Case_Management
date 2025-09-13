# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import fields

class TestLegalCase(TransactionCase):

    def setUp(self):
        super(TestLegalCase, self).setUp()
        # Create a lawyer and client
        self.lawyer = self.env['res.partner'].create({'name': 'Test Lawyer', 'is_lawyer': True})
        self.client = self.env['res.partner'].create({'name': 'Test Client', 'is_client': True})
        # Create a user to be a member
        self.user = self.env['res.users'].create({'name': 'Case Member', 'login': 'casemember'})
        # Create a case
        self.case = self.env['legal.case'].create({
            'name': 'New',
            'client_id': self.client.id,
            'responsible_lawyer_id': self.lawyer.id,
            'fixed_fee_amount': 500.0,
        })

    def test_create_hearing_and_invoice(self):
        # Create a hearing
        hearing = self.env['legal.hearing'].create({
            'case_id': self.case.id,
            'name': 'Unit Test Hearing',
            'date_start': fields.Datetime.now(),
        })
        self.assertTrue(hearing.id)

        # Create invoice via button method
        action = self.case.action_create_invoice()
        # Ensure invoice exists
        invoices = self.env['account.move'].search([('legal_case_id','=',self.case.id)])
        self.assertTrue(invoices)
