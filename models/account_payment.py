from odoo import models, fields, exceptions

class AccountPaymentMethodSaldo(models.Model):
    _inherit = 'account.payment'

    payment_method_type = fields.Selection(
        selection=[('saldo', 'Pago con saldo'), ('cash', 'En metálico')],
        string="Tipo de Método de Pago",
        required=True,
        default='saldo'  # Define 'saldo' como valor predeterminado
    )

    def action_post(self):
        for record in self:
            if record.payment_method_type == 'saldo':
                cliente = record.partner_id
                if cliente.saldo < record.amount:
                    raise exceptions.UserError('Saldo insuficiente para completar el pago.')
                # Descontar el saldo
                cliente.saldo -= record.amount
                # Guardar los cambios en la base de datos
                cliente.sudo().write({'saldo': cliente.saldo})
        # Si el saldo es suficiente, ejecuta el proceso normal
        return super(AccountPaymentMethodSaldo, self).action_post()
