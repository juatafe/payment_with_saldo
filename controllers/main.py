from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class PaymentWithSaldoController(http.Controller):
    @http.route('/shop/payment/validate', type='http', auth='public', csrf=False)
    def validate_payment(self, **kwargs):
        _logger.info("🔹 [SALDO] Petició rebuda a `/shop/payment/validate`")
        
        # 🛠️ 1️⃣ Comprovem que els paràmetres han arribat correctament
        order_id = kwargs.get('order_id')
        payment_option_id = kwargs.get('payment_option_id')
        _logger.info(f"🔍 [SALDO] order_id: {order_id}, payment_option_id: {payment_option_id}")

        if not order_id:
            _logger.error("❌ [SALDO] El ID de la comanda (`order_id`) no s'ha rebut!")
            return request.redirect('/shop')

        # 🛠️ 2️⃣ Comprovem que la comanda existeix
        order = request.env['sale.order'].sudo().browse(int(order_id))
        if not order.exists():
            _logger.error(f"❌ [SALDO] La comanda amb ID {order_id} no existeix!")
            return request.redirect('/shop')
        
        _logger.info(f"✅ [SALDO] La comanda {order_id} s'ha trobat correctament.")

        # 🛠️ 3️⃣ Comprovem que el mètode de pagament és correcte
        if not payment_option_id or payment_option_id != "saldo":
            _logger.error(f"❌ [SALDO] Mètode de pagament incorrecte! Rebut: {payment_option_id}")
            return request.redirect('/shop')

        _logger.info(f"✅ [SALDO] Mètode de pagament correcte: {payment_option_id}")

        # 🛠️ 4️⃣ Comprovem que el client té saldo suficient
        client = order.partner_id
        _logger.info(f"🔍 [SALDO] Saldo actual del client {client.id}: {client.saldo}€")
        _logger.info(f"🔍 [SALDO] Import total de la comanda: {order.amount_total}€")

        if client.saldo < order.amount_total:
            _logger.warning(f"⚠️ [SALDO] El client {client.id} no té saldo suficient per pagar la comanda {order.id}")
            return request.render('payment_with_saldo.saldo_insufficient', {})

        # 🛠️ 5️⃣ Descomptem el saldo i confirmem la comanda
        new_saldo = client.saldo - order.amount_total
        _logger.info(f"🔹 [SALDO] Descomptant {order.amount_total}€. Nou saldo: {new_saldo}€")

        try:
            client.sudo().write({'saldo': new_saldo})
            _logger.info(f"🔹 [SALDO] Saldo del client {client.id} actualitzat a {new_saldo}€")
            order.sudo().action_confirm()
            _logger.info(f"🔹 [SALDO] Comanda {order.id} confirmada.")
            order.message_post(body="💰 [SALDO] Pagament realitzat correctament mitjançant saldo.")
            _logger.info(f"✅ [SALDO] Pagament completat correctament per la comanda {order.id}.")
        except Exception as e:
            _logger.error(f"❌ [SALDO] Error al processar el pagament: {str(e)}")
            return request.render('payment_with_saldo.payment_error', {'error': str(e)})

        return request.render('payment_with_saldo.payment_success', {})
