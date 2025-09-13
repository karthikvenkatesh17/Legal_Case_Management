Legal Case Management (Odoo 18)
================================

This module provides a minimal legal case management application:
- Partners flagged as lawyers and clients
- Cases with hearings and attachments
- Simple fixed-fee invoicing (one invoice per case)
- Case Summary QWeb report

Installation
------------
1. Place this folder in your Odoo addons path.
2. Update Apps list and install 'Legal Case Management'.
3. Load demo data by installing with demo data enabled.

Notes
-----
- The module adds a link from account.move -> legal_case_id to allow invoices to be associated with a case.
- If the 'product' model is available the module will attempt to create a 'Legal Services' product for invoice lines.
