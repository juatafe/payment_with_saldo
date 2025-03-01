from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class PaymentWithSaldoController(http.Controller):

    @http.route('/shop/payment/validate', type='json', auth='public', csrf=False)
    def validate_payment(self, **kwargs):
        _logger.info(f"🔹 [SALDO] Dades rebudes a la petició: {kwargs}")

        order_id = kwargs.get('order_id')
        payment_option_id = kwargs.get('payment_option_id')

        if not order_id:
            _logger.error("❌ [SALDO] `order_id` no rebut!")
            return {'status': 'error', 'message': 'Comanda no vàlida'}

        # Convertir `order_id` i `payment_option_id` a enter per seguretat
        try:
            order_id = int(order_id)
            payment_option_id = int(payment_option_id)  # 📌 Convertim `payment_option_id` a `int`
        except (ValueError, TypeError) as e:
            _logger.error(f"❌ [SALDO] Error en la conversió de valors: {str(e)}")
            return {'status': 'error', 'message': 'ID de comanda o mètode de pagament no vàlid'}

        _logger.info(f"✅ [SALDO] `order_id`: {order_id}, `payment_option_id`: {payment_option_id}")

        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists():
            _logger.error(f"❌ [SALDO] La comanda amb ID {order_id} no existeix!")
            return {'status': 'error', 'message': 'Comanda no trobada'}

        _logger.info(f"✅ [SALDO] La comanda {order_id} s'ha trobat correctament.")

        client = order.partner_id

        # 🛠️ **Diferents accions segons el mètode de pagament**
        if payment_option_id == 20:  # 🔹 Comprovem com a `int`
            _logger.info(f"💰 [SALDO] Pagament amb saldo seleccionat.")

            # **Comprovar saldo**
            _logger.info(f"🔍 [SALDO] Saldo actual del client {client.id}: {client.saldo}€")
            _logger.info(f"🔍 [SALDO] Import total de la comanda: {order.amount_total}€")

            if client.saldo < order.amount_total:
                _logger.warning(f"⚠️ [SALDO] El client {client.id} no té saldo suficient!")
                return {'status': 'error', 'message': 'Saldo insuficient'}

            # **Restar saldo i confirmar comanda**
            new_saldo = client.saldo - order.amount_total
            _logger.info(f"🔹 [SALDO] Descomptant {order.amount_total}€. Nou saldo: {new_saldo}€")

            try:
                client.sudo().write({'saldo': new_saldo})
                _logger.info(f"🔹 [SALDO] Saldo del client {client.id} actualitzat a {new_saldo}€")
                order.sudo().action_confirm()
                order.message_post(body="💰 [SALDO] Pagament realitzat amb saldo.")
                _logger.info(f"✅ [SALDO] Pagament completat correctament per la comanda {order.id}.")

                return {
                    'status': 'success',
                    'message': 'Pagament realitzat correctament!',
                    'redirect_url': f"/my/orders/{order.id}"
                }

            except Exception as e:
                _logger.error(f"❌ [SALDO] Error al processar el pagament: {str(e)}")
                return {'status': 'error', 'message': f'Error en processar el pagament: {str(e)}'}

        else:
            # **Pagament en efectiu o altres mètodes**
            _logger.info(f"💵 [EFECTIU] Pagament amb mètode alternatiu (ID {payment_option_id}). Acceptant com pagat.")
            try:
                order.sudo().action_confirm()
                order.message_post(body="💵 [EFECTIU] Pagament realitzat en efectiu o altra forma de pagament.")
                _logger.info(f"✅ [EFECTIU] Pagament confirmat per la comanda {order.id}.")

                return {
                    'status': 'success',
                    'message': 'Pagament acceptat correctament!',
                    'redirect_url': f"/my/orders/{order.id}"
                }

            except Exception as e:
                _logger.error(f"❌ [EFECTIU] Error al processar el pagament: {str(e)}")
                return {'status': 'error', 'message': f'Error en processar el pagament: {str(e)}'}
