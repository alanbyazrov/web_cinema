// static/js/phone-mask.js
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация маски для телефона
    function initPhoneMask() {
        // Маска для поля регистрации
        if ($('#id_phone').length) {
            $('#id_phone').inputmask({
                mask: '+7 (999) 999 99 99',
                placeholder: ' ',
                clearMaskOnLostFocus: false,
                showMaskOnHover: false,
                onBeforeMask: function(value, opts) {
                    // Очищаем значение от всего, кроме цифр
                    var processedValue = value.replace(/\D/g, '');

                    // Если начинается с 7 или 8, преобразуем в +7
                    if (processedValue.startsWith('7') && processedValue.length === 11) {
                        processedValue = '+7' + processedValue.substring(1);
                    } else if (processedValue.startsWith('8') && processedValue.length === 11) {
                        processedValue = '+7' + processedValue.substring(1);
                    } else if (processedValue.length === 10) {
                        processedValue = '+7' + processedValue;
                    } else if (!processedValue.startsWith('7')) {
                        processedValue = '+7' + processedValue;
                    }

                    return processedValue;
                }
            });
        }

        // Маска для поля логина
        if ($('#id_username').length) {
            $('#id_username').inputmask({
                mask: '+7 (999) 999 99 99',
                placeholder: ' ',
                clearMaskOnLostFocus: false,
                showMaskOnHover: false,
                onBeforeMask: function(value, opts) {
                    var processedValue = value.replace(/\D/g, '');

                    if (processedValue.startsWith('7') && processedValue.length === 11) {
                        processedValue = '+7' + processedValue.substring(1);
                    } else if (processedValue.startsWith('8') && processedValue.length === 11) {
                        processedValue = '+7' + processedValue.substring(1);
                    } else if (processedValue.length === 10) {
                        processedValue = '+7' + processedValue;
                    } else if (!processedValue.startsWith('7')) {
                        processedValue = '+7' + processedValue;
                    }

                    return processedValue;
                }
            });
        }
    }

    // Запускаем инициализацию
    initPhoneMask();

    // Также обрабатываем динамически добавленные элементы
    $(document).on('focus', '#id_phone, #id_username', function() {
        if (!$(this).data('inputmask')) {
            $(this).inputmask({
                mask: '+7 (999) 999 99 99',
                placeholder: ' ',
                clearMaskOnLostFocus: false
            });
        }
    });
});