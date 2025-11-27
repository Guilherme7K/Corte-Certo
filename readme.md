# Relatório Técnico - Sistema Corte Certo

## 1. Visão Geral do Sistema

O **Corte Certo** é um sistema web completo de agendamento para barbearias, desenvolvido com foco em usabilidade, design minimalista e responsividade mobile. O sistema permite que clientes agendem horários online e que administradores gerenciem serviços, agendamentos e bloqueios de agenda.

---

## 2. Stack Tecnológica

### 2.1 Backend

#### **Python 3.x**
- **Por quê?** Linguagem de alto nível, amplamente utilizada para desenvolvimento web, com sintaxe clara e grande ecossistema de bibliotecas.
- **Vantagens:** Rápido desenvolvimento, fácil manutenção, comunidade ativa.

#### **Flask 3.0.0**
- **Por quê?** Microframework web minimalista e flexível para Python.
- **Vantagens:**
  - Leve e rápido
  - Fácil de aprender e implementar
  - Ideal para aplicações de médio porte
  - Extensível através de plugins
  - Roteamento simples e intuitivo

#### **Flask-SQLAlchemy 3.1.1**
- **Por quê?** ORM (Object-Relational Mapping) que abstrai operações de banco de dados.
- **Vantagens:**
  - Escreve queries em Python ao invés de SQL puro
  - Previne SQL Injection automaticamente
  - Facilita migrações e manutenção do schema
  - Suporta múltiplos bancos de dados

### 2.2 Banco de Dados

#### **PostgreSQL (Produção) / SQLite (Desenvolvimento)**
- **PostgreSQL (Supabase):**
  - **Por quê?** Banco de dados relacional robusto, open-source e escalável.
  - **Vantagens:**
    - ACID compliant (Atomicidade, Consistência, Isolamento, Durabilidade)
    - Suporta JSON e dados complexos
    - Excelente performance
    - Backup automático via Supabase
    - Free tier generoso
  
- **SQLite (Desenvolvimento):**
  - **Por quê?** Banco de dados local leve para desenvolvimento.
  - **Vantagens:**
    - Zero configuração
    - Arquivo único
    - Perfeito para testes locais

#### **psycopg2-binary 2.9.9**
- **Por quê?** Adaptador PostgreSQL mais popular para Python.
- **Vantagens:** Alta performance, thread-safe, compatível com Flask-SQLAlchemy.

### 2.3 Frontend

#### **HTML5 + Jinja2**
- **Por quê?** Jinja2 é o template engine do Flask.
- **Vantagens:**
  - Separação de lógica e apresentação
  - Templates reutilizáveis (herança)
  - Variáveis dinâmicas e loops
  - Filtros e funções customizadas

#### **Tailwind CSS 3.x (CDN)**
- **Por quê?** Framework CSS utility-first moderno.
- **Vantagens:**
  - Design system consistente
  - Responsividade nativa (mobile-first)
  - Classes utilitárias rápidas de implementar
  - Customização fácil via config
  - Sem CSS não utilizado
  - Design minimalista "Navalha & Concreto"

#### **JavaScript Vanilla + GSAP**
- **JavaScript Vanilla:**
  - **Por quê?** Sem dependências pesadas de frameworks.
  - **Vantagens:** Performance, controle total, carregamento rápido.

- **GSAP (GreenSock Animation Platform):**
  - **Por quê?** Biblioteca de animações profissionais.
  - **Vantagens:**
    - Animações suaves e performáticas
    - ScrollTrigger para animações on-scroll
    - Cross-browser compatível

#### **Font Awesome 6.4.0**
- **Por quê?** Biblioteca de ícones vetoriais.
- **Vantagens:** Ícones escaláveis, consistentes, fácil implementação.

#### **Google Fonts (Syne + Manrope)**
- **Syne:** Fonte display moderna e artística para títulos
- **Manrope:** Fonte sans-serif legível para corpo de texto
- **Por quê?** Combinação que transmite sofisticação e modernidade

### 2.4 Segurança

#### **Werkzeug 3.0.1**
- **Por quê?** Biblioteca WSGI com utilitários de segurança.
- **Recursos utilizados:**
  - Hash de senhas (generate_password_hash)
  - Verificação de senhas (check_password_hash)
  - Proteção contra timing attacks

#### **Flask Sessions**
- **Por quê?** Gerenciamento de sessões de usuário.
- **Implementação:**
  - Cookies assinados
  - SECRET_KEY para criptografia
  - Separação de sessões admin/cliente

#### **Decorators de Autorização**
- `@login_required`: Exige autenticação
- `@admin_required`: Exige permissão de administrador
- **Por quê?** Protege rotas sensíveis contra acesso não autorizado.

### 2.5 Deploy e Infraestrutura

#### **Gunicorn 21.2.0**
- **Por quê?** Servidor HTTP WSGI para Python em produção.
- **Vantagens:**
  - Pre-fork worker model
  - Suporta múltiplos workers
  - Estável e confiável
  - Recomendado para Flask em produção

#### **Render.com**
- **Por quê?** Plataforma de deploy moderna e fácil.
- **Vantagens:**
  - Deploy automático via Git
  - HTTPS gratuito
  - Free tier disponível
  - Zero configuração de servidor
  - Logs em tempo real

#### **python-dotenv 1.0.0**
- **Por quê?** Gerencia variáveis de ambiente.
- **Vantagens:**
  - Separa configurações sensíveis do código
  - Facilita deploy em diferentes ambientes
  - Segurança (credenciais fora do repositório)

---

## 3. Arquitetura do Sistema

### 3.1 Padrão MVC (Model-View-Controller)

```
┌─────────────────────────────────────────┐
│         CLIENTE (Navegador)             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     CONTROLLER (Flask Routes)           │
│  - app.py                               │
│  - Rotas de autenticação                │
│  - Rotas de agendamento                 │
│  - Rotas administrativas                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      MODEL (SQLAlchemy ORM)             │
│  - models.py                            │
│  - Usuario, Servico, Agendamento        │
│  - BloqueioAgenda                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    DATABASE (PostgreSQL/SQLite)         │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      VIEW (Jinja2 Templates)            │
│  - templates/                           │
│    - base.html                          │
│    - index.html                         │
│    - admin/*.html                       │
│    - cliente/*.html                     │
└─────────────────────────────────────────┘
```

### 3.2 Estrutura de Diretórios

```
Corte-certo-2/
├── app.py                 # Aplicação principal Flask
├── models.py              # Modelos de dados (ORM)
├── config.py              # Configurações da aplicação
├── utils.py               # Funções auxiliares
├── init_database.py       # Script de inicialização do BD
├── requirements.txt       # Dependências Python
├── Procfile              # Configuração Render.com
├── render.yaml           # Configuração adicional Render
├── gunicorn.conf.py      # Configuração Gunicorn
├── instance/             # Banco SQLite local
│   └── barbearia.db
├── static/               # Arquivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
└── templates/            # Templates Jinja2
    ├── base.html         # Template base
    ├── index.html        # Landing page
    ├── login.html
    ├── cadastro.html
    ├── admin/            # Painel administrativo
    │   ├── dashboard.html
    │   ├── agendamentos.html
    │   ├── servicos.html
    │   ├── bloqueios.html
    │   └── novo_bloqueio.html
    └── cliente/          # Painel do cliente
        ├── dashboard.html
        └── agendar.html
```

---

## 4. Modelos de Dados

### 4.1 Usuario
```python
- id (Integer, PK)
- nome (String)
- email (String, Unique)
- telefone (String)
- senha_hash (String)
- tipo (String: 'admin' ou 'cliente')
- data_cadastro (DateTime)
```

### 4.2 Servico
```python
- id (Integer, PK)
- nome (String)
- descricao (Text)
- duracao_minutos (Integer)
- preco (Float)
- ativo (Boolean)
```

### 4.3 Agendamento
```python
- id (Integer, PK)
- cliente_id (Integer, FK → Usuario)
- servico_id (Integer, FK → Servico)
- data (Date)
- hora (Time)
- status (String: 'pendente', 'confirmado', 'cancelado', 'concluido')
- observacoes (Text)
- data_criacao (DateTime)
```

### 4.4 BloqueioAgenda
```python
- id (Integer, PK)
- motivo (String)
- data_inicio (Date)
- data_fim (Date)
- observacoes (Text)
- ativo (Boolean)
```

### 4.5 Barbeiro
```python
- id (Integer, PK)
- barbearia (String)
- horario_abertura (Time)
- horario_fechamento (Time)
- intervalo_minutos (Integer: 30)
```

---

## 5. Funcionalidades Implementadas

### 5.1 Autenticação e Autorização
- ✅ Cadastro de clientes
- ✅ Login com validação de senha hash
- ✅ Sistema de sessões
- ✅ Separação admin/cliente
- ✅ Decorators de proteção de rotas
- ✅ Logout seguro

### 5.2 Painel do Cliente
- ✅ Dashboard com agendamentos
- ✅ Sistema de agendamento online
- ✅ Seleção de serviços
- ✅ Calendário de disponibilidade
- ✅ Validação de horários (30min antecedência)
- ✅ Filtro de horários passados
- ✅ Cancelamento de agendamentos (2h antecedência)
- ✅ Status de agendamentos

### 5.3 Painel Administrativo
- ✅ Dashboard com estatísticas
- ✅ Gerenciamento de agendamentos
- ✅ Filtros por status e data
- ✅ Atualização de status
- ✅ CRUD de serviços
- ✅ Modal de edição
- ✅ Ativação/desativação de serviços
- ✅ Gerenciamento de bloqueios
- ✅ Criação de períodos bloqueados
- ✅ Ativação/desativação de bloqueios
- ✅ Exclusão de bloqueios (incluindo histórico)

### 5.4 Sistema de Disponibilidade
- ✅ Verificação de horários bloqueados
- ✅ Verificação de agendamentos existentes
- ✅ Intervalo de 30 minutos entre horários
- ✅ Respeita horário de funcionamento
- ✅ Impede agendamentos em datas passadas

### 5.5 Design e UX
- ✅ Tema minimalista "Navalha & Concreto"
- ✅ Paleta: Moss, Sand, Clay
- ✅ Totalmente responsivo (mobile-first)
- ✅ Menu hamburguer mobile
- ✅ Animações GSAP
- ✅ Loading states
- ✅ Flash messages
- ✅ Confirmações de ação

---

## 6. Decisões de Design

### 6.1 Paleta de Cores
```css
--moss: #1A2318      /* Background principal */
--sand: #EAE6D7      /* Texto e elementos claros */
--clay: #BC5D2E      /* Accent color (laranja) */
--surface: #232E21   /* Cards e containers */
```

**Conceito:** Estética masculina, artesanal, "Navalha & Concreto" - transmite solidez e sofisticação.

### 6.2 Tipografia
- **Display (Syne):** Títulos - moderna, bold, impactante
- **Body (Manrope):** Corpo - legível, limpa, profissional
- **Mono:** Dados técnicos - datas, horários, status

### 6.3 Responsividade
```
Mobile: < 768px  (1 coluna, menu hamburguer)
Tablet: 768px+   (2 colunas, nav expandido)
Desktop: 1024px+ (3-4 colunas, espaçamento amplo)
```

---

## 7. Segurança Implementada

### 7.1 Autenticação
- ✅ Senhas com hash bcrypt
- ✅ Salt automático por senha
- ✅ Sessões com SECRET_KEY
- ✅ Cookies assinados

### 7.2 Autorização
- ✅ Verificação de permissões por rota
- ✅ Clientes não acessam admin
- ✅ Validação de ownership (cliente só vê seus agendamentos)

### 7.3 Validação de Dados
- ✅ Validação server-side
- ✅ Sanitização de inputs
- ✅ Prevenção de SQL Injection (ORM)
- ✅ CSRF implícito (POST forms)

### 7.4 Regras de Negócio
- ✅ Não permite agendar com menos de 30min antecedência
- ✅ Não permite cancelar com menos de 2h antecedência
- ✅ Valida sobreposição de horários
- ✅ Respeita bloqueios de agenda

---

## 8. Performance e Otimizações

### 8.1 Banco de Dados
- ✅ Pool de conexões configurado
- ✅ Pre-ping para detectar conexões mortas
- ✅ Índices em campos chave (email, data, cliente_id)
- ✅ Queries otimizadas com joins

### 8.2 Frontend
- ✅ CSS utility-first (Tailwind) - menor bundle
- ✅ Font loading otimizado
- ✅ Lazy loading implícito
- ✅ Animações GPU-accelerated (GSAP)

### 8.3 Servidor
- ✅ Gunicorn com múltiplos workers
- ✅ Pool size ajustado para free tier
- ✅ Timeout configurado

---

## 9. Deploy

### 9.1 Ambiente de Produção
- **Plataforma:** Render.com
- **Servidor:** Gunicorn
- **Banco:** PostgreSQL (Supabase)
- **HTTPS:** Automático via Render

### 9.2 Variáveis de Ambiente
```env
SECRET_KEY=<chave-secreta>
DATABASE_URL=postgresql://...
```

### 9.3 Processo de Deploy
1. Push para repositório Git
2. Render detecta mudanças
3. Instala dependências (requirements.txt)
4. Executa build commands
5. Inicia Gunicorn
6. Deploy automático

---

## 10. Possíveis Melhorias Futuras

### 10.1 Funcionalidades
- [ ] Integração Mercado Pago (pagamento online)
- [ ] Sistema de avaliações
- [ ] Notificações por email/SMS
- [ ] Lembretes automáticos
- [ ] Programa de fidelidade
- [ ] Múltiplos barbeiros
- [ ] Relatórios financeiros
- [ ] API REST

### 10.2 Técnicas
- [ ] Testes automatizados (pytest)
- [ ] CI/CD pipeline
- [ ] Cache (Redis)
- [ ] CDN para assets
- [ ] Monitoring (Sentry)
- [ ] Logs estruturados
- [ ] Docker containerization

---

## 11. Conclusão

O sistema **Corte Certo** foi desenvolvido com tecnologias modernas, práticas de segurança adequadas e foco em experiência do usuário. A escolha de Flask oferece simplicidade e rapidez no desenvolvimento, enquanto PostgreSQL garante robustez e escalabilidade. O design minimalista com Tailwind CSS resulta em uma interface profissional e responsiva.

A arquitetura MVC mantém o código organizado e manutenível, e o sistema de autenticação/autorização protege adequadamente os dados dos usuários. As validações de regras de negócio (horários, antecedências, bloqueios) garantem o funcionamento correto do sistema de agendamentos.

O projeto está pronto para produção e pode ser facilmente expandido com novas funcionalidades conforme a necessidade do negócio.

---

**Desenvolvedor:** Grupo Corte Certo 
**Data:** Novembro 2025  
**Versão:** 1.0  
