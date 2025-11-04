# Novas Ferramentas do Chatbot IA

Este documento descreve as 7 novas ferramentas implementadas para o chatbot de IA do sistema de monitoramento industrial.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Ferramentas Disponíveis](#ferramentas-disponíveis)
3. [Exemplos de Uso](#exemplos-de-uso)
4. [Integração com o LLM](#integração-com-o-llm)
5. [Dependências e Configuração](#dependências-e-configuração)

---

## Visão Geral

As novas ferramentas expandem significativamente as capacidades do chatbot, permitindo que ele:

- 📊 **Visualize dados** através de gráficos
- 🤖 **Preveja manutenções** usando Machine Learning
- 📧 **Envie notificações** para usuários
- 📈 **Analise dados estatisticamente**
- 📦 **Liste equipamentos e sensores**
- 📅 **Agende manutenções**

Todas as ferramentas foram implementadas seguindo o padrão existente e são **automaticamente descobertas** pelo sistema de importação dinâmica.

---

## Ferramentas Disponíveis

### 1. 📦 Listar Equipamentos

**Arquivo:** `listar_equipamentos_tool.py`  
**Função:** `listar_equipamentos()`  
**Descrição:** Lista todos os equipamentos cadastrados no sistema com informações detalhadas.

**Retorna:**
- ID do equipamento
- Nome e modelo
- Localização
- Data de instalação
- Número de sensores associados
- Descrição

**Exemplo de uso pelo usuário:**
- "Quais equipamentos estão cadastrados?"
- "Me mostre todos os equipamentos do sistema"
- "Liste os equipamentos disponíveis"

---

### 2. 📡 Listar Sensores

**Arquivo:** `listar_sensores_tool.py`  
**Função:** `listar_sensores(equipamento_id: int = None)`  
**Descrição:** Lista todos os sensores ou filtra por equipamento específico.

**Parâmetros:**
- `equipamento_id` (opcional): ID do equipamento para filtrar sensores

**Retorna:**
- ID e nome do sensor
- Tipo (temperatura, vibração, luminosidade)
- Equipamento associado
- Código serial
- Limiares de manutenção (superior e inferior)
- Data de instalação

**Exemplo de uso pelo usuário:**
- "Quais sensores estão instalados?"
- "Me mostre os sensores do equipamento 1"
- "Liste todos os sensores de temperatura"

---

### 3. 📅 Agendar Manutenção

**Arquivo:** `agendar_manutencao_tool.py`  
**Função:** `agendar_manutencao(equipamento_id: int, data_previsao: str, motivo: str, descricao: str = None)`  
**Descrição:** Agenda uma nova manutenção preventiva ou corretiva.

**Parâmetros:**
- `equipamento_id`: ID do equipamento (obrigatório)
- `data_previsao`: Data no formato YYYY-MM-DD ou DD/MM/YYYY (obrigatório)
- `motivo`: Razão da manutenção (obrigatório)
- `descricao`: Detalhes adicionais (opcional)

**Validações:**
- Verifica se o equipamento existe
- Suporta múltiplos formatos de data
- Alerta sobre datas no passado

**Exemplo de uso pelo usuário:**
- "Agende uma manutenção preventiva para o equipamento 1 no dia 31/12/2024"
- "Preciso agendar manutenção do equipamento 2 para 2025-01-15 devido a temperatura alta"
- "Marque uma revisão para o próximo mês no equipamento 3"

---

### 4. 📧 Enviar Notificação

**Arquivo:** `enviar_notificacao_tool.py`  
**Função:** `enviar_notificacao(assunto: str, mensagem: str)`  
**Descrição:** Envia notificações por e-mail via AWS SNS.

**Parâmetros:**
- `assunto`: Assunto do e-mail (máx. 100 caracteres)
- `mensagem`: Corpo da mensagem

**Configuração necessária (.env):**
```
SNS_TOPIC_ARN=arn:aws:sns:region:account:topic-name
SNS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_SESSION_TOKEN=your-token (se aplicável)
```

**Tratamento de erros:**
- Detecta falta de configuração
- Identifica problemas de autenticação AWS
- Trunca assuntos muito longos automaticamente

**Exemplo de uso pelo usuário:**
- "Envie uma notificação sobre a temperatura alta no sensor 3"
- "Alerte a equipe sobre a necessidade de manutenção no equipamento 1"
- "Notifique que o sistema está operando normalmente"

---

### 5. 📊 Analisar Dados do Sensor

**Arquivo:** `analisar_dados_sensor_tool.py`  
**Função:** `analisar_dados_sensor(sensor_id: int, dias: int = 7)`  
**Descrição:** Realiza análise estatística completa das leituras de um sensor.

**Parâmetros:**
- `sensor_id`: ID do sensor a analisar
- `dias`: Período de análise em dias (padrão: 7)

**Análises realizadas:**
- **Estatísticas básicas:** média, mediana, desvio padrão, mín, máx
- **Detecção de anomalias:** identifica outliers (>2σ)
- **Análise de tendência:** compara primeira vs segunda metade dos dados
- **Verificação de limiares:** detecta violações de limites configurados
- **Recomendações:** sugere ações baseadas nos dados

**Exemplo de uso pelo usuário:**
- "Analise os dados do sensor 1 dos últimos 7 dias"
- "Como está o comportamento do sensor de temperatura 3 na última semana?"
- "Me dê um resumo estatístico do sensor 2"

---

### 6. 📈 Gerar Gráfico de Leituras

**Arquivo:** `gerar_grafico_leituras_tool.py`  
**Função:** `gerar_grafico_leituras(sensor_id: int, dias: int = 7, data_especifica: str = None)`  
**Descrição:** Gera gráficos de linha com as leituras de sensores ao longo do tempo.

**Parâmetros:**
- `sensor_id`: ID do sensor
- `dias`: Número de dias para incluir (padrão: 7)
- `data_especifica`: Data específica no formato YYYY-MM-DD (opcional)

**Recursos do gráfico:**
- Plotagem de valores ao longo do tempo
- Linhas de limiar (superior e inferior) se configuradas
- Marcadores visuais para cada leitura
- Grade para melhor legibilidade

**Saída:**
- Descrição textual detalhada com estatísticas
- Gráfico gerado internamente (base64 para uso futuro na web)
- Análise de tendência
- Alertas de violação de limiares

**Exemplo de uso pelo usuário:**
- "Gere um gráfico das leituras do sensor 1 dos últimos 7 dias"
- "Mostre-me o histórico de temperatura do sensor 3"
- "Crie um gráfico para o dia 2024-01-15"

---

### 7. 🤖 Prever Necessidade de Manutenção

**Arquivo:** `prever_necessidade_manutencao_tool.py`  
**Função:** `prever_necessidade_manutencao(equipamento_id: int, dias_analise: int = 7)`  
**Descrição:** Usa Machine Learning para prever se um equipamento precisa de manutenção.

**Parâmetros:**
- `equipamento_id`: ID do equipamento
- `dias_analise`: Dias de histórico para análise (padrão: 7)

**Modelo utilizado:**
- **Algoritmo:** Decision Tree (max_depth=5)
- **Acurácia:** 95.24%
- **F1-Score:** 0.9524
- **Localização:** `assets/modelos_otimizados_salvos/DecTree_d5.pkl`

**Features analisadas:**
- Temperatura média
- Vibração média
- Luminosidade média

**Retorna:**
- Probabilidade de necessidade de manutenção (%)
- Status: MANUTENÇÃO RECOMENDADA ou EQUIPAMENTO NORMAL
- Dados coletados dos sensores
- Valores médios detectados
- Recomendações específicas

**Exemplo de uso pelo usuário:**
- "O equipamento 1 precisa de manutenção?"
- "Analise se há necessidade de manter o equipamento 2"
- "Use machine learning para prever manutenção no equipamento 3"

---

## Exemplos de Uso

### Cenário 1: Verificação de Status de Equipamento

**Usuário:** "Me mostre informações do equipamento 1 e seus sensores"

**Chatbot (internamente):**
1. Chama `listar_equipamentos()` para encontrar o equipamento
2. Chama `listar_sensores(equipamento_id=1)` para listar sensores
3. Responde com informações consolidadas

**Resposta esperada:**
```
Encontrei o equipamento 1:
- Nome: Bomba Hidráulica Principal
- Modelo: BH-2000
- Localização: Setor A
- Instalação: 15/01/2023
- Sensores: 3

Sensores instalados:
1. Sensor Temperatura - Limiar: 10°C a 80°C
2. Sensor Vibração - Limiar: 0 a 3
3. Sensor Luminosidade - Sem limiares configurados
```

---

### Cenário 2: Análise Completa com Predição

**Usuário:** "Analise o equipamento 1 e me diga se precisa manutenção"

**Chatbot (internamente):**
1. Chama `prever_necessidade_manutencao(equipamento_id=1)`
2. Se a probabilidade > 50%, chama `analisar_dados_sensor()` para cada sensor
3. Chama `agendar_manutencao()` se o usuário concordar

**Resposta esperada:**
```
🤖 Análise de Machine Learning concluída!

Equipamento: Bomba Hidráulica Principal
Probabilidade de Manutenção: 78.5%
Status: ⚠️ MANUTENÇÃO RECOMENDADA

Detalhes dos sensores:
- Temperatura: 65.3°C (média dos últimos 7 dias)
- Vibração: 2.1 (tendência de aumento)
- Luminosidade: Normal

Recomendações:
✓ Agendar manutenção preventiva urgente
✓ Sensor de temperatura próximo ao limiar
✓ Vibração em tendência crescente

Deseja que eu agende a manutenção?
```

---

### Cenário 3: Monitoramento e Notificação

**Usuário:** "Analise o sensor 1 e me notifique se houver problema"

**Chatbot (internamente):**
1. Chama `analisar_dados_sensor(sensor_id=1, dias=7)`
2. Se detectar anomalia, chama `enviar_notificacao()`

**Resposta esperada:**
```
📊 Análise do Sensor 1 completa!

Estatísticas (últimos 7 dias):
- Média: 72.5°C
- Máximo: 85.3°C (⚠️ ACIMA do limiar de 80°C)
- Mínimo: 68.2°C
- Desvio padrão: 4.2

⚠️ ALERTAS:
- 12 leituras acima do limiar superior
- Tendência de AUMENTO (15.3%)

📧 Notificação enviada para a equipe técnica!
ID da Mensagem: abc123xyz

Recomendações:
- Verificar equipamento imediatamente
- Considerar parada programada
- Agendar inspeção técnica
```

---

## Integração com o LLM

### Descoberta Automática

As ferramentas são **automaticamente descobertas** pelo sistema:

```python
# dynamic_tools.py faz a descoberta
from src.large_language_model.dynamic_tools import import_tools

tools = import_tools(sort=True)
# Todas as 7 novas ferramentas são encontradas automaticamente!
```

### Registro com Google Gemini

```python
# client.py registra as ferramentas
def _get_function_declarations(self) -> list[types.FunctionDeclaration]:
    return [tool.as_declaration() for tool in self.tool_list]
```

### Como o LLM Decide Usar as Ferramentas

O modelo analisa:
1. **Docstring da função:** Descrição detalhada do que a ferramenta faz
2. **Parâmetros:** Type hints e descrições dos argumentos
3. **Contexto da conversa:** O que o usuário está perguntando

**Exemplo:**

Usuário: "Quais equipamentos temos?"

LLM identifica:
- Palavra-chave "equipamentos"
- Necessidade de listar/buscar
- Ferramenta `listar_equipamentos` tem docstring que menciona "Lista todos os equipamentos"
- **Decisão:** Chamar `listar_equipamentos()`

---

## Dependências e Configuração

### Dependências Python

Todas já estão em `requirements.txt`:
- `matplotlib` - Geração de gráficos
- `scikit-learn` - ML e normalização de dados
- `joblib` - Carregamento de modelos ML
- `boto3` - AWS SNS para notificações
- `numpy` - Computação numérica
- `pandas` - Manipulação de dados

### Configuração AWS SNS (Notificações)

Para habilitar notificações por e-mail, configure no `.env`:

```bash
# AWS SNS Configuration
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789:seu-topico
SNS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...  # Opcional, se usar sessão temporária
```

**Passos para configurar SNS:**

1. Acesse o console AWS SNS
2. Crie um tópico (Topic)
3. Adicione subscrições (e-mails)
4. Copie o ARN do tópico
5. Configure as variáveis no `.env`

Se não configurar, a ferramenta retorna mensagem amigável informando que notificações não estão habilitadas.

### Modelos de Machine Learning

A ferramenta de predição precisa dos modelos treinados em:
```
assets/modelos_otimizados_salvos/DecTree_d5.pkl
```

Se o modelo não existir, a ferramenta informa que é necessário treinar antes de usar.

Para treinar os modelos:
```bash
python src/machine_learning/training.py
```

---

## Estrutura dos Arquivos

```
src/large_language_model/tools/
├── __init__.py
├── datetime_tool.py                          # Ferramenta existente
├── count_equipamentos_tool.py                # Ferramenta existente
├── listar_equipamentos_tool.py               # ✨ NOVO
├── listar_sensores_tool.py                   # ✨ NOVO
├── agendar_manutencao_tool.py                # ✨ NOVO
├── enviar_notificacao_tool.py                # ✨ NOVO
├── analisar_dados_sensor_tool.py             # ✨ NOVO
├── gerar_grafico_leituras_tool.py            # ✨ NOVO
└── prever_necessidade_manutencao_tool.py     # ✨ NOVO
```

---

## Testes

### Executar Testes

```bash
# Testar apenas as novas ferramentas
python -m pytest tests/unit/test_new_chatbot_tools.py -v

# Testar todo o sistema de chat
python -m pytest tests/unit/test_chat.py -v

# Testar tudo
python -m pytest tests/unit/ -v
```

### Cobertura de Testes

- ✅ 32 testes para as novas ferramentas
- ✅ Testes de instanciação
- ✅ Testes de docstrings
- ✅ Testes com dados vazios
- ✅ Testes com dados válidos
- ✅ Testes de tratamento de erros
- ✅ Testes de descoberta automática

---

## Boas Práticas

### Para Usuários do Chatbot

1. **Seja específico:** "Analise o sensor 1" é melhor que "Analise"
2. **Forneça IDs quando possível:** "Equipamento 1" ou "Sensor 3"
3. **Use linguagem natural:** O LLM entende contexto
4. **Peça confirmação:** Para ações críticas como agendar manutenção

### Para Desenvolvedores

1. **Sempre adicione docstrings completas:** O LLM usa para decidir quando chamar
2. **Use type hints:** Ajuda na validação e documentação
3. **Trate erros graciosamente:** Retorne mensagens amigáveis
4. **Teste com dados vazios:** Nem sempre haverá dados no banco
5. **Valide entradas:** IDs inválidos, datas malformadas, etc.
6. **Siga o padrão:** Use a mesma estrutura das ferramentas existentes

---

## Troubleshooting

### Ferramenta não é descoberta

**Problema:** Nova ferramenta não aparece no chat

**Soluções:**
1. Verifique se o arquivo está em `src/large_language_model/tools/`
2. Certifique-se que a classe herda de `BaseTool`
3. Implemente todos os métodos abstratos
4. Adicione docstring à função
5. Reinicie o servidor Streamlit

### Erro ao carregar modelo ML

**Problema:** "Modelo de predição não encontrado"

**Solução:**
```bash
# Execute o treinamento
python src/machine_learning/training.py
```

### Notificações não funcionam

**Problema:** "Notificações não estão configuradas"

**Soluções:**
1. Verifique as variáveis no `.env`
2. Teste credenciais AWS: `aws sns list-topics`
3. Verifique permissões IAM
4. Confirme que o tópico SNS existe

---

## Roadmap Futuro

Possíveis melhorias:

- [ ] Exportar gráficos como arquivos salvos
- [ ] Suporte a múltiplos canais de notificação (SMS, Push)
- [ ] Dashboard web para visualizar gráficos
- [ ] Predições mais avançadas (séries temporais, LSTM)
- [ ] Relatórios PDF automáticos
- [ ] Integração com calendário para manutenções
- [ ] Análise de múltiplos sensores simultaneamente
- [ ] Detecção de padrões anormais em tempo real

---

## Suporte

Para dúvidas ou problemas:

1. Verifique a documentação: `TOOLS_GUIDE.md`
2. Execute os testes: `pytest tests/unit/ -v`
3. Revise os logs do Streamlit
4. Consulte os exemplos neste documento

---

**Desenvolvido para o projeto FIAP Sprint 4 - Sistema de Manutenção Preditiva Industrial**
