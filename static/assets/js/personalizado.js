document.addEventListener('DOMContentLoaded', () => {
    console.log('Script carregado e executado');

    // Função para formatar campos de entrada
    function formatField(inputElement, format) {
        if (inputElement) {
            inputElement.addEventListener('input', function () {
                let value = this.value.replace(/\D/g, '');
                let formattedValue = '';

                for (let i = 0; i < format.length && value.length > 0; i++) {
                    if (format[i] === '#') {
                        formattedValue += value[0];
                        value = value.slice(1);
                    } else {
                        formattedValue += format[i];
                    }
                }

                this.value = formattedValue;
            });
        }
    }

    // Usando a função formatField para formatar os campos
    formatField(document.getElementById('cep'), '#####-####');
    formatField(document.getElementById('id_cep'), '#####-####');
    formatField(document.getElementById('id_telefone'), '(##) #####-####');

    // ==========================
    // Correção para alertas
    // ==========================
    document.querySelectorAll('#msg-container .alert').forEach(alertEl => {
        const pb = alertEl.querySelector('.progress-bar');

        if (pb) {
            // Se tiver barra de progresso, usar a duração dela
            const css = getComputedStyle(pb).animationDuration;
            let ms = 0;

            if (css.endsWith('ms')) {
                ms = parseFloat(css);
            } else if (css.endsWith('s')) {
                ms = parseFloat(css) * 1000;
            }

            if (ms > 0) {
                setTimeout(() => {
                    // Primeiro adiciona classe fade
                    alertEl.classList.add('fade');

                    // Depois de um pequeno tempo, remove o alerta
                    setTimeout(() => {
                        alertEl.remove();
                    }, 500); // 500ms para dar tempo do fade funcionar
                }, ms);
            }
        } else {
            // Se NÃO tiver barra de progresso, usa 2 segundos e faz fade
            setTimeout(() => {
                alertEl.classList.add('fade');
                setTimeout(() => {
                    alertEl.remove();
                }, 500); 
            }, 2000);
        }
    });


    // Função para mudar a cor de fundo de um elemento
    function changeBackgroundColor(elementId, color, duration) {
        const element = document.getElementById(elementId);
        if (element) {
            setTimeout(() => {
                element.style.backgroundColor = color;
            }, duration);
        }
    }

    // Chamando a função para mudar a cor de fundo
    changeBackgroundColor('elementoId', 'lightblue', 3000);

    // Ajuste de altura para os textareas
    const textareas = document.querySelectorAll("textarea.form-control");

    function adjustTextareaHeights() {
        textareas.forEach(textarea => {
            textarea.style.height = "auto"; 
        });

        let maxHeight = 0;
        textareas.forEach(textarea => {
            maxHeight = Math.max(maxHeight, textarea.scrollHeight);
        });

        textareas.forEach(textarea => {
            textarea.style.height = maxHeight + "px"; 
        });
    }

    textareas.forEach(textarea => {
        textarea.addEventListener("input", adjustTextareaHeights);
    });

    adjustTextareaHeights();

    // ==============================
    // Fim das correções
    // ==============================

});
