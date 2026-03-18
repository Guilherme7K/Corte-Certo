# ✂️ Corte Certo — Sistema de Agendamento para Barbearias

Sistema web full-stack de agendamento online para barbearias, com painel administrativo e área do cliente. Desenvolvido com **Flask**, **SQLAlchemy** e **Tailwind CSS**, seguindo o padrão **MVC** com Flask Blueprints.

> 🔗 **Demo:** [cortecerto.onrender.com](https://cortecerto.onrender.com)

---

## 🖼️ Visão Geral

- **Página pública** com apresentação da barbearia e call-to-action para cadastro
- **Área do cliente** para agendar, visualizar e cancelar horários
- **Painel admin** com dashboard de métricas, gestão de serviços, agendamentos e bloqueios de agenda
- **API interna** para consulta dinâmica de horários disponíveis

---

## 🛠️ Tech Stack

| Camada | Tecnologia |
|---|---|
| **Backend** | Python 3 · Flask 3 · SQLAlchemy ORM |
| **Frontend** | Jinja2 · Tailwind CSS · JavaScript · GSAP |
| **Banco de Dados** | PostgreSQL (produção) · SQLite (dev) |
| **Segurança** | Werkzeug (hash de senhas) · Session-based auth · Decorators de autorização |
| **Deploy** | Render.com · Gunicorn · Supabase (PostgreSQL) |

---

## 📁 Arquitetura (MVC)

```
Corte-certo-2/
├── app.py                          # Entry point — inicialização e registro de Blueprints
├── config.py                       # Configurações e variáveis de ambiente
├── models.py                       # Model — entidades do banco (ORM)
├── decorators.py                   # Middlewares de autenticação/autorização
├── utils.py                        # Funções utilitárias e validações
│
├── controllers/                    # Controller — lógica de negócio por domínio
│   ├── main_controller.py          #   Página inicial
│   ├── auth_controller.py          #   Login, cadastro, logout
│   ├── admin_controller.py         #   Dashboard, serviços, agendamentos, bloqueios
│   ├── cliente_controller.py       #   Agendar, cancelar, histórico
│   └── api_controller.py           #   API JSON (horários disponíveis)
│
├── templates/                      # View — templates Jinja2
│   ├── base.html                   #   Layout principal
│   ├── index.html                  #   Landing page
│   ├── login.html / cadastro.html  #   Autenticação
│   ├── admin/                      #   Painel administrativo
│   └── cliente/                    #   Painel do cliente
│
├── static/                         # Assets estáticos
│   ├── css/ · js/ · images/
│
├── requirements.txt                # Dependências Python
├── Procfile / render.yaml          # Configuração de deploy
└── gunicorn.conf.py                # Servidor WSGI
```

---

## ⚙️ Funcionalidades

### Cliente
- Cadastro e login com validação de senha forte
- Agendamento online com verificação de disponibilidade em tempo real
- Cancelamento de agendamentos (mínimo 2h de antecedência)
- Histórico completo de agendamentos

### Administrador
- Dashboard com métricas: agendamentos do dia, receita, serviços mais populares
- CRUD completo de serviços (preço, duração, ativar/desativar)
- Gestão de agendamentos com filtros por data e status
- Bloqueio de agenda por período com cancelamento automático de agendamentos afetados

### Segurança
- Hash de senhas com Werkzeug (bcrypt)
- Decorators `@login_required` e `@admin_required` para proteção de rotas
- Sanitização de inputs contra XSS
- Proteção contra SQL Injection via ORM
- Validação server-side de todas as regras de negócio

---

## 🚀 Instalação Local

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/corte-certo.git
cd corte-certo

# Criar e ativar environment
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com sua SECRET_KEY e DATABASE_URL (opcional)

# Rodar a aplicação
python app.py
```

O servidor inicia em `http://localhost:5000`. O banco SQLite é criado automaticamente com dados de exemplo.

**Login padrão admin:** `admin@cortecerto.com` / `admin123`

---

## 📦 Deploy (Render.com)

1. Conecte o repositório Git ao Render
2. Configure as variáveis de ambiente: `SECRET_KEY`, `DATABASE_URL`
3. O deploy é automático a cada push — Gunicorn + PostgreSQL

---

## 📝 Licença

Este projeto foi desenvolvido para fins de estudo e portfólio.
