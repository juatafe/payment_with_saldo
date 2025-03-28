from odoo import http
from odoo.http import request

class SaleOrderController(http.Controller):
    @http.route(['/order/<int:order_id>'], type='http', auth="public", website=True)
    def order_public_view(self, order_id, **kwargs):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order or not order.exists():
            return request.render("website.404")

        return request.render("sale.sale_order_view", {
            "order": order
        })
