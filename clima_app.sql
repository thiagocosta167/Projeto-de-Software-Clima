CREATE DATABASE clima_app;
USE clima_app;

CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL
);

CREATE TABLE pesquisas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT,
    cidade VARCHAR(255) NOT NULL,
    data_pesquisa DATETIME DEFAULT CURRENT_TIMESTAMP,
    resultado TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
