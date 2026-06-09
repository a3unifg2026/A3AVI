/* ===== TEMA ESCURO ===== */
(function() {
    var saved = localStorage.getItem('theme');
    if (saved === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
})();

function toggleTheme() {
    var html = document.documentElement;
    var current = html.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeButton(next);
}

function updateThemeButton(theme) {
    var icon = document.getElementById('theme-icon');
    var text = document.getElementById('theme-text');
    if (icon && text) {
        icon.textContent = theme === 'dark' ? '\u2600' : '\u263D';
        text.textContent = theme === 'dark' ? 'Tema Claro' : 'Tema Escuro';
    }
}

/* ===== CONFIRMACAO DE ACOES ===== */
function confirmarAcao(mensagem) {
    return confirm(mensagem || 'Tem certeza que deseja realizar esta acao?');
}

function confirmarExclusao(nome) {
    return confirm('ATENÇÃO: Esta ação é IRREVERSÍVEL!\n\nVocê está prestes a excluir permanentemente o funcionário "' + nome + '" do sistema.\n\nTodos os dados serão perdidos. Deseja continuar?');
}

/* ===== MASCARA DE TELEFONE ===== */
function mascaraTelefone(input) {
    var valor = input.value.replace(/\D/g, '');
    if (valor.length > 11) valor = valor.substring(0, 11);
    if (valor.length > 6) {
        input.value = '(' + valor.substring(0, 2) + ') ' + valor.substring(2, 7) + '-' + valor.substring(7);
    } else if (valor.length > 2) {
        input.value = '(' + valor.substring(0, 2) + ') ' + valor.substring(2);
    } else if (valor.length > 0) {
        input.value = '(' + valor;
    }
}

/* ===== MASCARA DE SALARIO ===== */
function mascaraSalario(input) {
    var valor = input.value.replace(/[^\d,\.]/g, '');
    valor = valor.replace('.', ',');
    var partes = valor.split(',');
    if (partes.length > 2) {
        valor = partes[0] + ',' + partes.slice(1).join('');
    }
    if (partes[1] && partes[1].length > 2) {
        valor = partes[0] + ',' + partes[1].substring(0, 2);
    }
    input.value = valor;
}

/* ===== VALIDACAO DE FORMULARIO ===== */
function validarFormulario(form) {
    var valido = true;

    var nome = form.querySelector('#nome');
    if (nome && nome.value.trim().length < 3) {
        mostrarErro('erro-nome');
        valido = false;
    } else {
        esconderErro('erro-nome');
    }

    var contato = form.querySelector('#contato');
    if (contato) {
        var tel = contato.value.replace(/\D/g, '');
        if (tel.length < 10 || tel.length > 11) {
            mostrarErro('erro-contato');
            valido = false;
        } else {
            esconderErro('erro-contato');
        }
    }

    var email = form.querySelector('#email');
    if (email) {
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value)) {
            mostrarErro('erro-email');
            valido = false;
        } else {
            esconderErro('erro-email');
        }
    }

    var salario = form.querySelector('#salario');
    if (salario) {
        var salarioNum = salario.value.replace(',', '.');
        if (isNaN(parseFloat(salarioNum)) || parseFloat(salarioNum) <= 0) {
            mostrarErro('erro-salario');
            valido = false;
        } else {
            esconderErro('erro-salario');
            salario.value = salarioNum;
        }
    }

    return valido;
}

function mostrarErro(id) {
    var el = document.getElementById(id);
    if (el) el.classList.add('visible');
}

function esconderErro(id) {
    var el = document.getElementById(id);
    if (el) el.classList.remove('visible');
}

/* ===== INICIALIZACAO ===== */
document.addEventListener('DOMContentLoaded', function() {
    var theme = localStorage.getItem('theme') || 'light';
    updateThemeButton(theme);

    /* Mascara de telefone */
    var telefoneInputs = document.querySelectorAll('input[type="tel"]');
    telefoneInputs.forEach(function(input) {
        input.addEventListener('input', function() { mascaraTelefone(this); });
    });

    /* Mascara de salario */
    var salarioInput = document.getElementById('salario');
    if (salarioInput) {
        salarioInput.addEventListener('input', function() { mascaraSalario(this); });
    }

    /* Validacao no submit */
    var formCadastro = document.getElementById('formCadastro');
    if (formCadastro) {
        formCadastro.addEventListener('submit', function(e) {
            if (!validarFormulario(this)) {
                e.preventDefault();
            }
        });
    }

    var formEdicao = document.getElementById('formEdicao');
    if (formEdicao) {
        formEdicao.addEventListener('submit', function(e) {
            if (!validarFormulario(this)) {
                e.preventDefault();
            }
        });
    }

    /* Flash messages auto-dismiss */
    var flashes = document.querySelectorAll('.flash-message');
    flashes.forEach(function(el) {
        setTimeout(function() {
            el.style.opacity = '0';
            el.style.transform = 'translateY(-8px)';
            setTimeout(function() { el.remove(); }, 300);
        }, 5000);
    });

    /* Esconder erros ao digitar */
    var inputs = document.querySelectorAll('input');
    inputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var erroId = 'erro-' + this.id;
            esconderErro(erroId);
            this.classList.remove('input-error');
        });
    });
});
