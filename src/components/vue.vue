<template>
  <div id="app">
    <header class="header">
      <h1>Busca de Operadoras de Saúde</h1>
    </header>
    
    <main class="main-content">
      <div class="search-box">
        <input 
          v-model="termoBusca" 
          placeholder="Digite nome, CNPJ ou registro ANS..."
          @keyup.enter="buscarOperadoras"
        >
        <button @click="buscarOperadoras" :disabled="!termoBusca || carregando">
          <span v-if="carregando">
            <i class="fas fa-spinner fa-spin"></i> Buscando...
          </span>
          <span v-else>Buscar</span>
        </button>
      </div>
      
      <div v-if="mensagemErro" class="error-message">
        {{ mensagemErro }}
      </div>
      
      <div v-if="resultados.length" class="results-container">
        <h2>Resultados </h2>
        <p class="result-count">{{ resultados.length }} operadoras encontradas</p>
        
        <div class="table-responsive">
          <table class="results-table">
            <thead>
              <tr>
                <th @click="ordenarPor('Relevancia')">Relevância</th>
                <th @click="ordenarPor('Razao_Social')">Razão Social</th>
                <th @click="ordenarPor('Nome_Fantasia')">Nome Fantasia</th>
                <th @click="ordenarPor('CNPJ')">CNPJ</th>
                <th @click="ordenarPor('Registro_ANS')">Registro ANS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in resultadosOrdenados" :key="item.Registro_ANS">
                <td class="relevance-cell">{{ item.Relevancia }}%</td>
                <td>{{ item.Razao_Social }}</td>
                <td>{{ formatarCampoVazio(item.Nome_Fantasia) }}</td>
                <td>{{ formatarCNPJ(item.CNPJ) }}</td>
                <td>{{ item.Registro_ANS }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div v-else-if="termoBusca && carregando" class="no-results">
        Buscando operadora para "{{ termoBusca }}"
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import { debounce } from 'lodash';

export default {
  name: 'App',
  data() {
    return {
      termoBusca: '',
      resultados: [],
      carregando: false,
      mensagemErro: '',
      ordenacao: {
        campo: 'Relevancia',
        direcao: 'desc'
      }
    };
  },
  computed: {
    resultadosOrdenados() {
      return [...this.resultados].sort((a, b) => {
        const valA = a[this.ordenacao.campo];
        const valB = b[this.ordenacao.campo];
        if (this.ordenacao.direcao === 'asc') {
          return valA > valB ? 1 : -1;
        }
        return valA < valB ? 1 : -1;
      });
    }
  },
  methods: {
    buscarOperadoras: debounce(async function() {
  if (!this.termoBusca.trim()) return;

  this.carregando = true;
  this.mensagemErro = '';
  this.resultados = [];

  try {
    const apiUrl = 'http://localhost:5000/api';
    const response = await axios.get(`${apiUrl}/buscar_operadoras`, {
      params: {
        termo: this.termoBusca
      }
    });

    if (!response.data.resultados || response.data.resultados.length === 0) {
      this.mensagemErro = `Nenhuma operadora encontrada para "${this.termoBusca}"`;
      return;
    }

    // Mapeamento correto dos campos
    this.resultados = response.data.resultados.map(item => ({
      Razao_Social: item.Razao_Social || '',
      Nome_Fantasia: item.Nome_Fantasia || '',
      CNPJ: item.CNPJ || '',
      Registro_ANS: item.Registro_ANS || '',
      Relevancia: item.RELEVANCIA || 0  // Mapeia RELEVANCIA para Relevancia
    }));

  } catch (error) {
    console.error('Erro na busca:', error);
    this.mensagemErro = this.tratarErro(error);
  } finally {
    this.carregando = false;
  }
}, 300),

    ordenarPor(campo) {
      if (this.ordenacao.campo === campo) {
        this.ordenacao.direcao = this.ordenacao.direcao === 'asc' ? 'desc' : 'asc';
      } else {
        this.ordenacao.campo = campo;
        this.ordenacao.direcao = 'desc';
      }
    },

    formatarCNPJ(cnpj) {
      if (!cnpj) return '-';
      const numeros = cnpj.toString().replace(/\D/g, '');
      if (numeros.length !== 14) return cnpj;
      return `${numeros.slice(0, 2)}.${numeros.slice(2, 5)}.${numeros.slice(5, 8)}/${numeros.slice(8, 12)}-${numeros.slice(12)}`;
    },

    formatarCampoVazio(valor) {
      return valor || '-';
    },

    tratarErro(error) {
      if (error.message.includes('Failed to fetch')) {
        return 'Não foi possível conectar ao servidor. Verifique a conexão.';
      }
      return `Erro: ${error.message}`;
    }
  }
};
</script>

<style scoped>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: #333;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-box input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.search-box button {
  padding: 10px 20px;
  background-color: #2c7be5;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-box button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #e63757;
  padding: 10px;
  background-color: #fff0f0;
  border-radius: 4px;
  margin-bottom: 20px;
}

.results-container {
  margin-top: 30px;
}

.result-count {
  color: #666;
  margin-bottom: 15px;
}

.table-responsive {
  overflow-x: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.results-table th {
  background-color: #f9fafc;
  padding: 12px 15px;
  text-align: left;
  border-bottom: 2px solid #e5e9f2;
  cursor: pointer;
  position: sticky;
  top: 0;
}

.results-table th:hover {
  background-color: #f0f4f8;
}

.results-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e5e9f2;
}

.results-table tr:hover {
  background-color: #f9fafc;
}

.relevance-cell {
  font-weight: bold;
  color: #2c7be5;
}

.no-results {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 18px;
  background: #f9f9f9;
  border-radius: 8px;
}

.fa-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
