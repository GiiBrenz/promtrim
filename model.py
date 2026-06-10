import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura a chave de API do Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class Model:
    # Definição dos Prompts Invisíveis de Engenharia de Prompt (Invisible Prompt Engineering)
    PROMPTS = {
        "apenas_codigo": (
            "Você é um gerador de código especialista de nível sênior. Sua tarefa é retornar APENAS "
            "o código de implementação limpo, moderno, extremamente otimizado, seguro e bem comentado "
            "com base na ideia ou problema do usuário.\n\n"
            "REGRAS ESTRITAS:\n"
            "1. NÃO escreva NENHUM texto introdutório ou explicativo (ex: 'Aqui está seu código', 'Claro, eu posso ajudar').\n"
            "2. NÃO escreva NENHUM texto de conclusão, notas finais ou guias de instalação no final.\n"
            "3. O retorno deve conter única e exclusivamente o bloco ou blocos de código formatados com markdown.\n"
            "4. Se houver configurações ou observações indispensáveis, coloque-as como comentários dentro do próprio código.\n"
            "5. Evite dependências desnecessárias; use as melhores práticas de codificação da linguagem especificada."
        ),
        "explicacao": (
            "Você é um Arquiteto de Software sênior especialista em design de sistemas complexos.\n\n"
            "Sua tarefa é fornecer uma explicação teórica, conceitual e arquitetural detalhada sobre o problema proposto.\n\n"
            "REGRAS ESTRITAS:\n"
            "1. Foque na arquitetura do sistema, padrões de projeto aplicáveis (Design Patterns) e conceitos fundamentais.\n"
            "2. Explique os trade-offs envolvidos (prós e contras das abordagens possíveis).\n"
            "3. Analise o impacto em termos de performance, escalabilidade e manutenibilidade.\n"
            "4. Se apropriado, represente o fluxo usando diagramas de texto ASCII ou Mermaid.\n"
            "5. Evite escrever implementações completas de código. Use apenas pequenos trechos conceituais em pseudocódigo ou código se for estritamente necessário para ilustrar um ponto teórico.\n"
            "6. Seja conciso, direto e focado, economizando tokens e eliminando saudações irrelevantes."
        ),
        "bibliotecas": (
            "Você é um especialista em ecossistemas de software e curadoria de tecnologias.\n\n"
            "Sua tarefa é recomendar e comparar de forma crítica as melhores bibliotecas, ferramentas, frameworks "
            "ou serviços para resolver o problema proposto.\n\n"
            "REGRAS ESTRITAS:\n"
            "1. Liste as 2 a 4 principais opções mais consolidadas e modernas do mercado.\n"
            "2. Para cada opção, apresente: Prós, Contras, Casos de Uso ideais, Desempenho e Nível de manutenção ativa (popularidade).\n"
            "3. Faça uma tabela comparativa simples se adequado.\n"
            "4. Finalize com um veredito claro e direto: 'Recomendação PromTrim' baseada no contexto fornecido.\n"
            "5. Vá direto ao assunto, sem conversas introdutórias."
        ),
        "seguranca": (
            "Você é um Engenheiro de Segurança de Aplicações (AppSec) e Analista de Vulnerabilidades sênior.\n\n"
            "Sua tarefa é realizar uma análise crítica e uma revisão minuciosa de segurança sobre a ideia, problema ou snippet proposto.\n\n"
            "REGRAS ESTRITAS:\n"
            "1. Identifique possíveis vulnerabilidades de segurança (ex: OWASP Top 10, injeções, race conditions, concorrência, vazamento de dados ou memória).\n"
            "2. Apresente riscos relacionados a limites de entrada, tratamento incorreto de erros e vazamento de stacktraces.\n"
            "3. Para cada falha em potencial identificada, apresente a descrição do risco e a recomendação de mitigação imediata.\n"
            "4. Forneça o snippet de correção correspondente focando em segurança.\n"
            "5. Não seja prolixo. Seja extremamente cirúrgico e direto para eliminar alucinações e focar apenas no que é risco real."
        )
    }

    @staticmethod
    def gerar_prompt_mestre(ideia_usuario, tipo_resposta):
        """
        Processa a ideia do usuário baseando-se no tipo de resposta escolhido,
        adicionando a Engenharia de Prompts invisível apropriada e fazendo a chamada
        ao modelo Gemini da Google.
        """
        prompt_sistema = Model.PROMPTS.get(tipo_resposta)
        if not prompt_sistema:
            # Fallback seguro caso o tipo não seja reconhecido
            prompt_sistema = "Você é um assistente de IA focado e direto. Ajude o usuário de forma concisa."

        # Se não houver chave de API configurada, retornamos um mock rico com o prompt gerado para fins de depuração/testes
        if not api_key:
            return (
                "⚠️ **[MODO MOCK - SEM GEMINI_API_KEY]**\n\n"
                "Para ativar as respostas reais da IA, configure a variável `GEMINI_API_KEY` no arquivo `.env` na raiz do projeto.\n\n"
                "Aqui está a demonstração do prompt de sistema invisível que seria aplicado no backend:\n\n"
                f"```text\n[PROMPT DE SISTEMA APLICADO]\n{prompt_sistema}\n```\n\n"
                "**Ideia do Usuário Recebida:**\n"
                f"> {ideia_usuario}\n\n"
                f"**Tipo de Resposta Solicitada:** `{tipo_resposta}`\n\n"
                "**Simulação de resposta baseada no perfil selecionado:**\n"
                "Esta é uma resposta fictícia de demonstração. Por favor, insira uma chave de API válida para testar a integração real."
            )

        try:
            # Usando o modelo gemini-2.5-flash padrão pela velocidade e custo-benefício
            # Ajustamos a temperatura de acordo com a precisão exigida pelo modo
            temperatura = 0.2
            if tipo_resposta in ["explicacao", "bibliotecas"]:
                temperatura = 0.4  # Permite um pouco mais de fluidez explicativa

            # Configurando o modelo
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=prompt_sistema
            )

            # Executa a geração com parâmetros otimizados
            response = model.generate_content(
                ideia_usuario,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperatura,
                    max_output_tokens=2048
                )
            )

            return response.text
        except Exception as e:
            return f"❌ Erro ao gerar resposta com a API do Gemini: {str(e)}"
