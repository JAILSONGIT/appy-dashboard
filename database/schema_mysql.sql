-- Esquema do banco APPY Dashboard para MySQL 8.0 ou superior.
-- Execute conectado ao MySQL com um usuário administrador.
CREATE DATABASE IF NOT EXISTS appy_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE appy_db;

CREATE TABLE IF NOT EXISTS produtos (
  id INT NOT NULL AUTO_INCREMENT,
  codigo INT NULL,
  nome VARCHAR(255) NOT NULL,
  entradas INT NOT NULL DEFAULT 0,
  devolvido INT NOT NULL DEFAULT 0,
  nao_devolvido INT NOT NULL DEFAULT 0,
  reformar INT NOT NULL DEFAULT 0,
  estoque INT NOT NULL DEFAULT 0,
  descarte INT NOT NULL DEFAULT 0,
  setor VARCHAR(120) NOT NULL DEFAULT 'INTERLAGOS',
  PRIMARY KEY (id),
  INDEX ix_produtos_codigo (codigo),
  INDEX ix_produtos_nome (nome)
) ENGINE=InnoDB;

-- O SQLAlchemy também cria a tabela automaticamente ao iniciar a aplicação.
-- Este arquivo permite preparar/verificar o banco manualmente.
