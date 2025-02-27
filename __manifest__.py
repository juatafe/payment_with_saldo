{
    'name': 'Payment with Saldo',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Method of payment that checks client saldo before payment',
    'description': 'Adds a payment method that only processes the payment if the client has enough saldo.',
    'depends': ['payment', 'account', 'saldo_favor'],
    'data': [
    'security/ir.model.access.csv',
    'views/account_payment_view.xml',
    'views/payment_provider_view.xml',
    'views/saldo_insufficient.xml',
    'views/payment_success.xml',
    'views/payment_templates.xml',
    'views/payment_checkout_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_with_saldo/static/src/js/payment_with_saldo.js',
            ],
        },


    'installable': True,
    'application': False,
}
