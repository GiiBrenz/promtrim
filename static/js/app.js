// Lógica do Painel de Controle de Intenções (PromTrim)

document.addEventListener("DOMContentLoaded", () => {
    // Inicializa os ícones do Lucide
    lucide.createIcons();

    // Seletores DOM
    const intentForm = document.getElementById("intent-form");
    const ideiaTextarea = document.getElementById("ideia");
    const charCountLabel = document.querySelector(".char-count");
    const gerarBtn = document.getElementById("gerar-btn");
    const btnText = gerarBtn.querySelector(".btn-text");
    const btnIcon = gerarBtn.querySelector(".btn-icon");

    const resultadoPainel = document.getElementById("resultado-painel");
    const resultLoader = document.getElementById("result-loader");
    const resultContent = document.getElementById("result-content");
    const resultTitleText = document.getElementById("result-title-text");
    const copyBtn = document.getElementById("copy-btn");

    // Variável para armazenar a resposta bruta para a cópia
    let respostaBruta = "";

    // Mapeamento dos títulos baseados na intenção para melhorar a experiência
    const titulosIntencao = {
        apenas_codigo: "Código Limpo Implementado",
        explicacao: "Análise Teórica & Arquitetura",
        bibliotecas: "Recomendações de Ecossistema",
        seguranca: "Relatório de Segurança & Bugs"
    };

    // Contador de Caracteres no Textarea
    ideiaTextarea.addEventListener("input", () => {
        const count = ideiaTextarea.value.length;
        charCountLabel.textContent = `${count} caractere${count !== 1 ? 's' : ''}`;
    });

    // Envio do formulário
    intentForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const ideia = ideiaTextarea.value.trim();
        // Obtém o valor do radio selecionado
        const tipoRadio = document.querySelector('input[name="tipo"]:checked');
        const tipo = tipoRadio ? tipoRadio.value : "apenas_codigo";

        if (!ideia) return;

        // 1. Alterar o estado do botão de ação
        gerarBtn.disabled = true;
        btnText.textContent = "Lapidando Resposta...";
        btnIcon.innerHTML = `<i data-lucide="loader-2" class="spin-animation"></i>`;
        lucide.createIcons({ attrs: { class: ["spin-animation"] } });

        // 2. Exibir o painel de resultados e ativar o loader
        resultadoPainel.classList.remove("hidden");
        resultLoader.classList.remove("hidden");
        resultContent.classList.add("hidden");
        resultContent.innerHTML = "";
        
        // Ajustar título dinâmico com base na intenção selecionada
        resultTitleText.textContent = titulosIntencao[tipo] || "Resposta Lapidada";

        // Scroll suave até o painel de resultado
        resultadoPainel.scrollIntoView({ behavior: "smooth", block: "start" });

        try {
            // Chamada à API no Flask
            const response = await fetch("/api/lapidar", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ ideia, tipo })
            });

            const dados = await response.get_json ? await response.get_json() : await response.json();

            if (!response.ok) {
                throw new Error(dados.erro || "Falha desconhecida no servidor.");
            }

            respostaBruta = dados.resposta;

            // Renderiza o Markdown de forma segura usando marked
            // Configura para que quebras de linha normais sejam convertidas em <br>
            marked.setOptions({
                breaks: true,
                gfm: true
            });
            
            const htmlRenderizado = marked.parse(respostaBruta);
            resultContent.innerHTML = htmlRenderizado;

            // Executa o syntax highlighting do PrismJS em blocos de código renderizados
            Prism.highlightAllUnder(resultContent);

            // Re-inicializa possíveis ícones criados dinamicamente no markdown
            lucide.createIcons();
            
            // Oculta loader e exibe conteúdo
            resultLoader.classList.add("hidden");
            resultContent.classList.remove("hidden");

        } catch (erro) {
            console.error(erro);
            resultContent.innerHTML = `
                <div class="error-banner">
                    <i data-lucide="alert-triangle"></i>
                    <div>
                        <strong>Erro ao processar requisição:</strong>
                        <p>${erro.message}</p>
                    </div>
                </div>
            `;
            lucide.createIcons();
            resultLoader.classList.add("hidden");
            resultContent.classList.remove("hidden");
        } finally {
            // Restaura estado inicial do botão
            gerarBtn.disabled = false;
            btnText.textContent = "Gerar Resposta Lapidada";
            btnIcon.innerHTML = `<i data-lucide="sparkles"></i>`;
            lucide.createIcons();
        }
    });

    // Copiar resposta para o clipboard
    copyBtn.addEventListener("click", () => {
        if (!respostaBruta) return;

        navigator.clipboard.writeText(respostaBruta).then(() => {
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = `<i data-lucide="check"></i> <span>Copiado!</span>`;
            lucide.createIcons();
            copyBtn.classList.add("btn-success");

            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove("btn-success");
                lucide.createIcons();
            }, 2000);
        }).catch(err => {
            console.error("Erro ao copiar: ", err);
        });
    });
});

// Estilos dinâmicos de animação de rotação via JS se necessário
const styleSheet = document.createElement("style");
styleSheet.innerText = `
    .spin-animation {
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .error-banner {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.2);
        padding: 1.25rem;
        border-radius: var(--radius-md);
        color: hsl(0, 84%, 65%);
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        margin: 1rem 0;
    }
    .error-banner i {
        flex-shrink: 0;
        width: 20px;
        height: 20px;
    }
    .btn-success {
        background: rgba(16, 185, 129, 0.2) !important;
        border-color: hsl(150, 84%, 45%) !important;
        color: hsl(150, 84%, 65%) !important;
    }
`;
document.head.appendChild(styleSheet);
