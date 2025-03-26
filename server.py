from flask import Flask, request, jsonify
import pandas as pd
from fuzzywuzzy import fuzz
from flask_cors import CORS
import unicodedata

app = Flask(__name__)
CORS(app)

def normalizar_texto(texto):
    """Normaliza texto removendo acentos e caracteres especiais"""
    if pd.isna(texto):
        return ""
    texto = str(texto)
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower()

def formatar_cnpj(cnpj):
    """Formata CNPJ para o padrão brasileiro"""
    try:
        cnpj = str(cnpj).strip()
        cnpj = ''.join(filter(str.isdigit, cnpj))
        cnpj = cnpj.zfill(14)
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    except:
        return str(cnpj)

def carregar_dados():
    try:
        # Tenta diferentes encodings
        encodings = ['utf-8', 'latin1', 'ISO-8859-1']
        for encoding in encodings:
            try:
                df = pd.read_csv('Relatorio_cadop.csv', 
                                encoding=encoding,
                                delimiter=';',
                                dtype={'CNPJ': str, 'Registro_ANS': str})
                break
            except UnicodeDecodeError:
                continue
        
        df.columns = df.columns.str.strip()
        
        # Normaliza colunas de texto
        if 'Razao_Social' in df.columns:
            df['Razao_Social'] = df['Razao_Social'].fillna('').apply(normalizar_texto)
        if 'Nome_Fantasia' in df.columns:
            df['Nome_Fantasia'] = df['Nome_Fantasia'].fillna('').apply(normalizar_texto)
        
        print("\n✅ Dados carregados com sucesso!")
        print(f"Total de registros: {len(df)}")
        #print("\nExemplo de dados:")
        #print(df[['Razao_Social', 'Nome_Fantasia']].head(3))
        return df
    
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Carrega os dados
df = carregar_dados()

@app.route('/api/buscar_operadoras', methods=['GET'])
def buscar_operadoras():
    if df.empty:
        return jsonify({"error": "Dados não disponíveis"}), 503
        
    termo = request.args.get('termo', '').strip()
    if not termo:
        return jsonify({"error": "Parâmetro 'termo' é obrigatório"}), 400
    
    try:
        termo_normalizado = normalizar_texto(termo)
        df_busca = df.copy()
        
        # Inicializa relevância para todos os registros
        df_busca['RELEVANCIA'] = 0
        
        # Busca numérica (CNPJ ou Registro ANS)
        if termo.isdigit():
            for campo_num in ['CNPJ', 'Registro_ANS']:
                if campo_num in df_busca.columns:
                    # Remove formatação para comparação
                    df_busca[f'MATCH_{campo_num}'] = df_busca[campo_num].str.replace('[^0-9]', '', regex=True)
                    
                    # Calcula similaridade
                    df_busca[f'RELEVANCIA_{campo_num}'] = df_busca[f'MATCH_{campo_num}'].apply(
                        lambda x: 100 if termo in x else fuzz.ratio(termo, x))
                    
                    # Atualiza relevância máxima
                    df_busca['RELEVANCIA'] = df_busca[[f'RELEVANCIA_{campo_num}', 'RELEVANCIA']].max(axis=1)
                    
                    # Se encontrou correspondência exata, retorna imediatamente
                    if (df_busca[f'RELEVANCIA_{campo_num}'] == 100).any():
                        resultados = df_busca[df_busca[f'RELEVANCIA_{campo_num}'] == 100]
                        return montar_resposta(termo, [campo_num], resultados)
        
        # Busca textual (Razão Social/Nome Fantasia)
        campos_usados = []
        for campo in ['Razao_Social', 'Nome_Fantasia']:
            if campo in df_busca.columns:
                campos_usados.append(campo)
                df_busca[f'RELEVANCIA_{campo}'] = df_busca[campo].apply(
                    lambda x: fuzz.token_set_ratio(termo_normalizado, x))
                df_busca['RELEVANCIA'] = df_busca[[f'RELEVANCIA_{campo}', 'RELEVANCIA']].max(axis=1)
        
        # Filtra e ordena resultados
        resultados = (
            df_busca[df_busca['RELEVANCIA'] > 0]
            .sort_values('RELEVANCIA', ascending=False)
            .head(20)
        )
        
        return montar_resposta(termo, campos_usados, resultados)
    
    except Exception as e:
        print(f"Erro durante busca: {e}")
        return jsonify({"error": str(e)}), 500

def montar_resposta(termo, campos, resultados):
    dados = []
    for _, row in resultados.iterrows():
        item = {
            'Razao_Social': str(row.get('Razao_Social', '')),
            'Nome_Fantasia': str(row.get('Nome_Fantasia', '')),
            'CNPJ': str(row.get('CNPJ', '')),
            'CNPJ_Formatado': formatar_cnpj(row.get('CNPJ', '')),
            'Registro_ANS': str(row.get('Registro_ANS', '')),
            'RELEVANCIA': int(row['RELEVANCIA'])  # Garante que a relevância está incluída
        }
        dados.append(item)
    
    return jsonify({
        "termo": termo,
        "campos_buscados": campos,
        "total": len(dados),
        "resultados": dados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)