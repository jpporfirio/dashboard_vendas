import pandas as pd
import requests
import streamlit as st
import time

def download(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_de_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso', icon= '✅')
    time.sleep(5)
    sucesso.empty()

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())

st.title('DADOS BRUTOS')

dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produto = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Preço do Produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0, 5000))
with st.sidebar.expander('Data da Compra'):
    data = st.date_input('Selecione a Data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Categoria do Produto'):
    categoria = st.multiselect('Selecione a Categoria', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Valor Frete'):
    frete_max = int(dados['Frete'].max())
    frete = st.slider('Selecione o Valor do Frete', 0, frete_max, (0, frete_max))
with st.sidebar.expander('Vendedores'):
    vendedor = st.multiselect('Selecione os Vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da Compra'):
    local_compra = st.multiselect('Selecione o Local', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da Compra'):
    avaliacao = st.slider('Selecione a Avaliação', 0, 5, (0,5))
with st.sidebar.expander('Tipo de Pagamento'):
    pagamento = st.multiselect('Selecione o tipo de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de parcelas'):
    parcela_max = dados['Quantidade de parcelas'].max()
    parcelas = st.slider('Selecione a quantidade de parcelas', 0, parcela_max, (0, parcela_max))

query = '''
Produto in @produto and \
@preco[0] <= Preço <= @preco[1] and \
@data[0] <= `Data da Compra` <= @data[1] and \
`Categoria do Produto` in @categoria and \
@frete[0] <= Frete <= @frete[1] and \
Vendedor in @vendedor and \
`Local da compra` in @local_compra and \
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @pagamento and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva o nome do arquivo')

coluna_1, coluna_2 = st.columns(2)
with coluna_1:
    nome_arquivo = st.text_input('', label_visibility= 'collapsed')
    nome_arquivo += '.csv'
with coluna_2:
    st.download_button('Fazer o Download da tabela', data = download(dados_filtrados), file_name= nome_arquivo,
                       mime= 'text/csv', on_click= mensagem_de_sucesso())
