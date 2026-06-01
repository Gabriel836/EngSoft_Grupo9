# Sistema de Turismo - Banco de Dados

## Descrição

Este repositório contém a implementação inicial do banco de dados para um sistema de gerenciamento de informações hoteleiras de Olímpia (SP)

O banco foi desenvolvido utilizando PostgreSQL e modelado a partir de um Modelo Entidade-Relacionamento (MER).

## Tecnologias Utilizadas

* PostgreSQL
* SQL

## Estrutura do Projeto

```text
.
├── main.sql
├── LICENSE
└── README.md
```

* `main.sql`: script de criação do banco de dados.

## Instalação do PostgreSQL

### Debian / Ubuntu

Atualize os pacotes:

```bash
sudo apt update
```

Instale o PostgreSQL:

```bash
sudo apt install postgresql
```

Verifique se o serviço está ativo:

```bash
sudo systemctl status postgresql
```

Caso necessário:

```bash
sudo systemctl start postgresql
```

## Criação do Banco de Dados

Criar o banco:

```bash
sudo -u postgres createdb turismo
```

Verificar se foi criado:

```bash
sudo -u postgres psql -l
```

## Execução do Script SQL

Execute o script de criação das tabelas:

```bash
sudo -u postgres psql turismo < turismo.sql
```

Se a execução for bem sucedida, o PostgreSQL exibirá mensagens semelhantes a:

```text
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
```

## Verificação das Tabelas

Acessar o banco:

```bash
sudo -u postgres psql turismo
```

Listar as tabelas:

```sql
\dt
```

Ver a estrutura de uma tabela:

```sql
\d usuario
```

Sair do PostgreSQL:

```sql
\q
```

## Entidades Implementadas

### Usuario

Armazena credenciais e informações básicas de acesso.

### Empresa

Representa usuários do tipo empresa.

### Funcionario

Representa usuários do tipo funcionário da secretaria.

### Dados_Empresa

Armazena informações mensais enviadas pelas empresas, como:

* Ano
* Mês
* Número de leitos
* Número de leitos ocupados
* Valor médio dos leitos

## Autores

Projeto desenvolvido para a disciplina de Engenharia de Software
