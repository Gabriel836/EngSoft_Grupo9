-- =====================================
-- TABELA USUARIO
-- =====================================

CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,

    login VARCHAR(50) UNIQUE NOT NULL,

    senha_hash VARCHAR(255) NOT NULL,

    tipo VARCHAR(20) NOT NULL
        CHECK (UPPER(tipo) IN ('EMPRESA', 'FUNCIONARIO'))
);

-- =====================================
-- TABELA FUNCIONARIO
-- =====================================

CREATE TABLE funcionario (
    id_usuario INTEGER PRIMARY KEY,

    cpf CHAR(11) UNIQUE NOT NULL,

    CONSTRAINT fk_funcionario_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

-- =====================================
-- TABELA EMPRESA
-- =====================================

CREATE TABLE empresa (
    id_usuario INTEGER NOT NULL,

    cnpj CHAR(14) UNIQUE NOT NULL,

    nome_empresa VARCHAR(255) NOT NULL,

    CONSTRAINT pk_empresa PRIMARY KEY (id_usuario, cnpj),

    CONSTRAINT fk_empresa_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

-- =====================================
-- TABELA DADOS DA EMPRESA
-- =====================================

CREATE TABLE dados_empresa (
    id_dados SERIAL PRIMARY KEY,

    id_empresa INTEGER NOT NULL,

    datas DATE NOT NULL,

    nro_leitos INTEGER NOT NULL
        CHECK (nro_leitos >= 0),

    nro_leitos_ocupados INTEGER NOT NULL
        CHECK (
            nro_leitos_ocupados >= 0
            AND nro_leitos_ocupados <= nro_leitos
        ),

    valor_leito NUMERIC(10,2) NOT NULL
        CHECK (valor_leito >= 0),

    id_usuario_modificador INTEGER NOT NULL,

    CONSTRAINT fk_dados_empresa
        FOREIGN KEY (id_empresa)
        REFERENCES empresa(id_usuario),

    CONSTRAINT fk_modificador
        FOREIGN KEY (id_usuario_modificador)
        REFERENCES usuario(id_usuario),

    CONSTRAINT unq_empresa_data
        UNIQUE (id_empresa, datas)
);-- =====================================
-- TABELA USUARIO
-- =====================================

CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,

    login VARCHAR(50) UNIQUE NOT NULL,

    senha_hash VARCHAR(255) NOT NULL,

    tipo VARCHAR(20) NOT NULL
        CHECK (UPPER(tipo) IN ('EMPRESA', 'FUNCIONARIO'))
);

-- =====================================
-- TABELA FUNCIONARIO
-- =====================================

CREATE TABLE funcionario (
    id_usuario INTEGER PRIMARY KEY,

    cpf CHAR(11) UNIQUE NOT NULL,

    CONSTRAINT fk_funcionario_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

-- =====================================
-- TABELA EMPRESA
-- =====================================

CREATE TABLE empresa (
    id_usuario INTEGER PRIMARY KEY,

    cnpj CHAR(14) UNIQUE NOT NULL,

    CONSTRAINT fk_empresa_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

-- =====================================
-- TABELA DADOS DA EMPRESA
-- =====================================

CREATE TABLE dados_empresa (
    id_dados SERIAL PRIMARY KEY,

    id_empresa INTEGER NOT NULL,

    ano INTEGER NOT NULL,

    mes INTEGER NOT NULL
        CHECK (mes BETWEEN 1 AND 12),

    nro_leitos INTEGER NOT NULL
        CHECK (nro_leitos >= 0),

    nro_leitos_ocupados INTEGER NOT NULL
        CHECK (
            nro_leitos_ocupados >= 0
            AND nro_leitos_ocupados <= nro_leitos
        ),

    valor_leito NUMERIC(10,2) NOT NULL
        CHECK (valor_leito >= 0),

    id_usuario_modificador INTEGER NOT NULL,

    CONSTRAINT fk_dados_empresa
        FOREIGN KEY (id_empresa)
        REFERENCES empresa(id_usuario),

    CONSTRAINT fk_modificador
        FOREIGN KEY (id_usuario_modificador)
        REFERENCES usuario(id_usuario),

    CONSTRAINT unq_empresa_periodo
        UNIQUE (id_empresa, ano, mes)
);
