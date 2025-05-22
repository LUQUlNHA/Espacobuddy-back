
# 🌱 EspaçoBuddy - Backend Modular para Gestão de Rotinas Automatizadas

Este projeto implementa um ecossistema de serviços backend modulares, com foco em automação de rotinas via MQTT e autenticação robusta com Keycloak. A estrutura foi concebida com **boas práticas de arquitetura, princípios SOLID**, e está organizada em microserviços com comunicação via Docker Compose.

---

## 📐 Arquitetura do Projeto

```
┌─────────────┐    ┌────────────┐    ┌─────────────┐
│ React Native│ →  │ Flask APIs │ →  │ PostgreSQL  │
└─────────────┘    └─────┬──────┘    └─────┬───────┘
                         ↓                    ↓
                ┌─────────────┐       ┌──────────────┐
                │ Mosquitto   │ ←──── │ run_routine  │
                └─────────────┘       └──────────────┘
```

**Serviços incluídos**:
- `list` – listagem dinâmica com suporte a filtros e foreign keys
- `register` – cadastro genérico de dados por tabela
- `delete` – exclusão condicional de registros
- `run_routine` – execução periódica com envio via MQTT
- `keycloak` – autenticação de usuários
- `postgres` – persistência central
- `mosquitto` – broker MQTT para comunicação com dispositivos

---

## 💡 Padrões e Boas Práticas Utilizadas

### ✅ Princípios SOLID

| Princípio | Aplicação |
|----------|-----------|
| **S – Single Responsibility** | Cada serviço (API Flask) tem um único propósito, como listar, cadastrar, deletar ou executar |
| **O – Open/Closed** | Funções como `build_where_clause` e os serviços são abertos à extensão (por ex. novos campos), sem alterar código existente |
| **L – Liskov Substitution** | Classes (como `Routine`) podem ser substituídas por subclasses sem quebrar a lógica dos serviços |
| **I – Interface Segregation** | Os serviços não forçam parâmetros desnecessários – cada rota trata apenas de seu domínio |
| **D – Dependency Inversion** | Variáveis de ambiente e injeção por `os.getenv` evitam acoplamento direto a detalhes técnicos |

---

## 🧱 Estrutura de Diretórios

```
.
├── docker-compose.yml
├── .env
├── services/
│   ├── list/           # Serviço de listagem dinâmica
│   ├── register/       # Serviço para inserção de dados
│   ├── delete/         # Serviço de exclusão
│   ├── run_routine/    # Serviço para execução de rotinas com MQTT
│   └── mosquitto/      # Configuração do broker MQTT
├── assets/
│   ├── postgres/       # Scripts e init do banco
│   └── keycloak/       # Temas e dados do Keycloak
└── volumes/            # Volumes nomeados (pgdata, keycloak)
```

---

## 🛠️ Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/LUQUlNHA/Espacobuddy-back.git
cd Espacobuddy-back
```

### 2. Configure o `.env`

Crie um arquivo `.env` com base no `.env.example`. Exemplo:

```env
DB_HOST=espacobuddy_postgres
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
FLASK_ENV=development

MQTT_BROKER=espacobuddy_mosquitto
MQTT_PORT=1883
MQTT_TOPIC_ROUTINE=menu/params/post/espacobuddy/routine
```

### 3. Suba os serviços

```bash
docker-compose up --build
```

---

## 🧪 Endpoints Principais

| Serviço   | Porta | Rota                | Método  | Descrição                                  |
|-----------|-------|---------------------|---------|--------------------------------------------|
| `list`    | 5003  | `/api/list`         | `GET`   | Lista registros com filtros e foreign keys |
| `register`| 5000  | `/api/register`     | `POST`  | Registra dinamicamente um novo dado        |
| `delete`  | 5004  | `/api/delete`       | `DELETE`| Remove registros com WHERE dinâmico        |
| `run_routine`| 5005 | (interno)          | loop    | Executa e envia rotinas via MQTT           |

---

## 🧰 Scripts Úteis

Localizados em `assets/keycloak/tools/` e `curls/`:

- `create-realm.sh` → Cria um realm no Keycloak
- `create_user.sh` → Registra um usuário via API
- `setup.sh` → Gera uma massa de dados inicial para testes

> **Atenção**: Estes scripts são apenas para facilitar testes em **ambientes de desenvolvimento e staging**, não devem ser usados em produção real.

---

## 🧭 Próximos Passos

- [ ] Adicionar autenticação JWT aos serviços Flask (Build 2)
- [ ] Implementar logs estruturados (com `loguru` ou `structlog`)
- [ ] Validação de entrada com Pydantic ou Marshmallow

---

## 👨‍💻 Autores

- Nicolas Leonardi Barsalini
- Lucas Ferreira Neto
- Pedro Henrique Fescina
- Lucas Miranda

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
