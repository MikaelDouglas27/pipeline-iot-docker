# Pipeline de Dados com IoT e Docker

Projeto acadêmico que importa leituras históricas de temperatura de sensores IoT, trata os dados com Python/Pandas, armazena no PostgreSQL em Docker e apresenta análises em um dashboard Streamlit.

## Tecnologias
- Python e Pandas: leitura e limpeza do CSV.
- SQLAlchemy/psycopg2: conexão e gravação no PostgreSQL.
- Docker Compose: execução do banco em contêiner.
- SQL: três views analíticas.
- Streamlit e Plotly: dashboard interativo.

## Estrutura
```text
pipeline_iot_docker/
├── data/                 
├── docs/                
├── sql/views.sql        
├── src/pipeline.py       
├── src/dashboard.py      
├── .env.example
├── docker-compose.yml
└── requirements.txt
```

## 1. Pré-requisitos
Instale Python 3.10+, Git e Docker Desktop. Baixe o CSV em:
https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices

Coloque o arquivo na pasta `data` e renomeie para `IOT-temp.csv`.

## 2. Configurar ambiente

Windows (PowerShell):
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 3. Iniciar PostgreSQL
```bash
docker compose up -d
docker compose ps
```
O banco será criado como `iot_db`, usuário `iot_user`, porta `5432`.

## 4. Executar o pipeline
Com o ambiente virtual ativado e o banco iniciado:
```bash
python src/pipeline.py
```
O programa normaliza os nomes das colunas do CSV, converte data e temperatura, remove linhas sem data/temperatura e duplicidades por identificador, grava a tabela `temperature_readings` e cria as três views.

## 5. Executar o dashboard
```bash
streamlit run src/dashboard.py
```
Abra o endereço local exibido no terminal.

## 6. Views SQL
1. `avg_temp_por_local`: média e quantidade de leituras por ambiente (interno/externo).
2. `leituras_por_hora`: volume de leituras em cada hora do dia, útil para observar padrões de coleta.
3. `temp_max_min_por_dia`: temperaturas máxima, mínima e média por dia, útil para acompanhar variações.

## 7. Validar no PostgreSQL
```bash
docker exec -it postgres-iot psql -U iot_user -d iot_db
```
No prompt do PostgreSQL:
```sql
SELECT COUNT(*) FROM temperature_readings;
SELECT * FROM avg_temp_por_local;
SELECT * FROM leituras_por_hora;
SELECT * FROM temp_max_min_por_dia LIMIT 10;
\q
```

## 8. Git e GitHub
```bash
git init
git add .
git commit -m "Projeto inicial: Pipeline de Dados IoT"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```
Para atualizações:
```bash
git add .
git commit -m "Descrição da alteração"
git push
```
Para baixar atualizações do remoto:
```bash
git pull
```
Configure sua identidade Git uma vez:
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

## 9. Capturas e documentação
Salva em `docs/` capturas reais do dashboard aberto no navegador.

## Fonte dos dados
Atul Anand Jha, **Temperature Readings: IoT Devices**, Kaggle:
https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices

O CSV original possui campos como `id`, `room_id/id`, `noted_date`, `temp` e `out/in`. O pipeline padroniza esses nomes antes de armazenar os registros.
