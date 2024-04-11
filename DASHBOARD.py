import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(layout= 'wide', page_title= 'DASHBOARD')
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'



st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'

regioes = ['Brasil', 'Centro-Oeste', 'Sudeste', 'Norte', 'Nordeste', 'Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)
query_string = {'regiao':regiao.lower(), 'ano':ano}

response = requests.get(url, params= query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]


#Tabelas Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = (dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']]
                   .merge(receita_estados, left_on= 'Local da compra', right_index= True)
                   .sort_values('Preço', ascending= False))

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending= False)

#Tabelas Vendas
vendas_map = dados.groupby('Local da compra')[['Frete']].count()
vendas_map = (dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']]
                  .merge(vendas_map, left_on= 'Local da compra', right_index= True)
                  .sort_values('Frete', ascending= False))
vendas_map.rename(columns={'Frete': 'Quantidade de Vendas'}, inplace= True)

vendas_mes = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Preço'].count().reset_index()
vendas_mes['Ano'] = vendas_mes['Data da Compra'].dt.year
vendas_mes['Mês'] = vendas_mes['Data da Compra'].dt.month_name()
vendas_mes.rename(columns={'Preço':'Quantidade de Vendas'}, inplace= True)

vendas_categoria = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending= False)
vendas_categoria.rename(columns= {'Preço':'Qauntidade de Vendas'}, inplace= True)


#Tabela Vendedores
vendedores = dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']).reset_index()
vendedores.columns = ['Vendedor', 'Soma', 'Contagem']


#Gráficos Receita
fig_map_receita = px.scatter_geo(receita_estados,
                                 lat= 'lat', lon= 'lon',
                                 scope= 'south america',
                                 size= 'Preço',
                                 template= 'seaborn',
                                 hover_name= 'Local da compra',
                                 hover_data= {'lat': False, 'lon': False},
                                 title= 'Receita Estado',
                                 color_discrete_sequence=['#800080'])

fig_receita_mensal = px.line(receita_mensal,
                         x= 'Mês',
                         y= 'Preço',
                         markers= True,
                         range_y= (0, receita_mensal.max()),
                         color= 'Ano',
                         line_dash= 'Ano',
                         title= 'Receita Mensal',
                         color_discrete_map={'2020': '#800080', '2021': '#4B0082', '2022': '#800080'}
)
fig_receita_mensal.update_layout(yaxis_title= 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto= True,
                             title= 'Top Estados (receita)',
                             color_discrete_sequence=['#800080'])
fig_receita_estados.update_layout(yaxis_title= 'Receita')

fig_receita_categoria = px.bar(receita_categorias,
                               text_auto= True,
                               title= 'Receita por Categoria',
                               color_discrete_sequence=['#800080'])
fig_receita_categoria.update_layout(yaxis_title= 'Receita')


#Gráfico Vendas
fig_qtd_map = px.scatter_geo(vendas_map,
               lat= 'lat', lon= 'lon',
               scope= 'south america',
               size= 'Quantidade de Vendas',
               template='seaborn',
               hover_name='Local da compra',
               hover_data={'lat': False, 'lon': False},
               title='Vendas por Estado',
               color_discrete_sequence=['#800080'])

fig_vendas_mes = px.line(vendas_mes,
                         x= 'Mês',
                         y= 'Quantidade de Vendas',
                          markers= True,
                         color= 'Ano',
                         range_y= (0, vendas_mes.max()),
                         line_dash= 'Ano',
                         title= 'Vendas Mensal',
                         color_discrete_map={'2020': '#4B0082', '2021': '#000080', '2022': '#6A5ACD'})
fig_vendas_mes.update_layout(yaxis_title= 'Quantidade de Vendas')

fig_top_vendas = px.bar(vendas_map.head(),
                        x= 'Local da compra',
                        y= 'Quantidade de Vendas',
                        title= 'Top Estados (Vendas)',
                        text_auto= True,
                        color_discrete_sequence=['#800080'])
fig_top_vendas.update_layout(xaxis_title= 'Local de Compra')

fig_vendas_categoria = px.bar(vendas_categoria,
                              text_auto= True,
                              title= 'Vendas por Categoria',
                              color_discrete_sequence=['#800080'])

##Visualização no st
aba_1, aba_2, aba_3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba_1:
    coluna_1, coluna_2 = st.columns(2)
    with coluna_1:
        st.metric('Receita', formata_numero(sum(dados['Preço'])), 'R$')
        st.plotly_chart(fig_map_receita, use_container_width= True)
        st.plotly_chart(fig_receita_estados, use_container_width= True)
    with coluna_2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width= True)
        st.plotly_chart(fig_receita_categoria, use_container_width= True)

with aba_2:
    coluna_1, coluna_2 = st.columns(2)
    with coluna_1:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qtd_map, use_container_width= True)
        st.plotly_chart(fig_top_vendas, use_container_width= True)

    with coluna_2:
        st.metric('Receita', formata_numero(sum(dados['Preço'])), 'R$')
        st.plotly_chart(fig_vendas_mes, use_container_width= True)
        st.plotly_chart(fig_vendas_categoria, use_container_width= True)

with aba_3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna_1, coluna_2 = st.columns(2)
    with coluna_1:
        st.metric('Receita', formata_numero(sum(dados['Preço'])), 'R$')
        fig_receita_vendedores = px.bar(vendedores.sort_values('Soma', ascending= True).head(qtd_vendedores),
                                        x= 'Soma',
                                        y= 'Vendedor',
                                        text_auto= True,
                                        title= f'Top {qtd_vendedores} vendedores (receita)',
                                        color_discrete_sequence=['#800080'])
        st.plotly_chart(fig_receita_vendedores, use_container_width= True)
    with coluna_2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores.sort_values('Contagem', ascending= True).head(qtd_vendedores),
                                       x= 'Contagem', y= 'Vendedor',
                                       text_auto= True,
                                       title= f'Top {qtd_vendedores} vendedores (vendas)',
                                       color_discrete_sequence=['#800080'])
        st.plotly_chart(fig_vendas_vendedores, use_container_width= True)