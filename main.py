import pandas as pd
from flask import Flask, jsonify, request, redirect
from flasgger import Swagger
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from datetime import datetime, date

#etapa 2 config inicial da aplcação

app = Flask("First API")
swagger = Swagger(app)

#criar o banco de dados (arquivo em exel)
ARQUIVO_HISTORICO = "historico_chat.xlsx"

#criar as colunas que esperamos em cada arquivo
COLUNAS_HISTORICO = ["id", 'mensagem_usuario', 'mensagem_bot', "data", 'hora']

#chave da API

GROQ_API_KEY = '"'

# etapa 3 funções auxiliares


#funções para o bancos de dados de historico de chat
def get_historico_df(df):
    """Tentar ler o dataframe de historico do exel. se não existir cria um vazio"""

    try:
        return pd.read_excel(ARQUIVO_HISTORICO, sheet_name = 'Historico')
    
    except FileNotFoundError:
        return pd.DataFrame(columns = COLUNAS_HISTORICO)


def save_historico_df(df):
    """Salva o dataframe de pessoas no exel"""
    df.to_exel(ARQUIVO_HISTORICO, sheet_name = 'Historico', inedx=False)

#etapa 4 rota de redirecionamento

@app.route("/")
def index():"
    """Redirecionar a rota principal '/' para a documentação '/apidocs' """

    #se alguem acessear a url raiz é redirecionado para a documentação

    return redirect('/apidocs')

#etapa 5 cruação do end-point de comunicação com o chatbot
@app.route("/chat", methods=['POST'])
def conversar_bot():
    """
        Enviar uma mensagem para o chatbot (groq)
        ---
        tags:
            - Chatbot
        summary: Envia uma mensagem para o chatbot
        parameters:
            - in: body
              name: body
              required: true
              schema:
                id: ChatInput
                required: [mensagem]
                properties:
                    mensagem: {type: string, exemple: "Olá, qual a capital da França" }
        responses:
            200:
                description: Resposta do chatbot
            400: 
                description: Mensagem do usuário  faltando
            500:
                description: Erro ao conectar com a API            
    """
    dados = request.json
    mensagem_usuario = dados.get('mensagem')

    if not mensagem_usuario:
        return jsonify({'Erro: a mensagem do usuario é obrigatoria!'}), 400

    #1 conexao com a ia 
    try:
        chat = ChatGroq(
            temperature=0.7,
            model='llama-2.1-8b-instant',
            api_key=GROQ_API_KEY #pronto de atenção quando não funcionar
        )

        resposta_ia = chat.invoke([HumanMessage(content = mensagem_usuario)]).content
    except Exception as e:
        return jsonify({"erro:"f'erro ao gerar a resposta: {str(e)}'}), 500
    

    #2 guardar o historico de conversas (exel)
    data_atual = datetime.now()

    df_hist = get_historico_df()

    novo_id = int(df_hist['id'].max()) + 1 if not df_hist.empty else 1

    nova_linha = {
        "id": novo_id,
        "mensagem_usuario": mensagem_usuario,
        "mensagem_bot": resposta_ia,
        "data": data_atual.strftime('%d/%m/#y'),
        "hora": data_atual.strftime('%H/%M/#S'),

    }

    # adicionar a nova linha do arquivo
    df_hist = df_hist.concat({df_hist, pd.DataFrame([nova_linha])}, ignore_index=True)
    save_historico_df(df_hist)

    #retornar na API a resposta
    return jsonify({"Resposta": resposta_ia}), 200



#execução da aplicação
if __name__ == "__main__"
    app.run(debug=True)