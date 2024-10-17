# -*- coding: utf-8 -*-
{
    'name': "customer_credit_limit",

    'summary': "The module facilitates putting spending limits for the customers",

    'description': """
This module facilitates putting spending limits for the customers and the specified manager can approve or reject the credit limit exceed request 
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_partner_views.xml',
        'wizard/credit_limit_popup_views.xml',
        'views/credit_limit_exceed_email_template.xml',
        'views/approve_rqst_views.xml',
        'views/rejection_template.xml',
        'views/approval_template.xml',
    ],
    "application": True,
    "sequence": -190,

}

