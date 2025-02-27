odoo.define('payment_with_saldo.payment', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');

    publicWidget.registry.PaymentWithSaldo = publicWidget.Widget.extend({
        selector: 'form.o_payment_form',
        events: {
            'submit': '_onSubmit',
            'change input[name="o_payment_radio"]': '_onPaymentOptionChange',
        },

        start: function () {
            this._super.apply(this, arguments);
            console.log("JavaScript de pago con saldo cargado correctamente.");

            var self = this;
            $(document).ready(function () {
                self._initializePaymentOption();
            });
        },

        _initializePaymentOption: function () {
            var $saldoOption = $('input[type="radio"][value="saldo"]');
            var $paymentOptionIdInput = $('input[name="payment_option_id"]');

            if ($saldoOption.length) {
                // Selecciona per defecte "Pago con saldo"
                $saldoOption.prop('checked', true);
                console.log("Opción de pago con saldo seleccionada por defecto.");

                // Assigna correctament el valor a payment_option_id
                if ($paymentOptionIdInput.length) {
                    $paymentOptionIdInput.val("saldo");
                    console.log("Estableciendo `payment_option_id`: " + $paymentOptionIdInput.val());
                } else {
                    console.error("❌ Campo `payment_option_id` no encontrado en el DOM.");
                }
            } else {
                console.warn("⚠️ No se encontró la opción de pago con saldo.");
            }
        },

        _onPaymentOptionChange: function (event) {
            var selectedOption = $(event.target).val();
            console.log("Método de pago cambiado a: " + selectedOption);

            // Actualitza l'input ocult amb el valor correcte
            var $paymentOptionIdInput = $('input[name="payment_option_id"]');
            if ($paymentOptionIdInput.length) {
                $paymentOptionIdInput.val(selectedOption);
            } else {
                console.error("❌ Campo `payment_option_id` no encontrado en el DOM.");
            }
        },

        _onSubmit: function (event) {
            var $form = $(event.currentTarget);
            var paymentOptionId = $form.find('input[name="payment_option_id"]').val();
            console.log("🛠 Valor de `payment_option_id` en el formulari:", paymentOptionId);

            if (!paymentOptionId) {
                console.error("❌ Error: `payment_option_id` no está definido.");
                alert("Error: `payment_option_id` no está definido.");
                event.preventDefault();
                return;
            }

            console.log("🔄 Enviando solicitud AJAX para procesar el pago con saldo...");

            $.ajax({
                url: $form.attr('action'),
                type: 'POST',
                dataType: 'json',
                data: { payment_option_id: paymentOptionId },
                success: function (response) {
                    if (response.status === 'success') {
                        console.log("✅ Pago realizado con éxito.");
                        window.location.href = response.redirect_url;
                    } else {
                        console.error("❌ Error en el pago: " + response.message);
                        alert("Error en el pago: " + response.message);
                    }
                },
                error: function () {
                    console.error("❌ Hubo un error al procesar el pago.");
                    alert("Hubo un error al procesar el pago.");
                }
            });

            event.preventDefault();
        }
    });

    return publicWidget.registry.PaymentWithSaldo;
});
