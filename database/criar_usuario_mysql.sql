-- Execute como administrador no MySQL.
-- Troque a senha de exemplo antes de executar.
CREATE USER IF NOT EXISTS 'appy_user'@'localhost' IDENTIFIED BY 'TroqueEstaSenha_123!';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP
  ON appy_db.* TO 'appy_user'@'localhost';
FLUSH PRIVILEGES;

-- Se a aplicação for executada dentro de Docker, o host do usuário precisa
-- ser compatível com a rede do container. Nesse caso, use o docker-compose.yml
-- fornecido, que cria um usuário restrito ao banco APPY para a rede do Compose.
