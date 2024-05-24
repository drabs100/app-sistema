import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide")

# Adicionar logo no topo da sidebar
st.sidebar.image("logo1.png", use_column_width=False, width=200)

# Adicionar o file uploader
uploaded_file = st.sidebar.file_uploader("Arraste e solte um arquivo Excel aqui", type="xlsx")

if uploaded_file is not None:
    # Carregar o arquivo Excel
    df = pd.read_excel(uploaded_file)

    # Adicionar filtros na barra lateral
    st.sidebar.header('Filtros')

    # Filtro por sexo
    sexo_options = ['TODOS'] + df['SEXO'].dropna().unique().tolist()
    sexo_selected = st.sidebar.selectbox('Sexo', sexo_options)

    # Filtro por faixa etária com ordem específica
    faixa_etaria_options = ['TODOS', '16 - 21', '22 - 34', '35 - 50', '51 - 61', 'MAIS 62']
    faixa_etaria_selected = st.sidebar.selectbox('Faixa Etária', faixa_etaria_options)

    # Filtro por bairro em ordem alfabética
    bairro_options = ['TODOS'] + sorted(df['BAIRRO'].dropna().unique().tolist())
    bairro_selected = st.sidebar.selectbox('Bairro', bairro_options)

    # Aplicar filtros
    if sexo_selected != 'TODOS':
        df = df[df['SEXO'] == sexo_selected]

    if faixa_etaria_selected != 'TODOS':
        df = df[df['FAIXA_ETARIA'] == faixa_etaria_selected]

    if bairro_selected != 'TODOS':
        df = df[df['BAIRRO'] == bairro_selected]

    # Função para criar gráficos de barras empilhadas
    def create_stacked_bar_chart(source_col, target_col, title):
        df_grouped = df.groupby([target_col, source_col]).size().reset_index(name='counts')
        df_pivot = df_grouped.pivot(index=target_col, columns=source_col, values='counts').fillna(0)

        fig = px.bar(df_pivot, barmode='stack', title=title)
        fig.update_layout(title_text=title, xaxis_title=target_col, yaxis_title='Contagem de Votos', legend_title=source_col, height=600)
        
        return fig

    # Criar gráficos
    def create_figures():
        figures = {}
        z_critical = 1.96  # Definindo o valor crítico para o intervalo de confiança de 95%

        # Gráfico de Intenção de Votos - Pesquisa Espontânea
        fig_espontanea = go.Figure()
        espontanea_data = df["ESPONTANEA"]
        espontanea_counts = espontanea_data.value_counts()
        total_votos = espontanea_counts.sum()
        espontanea_percentages = (espontanea_counts / total_votos) * 100
        if 'NÃO SABE' in espontanea_percentages.index:
            espontanea_percentages = espontanea_percentages.reindex(index=espontanea_percentages.index.drop('NÃO SABE').tolist() + ['NÃO SABE'])
        cores = px.colors.qualitative.Plotly
        for i, (categoria, porcentagem) in enumerate(zip(espontanea_percentages.index, espontanea_percentages)):
            cor = cores[i % len(cores)]
            fig_espontanea.add_trace(go.Bar(x=[categoria], y=[porcentagem], marker_color=cor, showlegend=False))
            fig_espontanea.add_annotation(x=i, y=porcentagem + 0.5, text=f'{porcentagem:.0f}%', showarrow=False, xanchor='center', yanchor='bottom')
        fig_espontanea.update_layout(title='INTENÇÃO DE VOTOS - PESQUISA ESPONTÂNEA', title_x=0.5, xaxis_title='Candidatos', yaxis_title='Porcentagem (%)', xaxis_tickangle=-45, bargap=0.1, height=500, margin=dict(l=50, r=50, t=50, b=50), title_xanchor='center')
        figures['Intenção de Votos - Pesquisa Espontânea'] = fig_espontanea

        # Gráfico de Intenção de Votos - Pesquisa Estimulada
        fig_estimulada = go.Figure()
        estimulada_data = df["ESTIMULADA"]
        estimulada_counts = estimulada_data.value_counts()
        estimulada_percentages = (estimulada_counts / estimulada_counts.sum()) * 100
        if 'INDECISO' in estimulada_percentages.index or 'NENHUM' in estimulada_percentages.index:
            estimulada_percentages = estimulada_percentages.reindex(index=[i for i in estimulada_percentages.index if i not in ['INDECISO', 'NENHUM']] + [i for i in ['INDECISO', 'NENHUM'] if i in estimulada_percentages.index])
        for i, (categoria, percentagem) in enumerate(zip(estimulada_percentages.index, estimulada_percentages.values)):
            cor = cores[i % len(cores)]
            fig_estimulada.add_trace(go.Bar(x=[categoria], y=[percentagem], marker_color=cor, showlegend=False))
            fig_estimulada.add_annotation(x=i, y=percentagem + 0.1, text=f'<b>{percentagem:.0f}%</b>', showarrow=False, xanchor='center', yanchor='bottom')
        fig_estimulada.update_layout(title='INTENÇÃO DE VOTOS - PESQUISA ESTIMULADA', title_x=0.5, xaxis_title='Candidatos', yaxis_title='Porcentagem (%)', xaxis_tickangle=-45, bargap=0.1, height=500, margin=dict(l=50, r=50, t=50, b=50), title_xanchor='center')
        figures['Intenção de Votos - Pesquisa Estimulada'] = fig_estimulada

        # Gráfico de Rejeição
        fig_rejeicao = go.Figure()
        rejeicao_data = df["REJEICAO"]
        rejeicao_counts = rejeicao_data.value_counts()
        if 'INDECISO' in rejeicao_counts.index or 'NENHUM' in rejeicao_counts.index:
            rejeicao_counts = rejeicao_counts.reindex(index=[i for i in rejeicao_counts.index if i not in ['INDECISO', 'NENHUM']] + [i for i in ['INDECISO', 'NENHUM'] if i in rejeicao_counts.index])
        rejeicao_percentages = (rejeicao_counts / rejeicao_counts.sum()) * 100
        for i, (categoria, porcentagem) in enumerate(zip(rejeicao_percentages.index, rejeicao_percentages.values)):
            cor = cores[i % len(cores)]
            fig_rejeicao.add_trace(go.Bar(x=[categoria], y=[porcentagem], marker_color=cor, showlegend=False))
            fig_rejeicao.add_annotation(x=i, y=porcentagem + 0.1, text=f'<b>{porcentagem:.0f}%</b>', showarrow=False, xanchor='center', yanchor='bottom')
        fig_rejeicao.update_layout(title='NÍVEL DE REJEIÇÃO', title_x=0.5, xaxis_title='Candidatos', yaxis_title='Porcentagem (%)', xaxis_tickangle=-45, bargap=0.1, height=500, margin=dict(l=50, r=50, t=50, b=50), title_xanchor='center')
        figures['Nível de Rejeição'] = fig_rejeicao

        # Gráfico de Confronto Direto - Cenário 1
        fig_estimulada_1v1 = go.Figure()
        estimulada_1v1_data = df["ESTIMULADA_1v1"]
        estimulada_1v1_counts = estimulada_1v1_data.value_counts()
        total_observations_1 = len(estimulada_1v1_data)
        estimulada_1v1_percentages = (estimulada_1v1_counts / total_observations_1) * 100
        ci_err_1 = z_critical * np.sqrt((estimulada_1v1_percentages * (100 - estimulada_1v1_percentages)) / total_observations_1)
        for i, (categoria, porcentagem) in enumerate(zip(estimulada_1v1_percentages.index, estimulada_1v1_percentages.values)):
            cor = cores[i % len(cores)]
            fig_estimulada_1v1.add_trace(go.Bar(x=[categoria], y=[porcentagem], marker_color=cor, showlegend=False, textposition='auto'))
            fig_estimulada_1v1.add_trace(go.Scatter(x=[categoria, categoria], y=[porcentagem + ci_err_1[i] + 1.5, porcentagem + ci_err_1[i] + 0.5], text=[f"IC: [{porcentagem - ci_err_1[i]:.1f}%, {porcentagem + ci_err_1[i]:.1f}%]"], mode='text', showlegend=False))
            fig_estimulada_1v1.add_annotation(x=categoria, y=porcentagem + 0.1, text=f'<b>{porcentagem:.1f}%</b>', showarrow=False, xanchor='center', yanchor='bottom', font=dict(color='black'))
        fig_estimulada_1v1.update_layout(title='CONFRONTO DIRETO - CENÁRIO 1', title_x=0.5, xaxis_title='Candidatos', yaxis_title='Porcentagem (%)', xaxis_tickangle=-45, bargap=0.1, height=500, margin=dict(l=50, r=50, t=50, b=50), title_xanchor='center')
        figures['Confronto Direto - Cenário 1'] = fig_estimulada_1v1

        # Gráfico de Confronto Direto - Cenário 2
        fig_estimulada_1v1_2 = go.Figure()
        estimulada_1v1_2_data = df["ESTIMULADA_1v1-2"]
        estimulada_1v1_2_counts = estimulada_1v1_2_data.value_counts()
        total_observations_2 = len(estimulada_1v1_2_data)
        estimulada_1v1_2_percentages = (estimulada_1v1_2_counts / total_observations_2) * 100
        ci_err_2 = z_critical * np.sqrt((estimulada_1v1_2_percentages * (100 - estimulada_1v1_2_percentages)) / total_observations_2)
        for i, (categoria, porcentagem) in enumerate(zip(estimulada_1v1_2_percentages.index, estimulada_1v1_2_percentages.values)):
            cor = cores[i % len(cores)]
            fig_estimulada_1v1_2.add_trace(go.Bar(x=[categoria], y=[porcentagem], marker_color=cor, showlegend=False, textposition='auto'))
            fig_estimulada_1v1_2.add_trace(go.Scatter(x=[categoria, categoria], y=[porcentagem + ci_err_2[i] + 1.5, porcentagem + ci_err_2[i] + 0.5], text=[f"IC: [{porcentagem - ci_err_2[i]:.1f}%, {porcentagem + ci_err_2[i]:.1f}%]"], mode='text', showlegend=False))
            fig_estimulada_1v1_2.add_annotation(x=categoria, y=porcentagem + 0.1, text=f'<b>{porcentagem:.1f}%</b>', showarrow=False, xanchor='center', yanchor='bottom', font=dict(color='black'))
        fig_estimulada_1v1_2.update_layout(title='CONFRONTO DIRETO - CENÁRIO 2', title_x=0.5, xaxis_title='Candidatos', yaxis_title='Porcentagem (%)', xaxis_tickangle=-45, bargap=0.1, height=500, margin=dict(l=50, r=50, t=50, b=50), title_xanchor='center')
        figures['Confronto Direto - Cenário 2'] = fig_estimulada_1v1_2

        # Gráfico de Confronto Direto - Cenário 3
        fig_estimulada_1v1_3 = go.Figure()
        estimulada_1v1_3_data = df["ESTIMULADA_1v1-3"]
        estimulada_1v1_3_counts = estimulada_1v1_3_data.value_counts()
        total_observations_3 = len(estimulada_1v1_3_data)
        estimulada_1v1_3_percentages = (estimulada_1v1_3_counts / total_observations_3) * 100
        ci_err_3 = z_critical * np.sqrt((estimulada_1v1_3_percentages * (100 - estimulada_1v1_3_percentages)) / total_observations_3)
        for i, (categoria, porcentagem) in enumerate(zip(estimulada_1v1_3_percentages.index, estimulada_1v1_3_percentages.values)):
            cor = cores[i % len(cores)]
            fig_estimulada_1v1_3.add_trace(go.Bar(x=[categoria], y=[porcentagem], marker_color=cor, showlegend=False, textposition='auto'))
            fig_estimulada_1v1_3.add_trace(go.Scatter(x=[categoria, categoria], y=[porcentagem + ci_err_3[i] + 1.5, porcentagem + ci_err_3[i] + 0.5], text=[f"IC: [{porcentagem - ci_err_3[i]:.1f}%, {porcentagem + ci_err_3[i]:.1f}%]"], mode='text', showlegend=False))
            fig_estimulada_1v1_3.add_annotation(x=categoria, y=porcentagem + 0.1, text=f'<b>{porcentagem:.1f}%</b>', showarrow=False, xanchor='center', yanchor='bottom', font=dict(color='black'))
        fig_estimulada_1v1_3.update_layout(title='CONFRONTO DIRETO - CENÁRIO 3', title_x=0.5, xaxis_title='Candidatos', yaxis_title='Porcentagem (%)', xaxis_tickangle=-45, bargap=0.1, height=500, margin=dict(l=50, r=50, t=50, b=50), title_xanchor='center')
        figures['Confronto Direto - Cenário 3'] = fig_estimulada_1v1_3

        return figures

    # Obter os gráficos
    figures = create_figures()

    # Adicionar gráficos de barras empilhadas às opções de gráficos
    figures['Transferência de Votos: Estimulada para Confronto Direto - Cenário 1'] = create_stacked_bar_chart('ESTIMULADA', 'ESTIMULADA_1v1', 'Transferência de Votos: Estimulada para Confronto Direto - Cenário 1')
    figures['Transferência de Votos: Estimulada para Confronto Direto - Cenário 2'] = create_stacked_bar_chart('ESTIMULADA', 'ESTIMULADA_1v1-2', 'Transferência de Votos: Estimulada para Confronto Direto - Cenário 2')
    figures['Transferência de Votos: Estimulada para Confronto Direto - Cenário 3'] = create_stacked_bar_chart('ESTIMULADA', 'ESTIMULADA_1v1-3', 'Transferência de Votos: Estimulada para Confronto Direto - Cenário 3')

    # Filtro para ordenar os gráficos, excluindo os fixos
    plot_order = st.sidebar.multiselect('Escolha o(s) gráfico(s)', options=[key for key in figures.keys() if key not in ['Distribuição por Sexo', 'Número de Respondentes', 'Pesquisa Eleitoral', 'Data da Pesquisa']], default=[key for key in figures.keys() if key not in ['Distribuição por Sexo', 'Número de Respondentes', 'Pesquisa Eleitoral', 'Data da Pesquisa']])

    # Organizar os gráficos de acordo com a ordem selecionada
    for i in range(0, len(plot_order), 2):
        with st.container():
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(plot_order):
                    col.plotly_chart(figures[plot_order[i + j]], use_container_width=True)
else:
    st.sidebar.warning("Por favor, carregue um arquivo Excel para visualizar o dashboard.")
