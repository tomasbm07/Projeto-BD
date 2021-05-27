----------------------------------
--------------TABELAS-------------
----------------------------------

CREATE TABLE utilizador (
	userid	 	SERIAL,
	username 	VARCHAR(512) UNIQUE NOT NULL,
	email	 	VARCHAR(512) UNIQUE NOT NULL,
	password 	VARCHAR(512) NOT NULL,
	nome	 	VARCHAR(512),
	morada	 	VARCHAR(512),
	PRIMARY KEY(userid)
);

CREATE TABLE leilao (
	id		 			SERIAL,
	titulo		 		VARCHAR(512) NOT NULL,
	descricao	 		VARCHAR(8192),
	precomin			INTEGER NOT NULL,
	precoatual	 		INTEGER NOT NULL DEFAULT 0,
	data		 		TIMESTAMP NOT NULL,
	artigos_artigoid	INTEGER NOT NULL,
	utilizador_userid 	INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE artigos (
	id	 			SERIAL,
	nome	 		VARCHAR(512) NOT NULL,
	descricao 		VARCHAR(2048),
	PRIMARY KEY(id)
);

CREATE TABLE comentario (
	id		 			SERIAL,
	comentario	 		VARCHAR(512) NOT NULL,
	resposta		 	VARCHAR(512),
	leilao_id	 		INTEGER,
	utilizador_userid 	INTEGER,
	PRIMARY KEY(id,leilao_id,utilizador_userid)
);

CREATE TABLE licitacao (
	id		 			SERIAL,
	valor		 		INTEGER NOT NULL,
	data		 		TIMESTAMP NOT NULL,
	leilao_id	 		INTEGER,
	utilizador_userid 	INTEGER,
	PRIMARY KEY(id,leilao_id,utilizador_userid)
);

CREATE TABLE authTokens (
	userid 			INTEGER,
	token		 	VARCHAR(1024) UNIQUE NOT NULL,
	time_created	TIMESTAMP NOT NULL DEFAULT NOW(), 
	PRIMARY KEY(userid)
);


ALTER TABLE leilao ADD CONSTRAINT leilao_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE authTokens ADD CONSTRAINT autenticado_fk1 FOREIGN KEY (userid) REFERENCES utilizador(userid);

----------------------------------
--------------ARTIGOS-------------
----------------------------------

INSERT INTO artigos (nome, descricao) VALUES ('PS5', '');
INSERT INTO artigos (nome, descricao) VALUES ('Batata', '');
INSERT INTO artigos (nome, descricao) VALUES ('Torradeira', '');
INSERT INTO artigos (nome, descricao) VALUES ('Gaming PC', '');
INSERT INTO artigos (nome, descricao) VALUES ('Sofá', '');
INSERT INTO artigos (nome, descricao) VALUES ('Ryzen 9 5950X', '');
INSERT INTO artigos (nome, descricao) VALUES ('ROG RTX 3090', '');
INSERT INTO artigos (nome, descricao) VALUES ('EVGA RTX 3080', '');
INSERT INTO artigos (nome, descricao) VALUES ('NVIDIA RTX 3060', '');
INSERT INTO artigos (nome, descricao) VALUES ('Intel Core i9-11900K', '');
INSERT INTO artigos (nome, descricao) VALUES ('MSI X570-A PRO', '');
