from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PaymentProviderSaldo(models.Model):
    _inherit = 'payment.provider'

    saldo_payment_type = fields.Selection(
        [('saldo', 'Pago con saldo')],
        string="Tipo de Pago con Saldo",
        default='saldo'
    )

    def process_saldo_payment(self, partner_id, amount):
        partner = self.env['res.partner'].browse(partner_id)
        if partner.saldo < amount:
            raise UserError(_('No tienes suficiente saldo para realizar este pago.'))

        partner.saldo -= amount
        partner.sudo().write({'saldo': partner.saldo})
        return {
            'status': 'success',
            'message': _('Pago realizado con éxito mediante saldo.'),
        }
