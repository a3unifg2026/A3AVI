alert("Sistema de RH Interlândia iniciado com sucesso!");
function verificarSeVaiDeletar() {
    var conferir = confirm("Você tem certeza absoluta que deseja apagar ou demitir esse registro?");
    if (conferir == true) {
        return true;
    } else {
        return false;
    }
}
window.onload = function() {
    var listaDeBotoes = document.getElementsByClassName("btn-del");
    for (var i = 0; i < listaDeBotoes.length; i++) {
        listaDeBotoes[i].onclick = verificarSeVaiDeletar;
    }
}