odoo.define('payment_with_saldo.payment', function (require) {
    "use strict";
    var globalPaymentOptionId = "saldo";  // Inicialitzada per defecte
    var publicWidget = require('web.public.widget');

    publicWidget.registry.PaymentWithSaldo = publicWidget.Widget.extend({
        selector: 'form.o_payment_form',
        events: {
            'submit': '_onSubmit',
            'change input[name="o_payment_radio"]': '_onPaymentOptionChange',
        },

        start: function () {
            this._super.apply(this, arguments);
            console.log("✅ [SALDO] JavaScript de pago con saldo cargado correctamente.");

            var self = this;
            $(document).ready(function () {
                self._initializePaymentOption();
                self._injectOrderId();  // 🆕 Afegim `order_id` al formulari si no hi és
                self._forceSubmitHandler();
            });
        },

        _initializePaymentOption: function () {
            var $saldoOption = $('input[type="radio"][value="saldo"]');
            var $paymentOptionIdInput = $('input[name="payment_option_id"]');

            if ($saldoOption.length) {
                $saldoOption.prop('checked', true);
                console.log("✅ [SALDO] Opción de pago con saldo seleccionada por defecto.");

                if ($paymentOptionIdInput.length) {
                    $paymentOptionIdInput.val("saldo");
                    globalPaymentOptionId = "saldo";  // Actualitzem la variable global
                    console.log("✅ [SALDO] Estableciendo `payment_option_id`: " + globalPaymentOptionId);
                } else {
                    console.error("❌ [SALDO] Campo `payment_option_id` no encontrado en el DOM.");
                }
            } else {
                console.warn("⚠️ [SALDO] No se encontró la opción de pago con saldo.");
            }
        },


        _injectOrderId: function () {
            // 🔍 Extreure `order_id` de la URL
            let urlParams = new URLSearchParams(window.location.search);
            let orderIdFromUrl = window.location.pathname.match(/\/my\/orders\/(\d+)/);
            let orderId = orderIdFromUrl ? orderIdFromUrl[1] : null;

            console.log("🔍 [SALDO] `order_id` detectat en la URL:", orderId);

            // Si `order_id` existeix, l'afegim com un `input hidden` al formulari
            if (orderId) {
                if ($('input[name="order_id"]').length === 0) {
                    $('form.o_payment_form').append(`<input type="hidden" name="order_id" value="${orderId}"/>`);
                    console.log("✅ [SALDO] `order_id` afegit al formulari:", orderId);
                }
            } else {
                console.error("❌ [SALDO] No s'ha pogut obtenir `order_id` de la URL.");
            }
        },

        _onPaymentOptionChange: function (event) {
            var selectedOption = $(event.target).val();
            console.log("🔄 [SALDO] Método de pago cambiado a: " + selectedOption);

            var $paymentOptionIdInput = $('input[name="payment_option_id"]');
            var $payButton = $('button[name="o_payment_submit_button"]');

            if ($paymentOptionIdInput.length) {
                $paymentOptionIdInput.val(selectedOption);
                globalPaymentOptionId = selectedOption;  // Actualitzem la variable global
                console.log("✅ [SALDO] `payment_option_id` actualizado a: " + globalPaymentOptionId);

                setTimeout(function () {
                    console.log("✅ [SALDO] Habilitant el botó de pagament...");
                    $payButton.prop('disabled', false);
                }, 500);
            } else {
                console.error("❌ [SALDO] Campo `payment_option_id` no encontrado en el DOM.");
            }
        },

        _forceSubmitHandler: function () {
            var self = this;
            var $form = $('form.o_payment_form');
            var $button = $('button[name="o_payment_submit_button"]');

            if ($form.length) {
                console.log("✅ [SALDO] Formulari `.o_payment_form` trobat.");

                // 🔧 Captura el `click` i força el `submit`
                $button.off('click').on('click', function (event) {
                    console.log("🖱️ [SALDO] Click detectat en el botó de pagament.");
                    event.preventDefault();

                    console.log("🔄 [SALDO] Forçant `submit()` manualment...");
                    $form.trigger('submit');
                });

                // 🔧 Comprova que el `submit` ara s'està detectant
                $form.off('submit').on('submit', function (event) {
                    console.log("📩 [SALDO] Event `submit` detectat en `form.o_payment_form`! Executant `_onSubmit()`...");
                    self._onSubmit(event);
                });
            } else {
                console.error("❌ [SALDO] Formulari `.o_payment_form` NO trobat.");
            }
        },

        _onSubmit: function (event) {
            event.preventDefault(); // Evita enviament normal
        
            var $form = $(event.currentTarget);
            var transactionRoute = $form.attr('action');
            var orderId = $form.find('input[name="order_id"]').val();
        
            console.log("🔍 [SALDO] Dades del formulari:");
            console.log("📝 `payment_option_id` (variable global): ", globalPaymentOptionId);
            console.log("📝 `transactionRoute`: ", transactionRoute);
            console.log("📝 `orderId`: ", orderId);
        
            if (!globalPaymentOptionId || !orderId || !transactionRoute) {
                console.error("❌ [SALDO] Error: Falta informació per al pagament.");
                alert("Error: Falta informació per completar el pagament.");
                return;
            }
        
            console.log("📩 [SALDO] Enviant sol·licitud AJAX amb les dades:");
            console.log("➡️ order_id:", orderId);
            console.log("➡️ payment_option_id:", paymentOptionId);
            console.log("➡️ transactionRoute:", transactionRoute);
            
            
            $.ajax({
                url: transactionRoute,
                type: 'POST',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify({
                    order_id: orderId,
                    payment_option_id: globalPaymentOptionId  // Ús de la variable global
                }),
                success: function (response) {
                    console.log("📩 [SALDO] Resposta del servidor:", response);
                    if (response.status === 'success') {
                        console.log("✅ [SALDO] Pagament realitzat correctament! Redirigint...");
                        window.location.href = response.redirect_url;
                    } else {
                        console.error("❌ [SALDO] Error en el pagament: ", response.message);
                        alert("Error en el pagament: " + response.message);
                    }
                },
                error: function (xhr, status, error) {
                    console.error("❌ [SALDO] Error AJAX:", error, xhr.responseText);
                    alert("Error al processar el pagament: " + xhr.responseText);
                }
            });
        },


    });

    return publicWidget.registry.PaymentWithSaldo;
});
