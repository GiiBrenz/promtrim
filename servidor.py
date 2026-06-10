import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from model import Model

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
CORS(app)

@app.route("/")
def home():
    """Serve a página principal (View)"""
    return render_template("index.html")

@app.route('/api/lapidar', methods=['POST'])
def lapidar_resposta():
    """
    Controller API: recebe payload JSON contendo a 'ideia' e o 'tipo' de resposta,
    valida e repassa para a camada Model gerar a resposta otimizada.
    """
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Payload inválido. JSON esperado."}), 400

    ideia_usuario = dados.get('ideia')
    tipo_resposta = dados.get('tipo') # Ex: 'apenas_codigo', 'explicacao', 'bibliotecas', 'seguranca'
    
    # Validação básica de campos obrigatórios
    if not ideia_usuario or not tipo_resposta:
        return jsonify({"erro": "Campos 'ideia' e 'tipo' são obrigatórios"}), 400
        
    # Delegação para a camada Model
    try:
        resposta_final = Model.gerar_prompt_mestre(ideia_usuario, tipo_resposta)
        return jsonify({"resposta": resposta_final})
    except Exception as e:
        return jsonify({"erro": f"Erro interno no servidor: {str(e)}"}), 500

if __name__ == "__main__":
    # O servidor roda localmente na porta 5005 (evitando a porta 5000 que costuma estar em uso no macOS pelo AirPlay Receiver)
    # Permitimos acesso externo para caso o usuário esteja em um ambiente de testes
    app.run(host="0.0.0.0", port=5005, debug=True)
