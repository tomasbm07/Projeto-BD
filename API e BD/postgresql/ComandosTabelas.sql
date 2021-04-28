CREATE TABLE utilizador (
	userid	 SERIAL,
	username VARCHAR(512) UNIQUE NOT NULL,
	email	 VARCHAR(512) UNIQUE NOT NULL,
	password VARCHAR(512) NOT NULL,
	nome	 VARCHAR(512),
	morada	 VARCHAR(512),
	PRIMARY KEY(userid)
);

CREATE TABLE leilao (
	id		 	 SERIAL,
	titulo		 VARCHAR(512) NOT NULL,
	descricao	 VARCHAR(8192),
	precomin		 INTEGER NOT NULL,
	precoatual	 INTEGER NOT NULL DEFAULT 0,
	idutlizador	 INTEGER,
	data		 TIMESTAMP NOT NULL,
	artigos_artigoid	 INTEGER NOT NULL,
	utilizador_userid INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE artigos (
	artigoid	 SERIAL,
	nome	 VARCHAR(512) NOT NULL,
	descricao VARCHAR(2048),
	PRIMARY KEY(artigoid)
);

CREATE TABLE comentario (
	id		 SERIAL,
	comentario	 VARCHAR(512) NOT NULL,
	resposta		 VARCHAR(512),
	leilao_id	 INTEGER,
	utilizador_userid INTEGER,
	PRIMARY KEY(id,leilao_id,utilizador_userid)
);

CREATE TABLE licitacao (
	idlicitacao	 SERIAL,
	valorlicitacao	 INTEGER NOT NULL,
	data		 TIMESTAMP NOT NULL,
	leilao_id	 INTEGER,
	utilizador_userid INTEGER,
	PRIMARY KEY(idlicitacao,leilao_id,utilizador_userid)
);


ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (artigos_artigoid) REFERENCES artigos(artigoid);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);

INSERT INTO utilizador (username, email, password) VALUES 'admin', 'admin@projetobd.pt', 'password';
