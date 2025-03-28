from odoo import models, fields, exceptions, api, _

class AccountPaymentMethodSaldo(models.Model):
    _inherit = 'account.payment'

    payment_method_line_id = fields.Many2one(
        'account.payment.method.line',
        string="Mètode de pagament",
        required=True,
        default=lambda self: self._get_valid_payment_method()
    )

    def _get_valid_payment_method(self):
        """Retorna un mètode de pagament vàlid (amb Journal)"""
        return self.env['account.payment.method.line'].search(
            [('journal_id', '!=', False)], limit=1
        ).id

    payment_method_type = fields.Selection(
        selection=[('saldo', 'Pago con saldo'), ('cash', 'En metàl·lic')],
        string="Tipus de Mètode de Pagament",
        required=True,
        default='saldo'
    )

    payment_option_id = fields.Many2one(
        'payment.provider',
        string="Opció de pagament",
        help="Mètode de pagament seleccionat"
    )

    def action_post(self):
        for record in self:
            if record.payment_method_type == 'saldo':
                cliente = record.partner_id
                if cliente.saldo < record.amount:
                    raise exceptions.UserError(_('Saldo insuficient per a completar el pagament.'))

                # Descomptar el saldo
                cliente.saldo -= record.amount
                cliente.sudo().write({'saldo': cliente.saldo})

                # Assignar el diari de pagament correctament
                if not record.journal_id:
                    journal_saldo = self.env['account.journal'].search([('code', '=', 'BF')], limit=1)
                    if journal_saldo:
                        record.journal_id = journal_saldo.id
                    else:
                        raise exceptions.UserError(_("No s'ha trobat el diari per a pagament amb saldo."))

                # Assignar el mètode de pagament si no està definit
                if not record.payment_method_line_id:
                    payment_method = self.env['account.payment.method.line'].search(
                        [('journal_id', '=', record.journal_id.id)], limit=1
                    )
                    if payment_method:
                        record.payment_method_line_id = payment_method
                    else:
                        raise exceptions.UserError(_("No s'ha trobat una línia de mètode de pagament vàlida."))

        return super(AccountPaymentMethodSaldo, self).action_post()
