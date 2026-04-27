function toggleDark() {
    document.body.classList.toggle("dark");
}

function buscarTempoReal() {
    let input = document.getElementById("busca").value.toLowerCase();
    let linhas = document.querySelectorAll("table tbody tr");

    linhas.forEach(linha => {
        let nome = linha.children[1].innerText.toLowerCase();

        if (nome.includes(input)) {
            linha.style.display = "";
        } else {
            linha.style.display = "none";
        }
    });
}