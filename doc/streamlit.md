Fundamentos
Instalação
Configuração do ambiente
Execução de aplicações
Modelo de execução do Streamlit
Rerun (reexecução do script)
Callbacks
Widgets
Session State
Cache
Arquitetura cliente-servidor
Aplicações reativas
Magic Commands
Gerenciamento de sessões
Tratamento de exceções
Gerenciamento de dependências
2. Elementos de texto
st.write()
st.write_stream()
st.title()
st.header()
st.subheader()
st.caption()
st.text()
st.markdown()
st.code()
st.latex()
st.html()
st.divider()
st.help()
3. Dados e tabelas
st.dataframe()
st.data_editor()
st.table()
st.metric()
st.json()
st.column_config
st.column_config.NumberColumn()
st.column_config.TextColumn()
st.column_config.CheckboxColumn()
st.column_config.SelectboxColumn()
st.column_config.DateColumn()
st.column_config.DatetimeColumn()
st.column_config.LinkColumn()
st.column_config.ImageColumn()
Formatação de tabelas
Ordenação de dados
Filtros de dados
Edição de células
Seleção de linhas
Formatação condicional
Validação de dados
Exportação de dados
Paginação de dados
4. Gráficos e visualizações
st.area_chart()
st.bar_chart()
st.line_chart()
st.scatter_chart()
st.map()
st.pyplot()
st.altair_chart()
st.vega_lite_chart()
st.plotly_chart()
st.pydeck_chart()
st.graphviz_chart()
st.mermaid_chart()
st.echarts_chart()
Gráficos interativos
Gráficos estatísticos
Gráficos financeiros
Gráficos de séries temporais
Gráficos geográficos
Mapas interativos
Visualização de dados com Pandas
Integração com Matplotlib
Integração com Plotly
Integração com Altair
Integração com PyDeck
Integração com Graphviz
Integração com Apache ECharts
Integração com bibliotecas de visualização externas
5. Widgets de entrada
st.button()
st.checkbox()
st.toggle()
st.radio()
st.selectbox()
st.multiselect()
st.slider()
st.select_slider()
st.number_input()
st.text_input()
st.text_area()
st.date_input()
st.time_input()
st.color_picker()
st.file_uploader()
st.camera_input()
st.audio_input()
st.feedback()
st.pills()
st.segmented_control()
st.multiselect()
st.selectbox()
Valores padrão
Valores mínimos e máximos
Validação de entradas
Widgets desabilitados
Widgets com chave (key)
Callbacks de widgets
Widgets condicionais
Widgets dependentes
Persistência de valores
6. Upload e gerenciamento de arquivos
Upload de arquivos
Upload de múltiplos arquivos
Upload de CSV
Upload de Excel
Upload de PDF
Upload de imagens
Upload de JSON
Upload de TXT
Upload de arquivos ZIP
Limitação de tamanho de arquivos
Processamento de arquivos enviados
Download de arquivos
st.download_button()
Geração de relatórios para download
Exportação de DataFrames
Exportação de arquivos processados
7. Layout e organização da interface
st.columns()
st.container()
st.empty()
st.expander()
st.popover()
st.sidebar
st.tabs()
st.dialog()
st.form()
st.form_submit_button()
st.space()
st.container(border=True)
Containers com largura configurável
Containers com altura configurável
Containers com bordas
Layout responsivo
Colunas de tamanhos diferentes
Layout horizontal
Layout vertical
Elementos aninhados
Organização de componentes
Sidebar fixa
Navegação lateral
Modais
Abas
Menus suspensos
8. Formulários
Criação de formulários
Campos de formulário
st.form()
st.form_submit_button()
Validação de formulários
Formulários com múltiplos campos
Formulários em colunas
Formulários na sidebar
Formulários com upload
Formulários com callbacks
Submissão de formulários
Controle de reruns
Formulários condicionais
Formulários de cadastro
Formulários de edição
Formulários de configurações
9. Status, mensagens e feedback
st.success()
st.info()
st.warning()
st.error()
st.exception()
st.toast()
st.progress()
st.spinner()
st.status()
st.skeleton()
st.balloons()
st.snow()
Barras de progresso
Indicadores de carregamento
Mensagens de validação
Mensagens de erro
Mensagens de sucesso
Alertas
Notificações
Estados de processamento
Feedback de operações
Indicadores de status
10. Chat e aplicações de IA
st.chat_message()
st.chat_input()
st.write_stream()
Interfaces de chat
Histórico de conversas
Mensagens do usuário
Mensagens do assistente
Streaming de respostas
Upload de arquivos no chat
Chatbots
Integração com OpenAI
Integração com modelos de linguagem
Integração com APIs de IA
Aplicações RAG
Agentes de IA
Copilotos
Assistentes virtuais
Análise de documentos
Geração de texto
Geração de código
Classificação de textos
Resumo de documentos
Aplicações de machine learning
Aplicações de deep learning
11. Estado da aplicação
st.session_state
Armazenamento de variáveis de sessão
Inicialização de estado
Atualização de estado
Remoção de estado
Estado compartilhado entre páginas
Estado de widgets
Estado de formulários
Estado de autenticação
Estado de filtros
Estado de navegação
Estado de carregamento
Estado de seleção
Estado de preferências do usuário
Persistência durante reruns
Gerenciamento de estado complexo
12. Callbacks e eventos
on_click
on_change
Callbacks de botões
Callbacks de inputs
Callbacks de formulários
Callbacks de seleção
Callbacks de upload
Eventos de alteração
Eventos de submissão
Execução de funções
Passagem de argumentos
Uso de args
Uso de kwargs
Atualização de Session State
Controle de fluxo com callbacks
13. Cache e desempenho
st.cache_data
st.cache_resource
Cache de dados
Cache de recursos
Cache de consultas SQL
Cache de chamadas de API
Cache de DataFrames
Cache de modelos de machine learning
Cache de conexões
Cache de objetos
Tempo de expiração
Invalidação de cache
Limpeza de cache
Controle de hash
Otimização de reruns
Otimização de consultas
Uso de fragments
st.fragment()
Atualização parcial de componentes
Processamento assíncrono com integrações externas
14. Conexões e bancos de dados
st.connection()
Conexões com bancos de dados
Conexões com APIs
Conexões personalizadas
SQL
SQLite
PostgreSQL
MySQL
SQL Server
Snowflake
MongoDB via bibliotecas externas
Redis via bibliotecas externas
SQLAlchemy
Pandas read_sql
Consultas parametrizadas
Pool de conexões
Gerenciamento de conexões
Reutilização de conexões
Transações
Tratamento de erros de conexão
Integração com serviços externos
15. Secrets e credenciais
st.secrets
Arquivo secrets.toml
Variáveis de ambiente
API Keys
Tokens de acesso
Credenciais de bancos de dados
Credenciais de APIs
Configuração de OAuth
Segredos por ambiente
Separação entre desenvolvimento e produção
Proteção de credenciais
Gerenciamento de segredos no deploy
16. Autenticação e usuários
st.login()
st.logout()
st.user
Login de usuários
Logout de usuários
Identidade do usuário
Autenticação OAuth
OpenID Connect
Integração com provedores de identidade
Controle de acesso
Sessões autenticadas
Usuários autenticados
Informações do perfil
Proteção de páginas
Autorização com bibliotecas externas
Integração com sistemas de autenticação próprios
17. Aplicações multipágina
st.navigation()
st.Page()
st.page_link()
st.switch_page()
Criação de páginas
Navegação entre páginas
Menus de navegação
Navegação na sidebar
Navegação por links
Navegação programática
Páginas dinâmicas
Páginas condicionais
Controle de acesso por página
Compartilhamento de Session State
Estrutura de projetos multipágina
Títulos de páginas
Ícones de páginas
URLs de páginas
Navegação personalizada
18. Configuração da página
st.set_page_config()
Título da página
Favicon
Layout wide
Layout centered
Estado inicial da sidebar
Configuração da toolbar
Configuração de menu
Configuração de tema
Configuração de servidor
Configuração de cliente
Configuração de execução
Configuração de cache
Configuração de upload
Configuração de segurança
Configuração de logs
19. Temas e aparência
Arquivo config.toml
Tema claro
Tema escuro
Cor primária
Cor de fundo
Cor de fundo secundária
Cor do texto
Tipografia
Personalização de fontes
Configuração de bordas
Personalização de componentes
Configuração de sidebar
Configuração de widgets
Personalização de gráficos
Identidade visual
CSS personalizado
HTML personalizado
Ícones
Logo
Favicon
Personalização de layout
20. Imagens e multimídia
st.image()
st.logo()
st.audio()
st.video()
st.pdf()
st.iframe()
Exibição de imagens
Imagens locais
Imagens remotas
Imagens em Base64
Galerias de imagens
Vídeos locais
Vídeos remotos
Reprodução de áudio
Reprodução de vídeo
Visualização de PDFs
Incorporação de páginas externas
Visualização de documentos
Integração com armazenamento de arquivos
21. HTML, CSS e JavaScript
st.html()
st.markdown(unsafe_allow_html=True)
HTML personalizado
CSS personalizado
Estilização de componentes
Classes CSS
IDs HTML
JavaScript incorporado
Componentes HTML
Elementos interativos
Layouts personalizados
Estilização de dashboards
Integração com bibliotecas JavaScript
Cuidados de segurança com HTML e JavaScript
22. Componentes personalizados
streamlit.components.v1
declare_component()
html()
iframe()
Componentes frontend
Componentes React
Componentes JavaScript
Componentes TypeScript
Componentes HTML
Comunicação frontend-backend
Componentes bidirecionais
Componentes de terceiros
Integração com bibliotecas JavaScript
Desenvolvimento de widgets personalizados
Empacotamento de componentes
Publicação de componentes
Integração de componentes externos
23. Visualização avançada e integrações
Plotly
Altair
Matplotlib
Seaborn
PyDeck
Graphviz
ECharts
Bokeh
Vega-Lite
Folium
NetworkX
Mermaid
AgGrid
Componentes de mapas
Componentes de gráficos financeiros
Componentes de tabelas avançadas
Componentes de diagramas
Componentes de dashboards
Bibliotecas de visualização personalizadas
24. Machine Learning e Data Science
Integração com Pandas
Integração com NumPy
Integração com Scikit-learn
Integração com TensorFlow
Integração com PyTorch
Integração com XGBoost
Integração com LightGBM
Integração com modelos de classificação
Integração com modelos de regressão
Integração com modelos de clustering
Previsões
Avaliação de modelos
Visualização de métricas
Upload de datasets
Pré-processamento de dados
Treinamento de modelos
Inferência
Monitoramento de modelos
Explicabilidade de modelos
Aplicações de análise estatística
25. Testes automatizados
streamlit.testing.v1
AppTest
AppTest.from_file()
AppTest.from_string()
AppTest.from_function()
Testes de aplicações
Testes de widgets
Testes de formulários
Testes de páginas
Testes de navegação
Testes de Session State
Simulação de cliques
Simulação de inputs
Simulação de uploads
Testes de validação
Testes de integração
Testes com Pytest
Testes de regressão
Automação de testes
Cobertura de testes
26. CLI do Streamlit
streamlit run
streamlit hello
streamlit version
streamlit config show
streamlit cache clear
streamlit docs
streamlit help
streamlit init
streamlit free
streamlit deploy
streamlit activate
streamlit skills
Execução de scripts
Configuração via terminal
Limpeza de cache
Consulta de versão
Inicialização de projetos
Gerenciamento de aplicações
27. Estrutura de projetos
app.py
Pasta pages
Pasta components
Pasta services
Pasta models
Pasta utils
Pasta tests
Pasta .streamlit
config.toml
secrets.toml
requirements.txt
pyproject.toml
README.md
Organização por funcionalidades
Organização por domínio
Separação entre frontend e backend
Separação entre serviços
Gerenciamento de configurações
Gerenciamento de ambientes
Estrutura para produção
Arquitetura modular
28. Integração com APIs
APIs REST
APIs GraphQL
Requisições HTTP
Biblioteca Requests
Biblioteca HTTPX
Autenticação por API Key
Autenticação Bearer Token
OAuth
Webhooks
Upload para APIs
Download de dados via APIs
Paginação de APIs
Tratamento de erros HTTP
Retry de requisições
Rate limiting
Cache de respostas
Integração com APIs de terceiros
Integração com APIs internas
Integração com serviços SaaS
29. Desenvolvimento de SaaS
Dashboard administrativo
Dashboard de clientes
Dashboard financeiro
Dashboard de vendas
Dashboard de marketing
Dashboard de indicadores
Gestão de usuários
Gestão de organizações
Gestão de permissões
Multi-tenancy
Controle de acesso baseado em funções
CRUD
Cadastro de clientes
Cadastro de produtos
Cadastro de serviços
Gestão de documentos
Gestão de tarefas
Gestão de projetos
Relatórios
Exportação de relatórios
Filtros avançados
Busca de dados
Notificações
Configurações de conta
Integração com bancos de dados
Integração com APIs
Autenticação
Auditoria
Logs de atividades
Integração com pagamentos externos
Integração com sistemas ERP
Integração com sistemas CRM
30. Segurança
Proteção de credenciais
Uso de Secrets
Variáveis de ambiente
Validação de entradas
Sanitização de dados
Proteção contra XSS
Controle de acesso
Autenticação
Autorização
Controle de sessões
Proteção de arquivos enviados
Limitação de upload
Validação de extensões
Tratamento de exceções
Logs de segurança
Proteção de APIs
Rate limiting com ferramentas externas
Proteção de endpoints
Controle de permissões
Segurança de banco de dados
Uso de HTTPS
Configuração segura de proxy
Segurança de componentes HTML
Segurança de aplicações multiusuário
31. Deploy e hospedagem
Execução local
Streamlit Community Cloud
Docker
Docker Compose
VPS
EasyPanel
Railway
Render
Heroku
AWS
Google Cloud
Azure
Snowflake
Kubernetes
Nginx
Reverse proxy
HTTPS
Domínio personalizado
Variáveis de ambiente em produção
Secrets em produção
Monitoramento
Logs de produção
Escalabilidade
Health checks
CI/CD
GitHub Actions
Gerenciamento de processos
Atualização de aplicações
32. Desempenho e escalabilidade
Cache de dados
Cache de recursos
Otimização de consultas
Paginação
Lazy loading
Processamento em lote
Redução de reruns
Uso de fragments
Compressão de dados
Otimização de DataFrames
Processamento assíncrono
Filas de tarefas
Workers externos
Gerenciamento de memória
Gerenciamento de sessões
Monitoramento de CPU
Monitoramento de RAM
Monitoramento de tempo de resposta
Otimização de uploads
Otimização de gráficos
Estratégias de escalabilidade horizontal
33. Documentação e recursos oficiais
Documentação oficial
API Reference
Get Started
Fundamentals
Tutorials
User Interface
Advanced concepts
Deployment
Components
App testing
Community
Blog
GitHub
Fórum da comunidade
Exemplos oficiais
Cheat Sheet
Release notes
Guias de migração
Referência de configuração
Referência de widgets
Referência de componentes