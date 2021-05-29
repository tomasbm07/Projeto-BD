----------------------------------
--------------TABELAS-------------
----------------------------------

CREATE TABLE utilizador (
	userid	 SERIAL,
	username	 VARCHAR(512) UNIQUE NOT NULL,
	email	 VARCHAR(512) UNIQUE NOT NULL,
	password	 VARCHAR(512) NOT NULL,
	nome	 VARCHAR(512),
	morada	 VARCHAR(512),
	mensagens_id INTEGER,
	PRIMARY KEY(userid)
);

CREATE TABLE leilao (
	id		 SERIAL,
	titulo		 VARCHAR(512) NOT NULL,
	descricao	 VARCHAR(1024),
	precomin		 INTEGER NOT NULL,
	precoatual	 INTEGER NOT NULL DEFAULT 0,
	data		 TIMESTAMP NOT NULL,
	artigos_id	 INTEGER NOT NULL,
	utilizador_userid INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE artigos (
	id	 SERIAL,
	nome	 VARCHAR(512) NOT NULL,
	descricao VARCHAR(1024),
	PRIMARY KEY(id)
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
	id		 SERIAL,
	valor		 INTEGER NOT NULL,
	data		 TIMESTAMP NOT NULL DEFAULT NOW(),
	leilao_id	 INTEGER,
	utilizador_userid INTEGER,
	PRIMARY KEY(id,leilao_id,utilizador_userid)
);

CREATE TABLE authtokens (
	token		 VARCHAR(1024) UNIQUE NOT NULL,
	time_created	 TIMESTAMP NOT NULL DEFAULT NOW(),
	utilizador_userid INTEGER NOT NULL,
	PRIMARY KEY(token)
);

CREATE TABLE mensagens (
	id	 SERIAL,
	mensagem VARCHAR(1024),
	PRIMARY KEY(id)
);
CREATE TABLE historico (
	titulo	 VARCHAR(512) NOT NULL,
	descricao	 VARCHAR(512),
	precomin	 INTEGER NOT NULL,
	dataacaba	 TIMESTAMP NOT NULL,
	dataalteracao TIMESTAMP NOT NULL DEFAULT NOW(),
	leilao_id	 INTEGER,
	PRIMARY KEY(dataalteracao,leilao_id)
);


ALTER TABLE utilizador ADD CONSTRAINT utilizador_fk1 FOREIGN KEY (mensagens_id) REFERENCES mensagens(id);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (artigos_id) REFERENCES artigos(id);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE authtokens ADD CONSTRAINT authtokens_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);

ALTER TABLE authTokens ADD CONSTRAINT autenticado_fk1 FOREIGN KEY (userid) REFERENCES utilizador(userid);
ALTER TABLE historico ADD CONSTRAINT historico_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);

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


---------------------------------------------------------
--------------FUNÇOES/PROCEDIMENTOS/TRIGGERS-------------
---------------------------------------------------------

--Função que devolve o username apartir de um userid
create or replace FUNCTION get_username_from_id(id utilizador.userid%type) returns utilizador.nome%type
language plpgsql
as $$
DECLARE
v_username utilizador.nome%type;
BEGIN
	SELECT username FROM utilizador WHERE userid = id INTO v_username;
	return v_username;
END;
$$;

--Função que devolve o username apartir de um token
create or replace FUNCTION get_username_from_token(p_token authTokens.token%type) returns utilizador.username%type
language plpgsql
as $$
DECLARE
v_userid utilizador.userid%type;
v_username utilizador.username%type;
BEGIN
	SELECT userid FROM authTokens WHERE token = p_token INTO v_userid;
	SELECT * FROM get_username_from_id(v_userid) INTO v_username;
	return v_username;
END;
$$;

--ATUALIZAR PRECO TABELA LEILAO NO FIM DE ADICIONAR ENTRADA NA TABELA LICITACAO
create or replace function atualiza_preco_leilao()
returns trigger
language plpgsql
as $$
declare
	c1 cursor for
		select leilao_id, valor from licitacao where id = (select last_value from licitacao_id_seq);
	v_valor INTEGER;
	v_leilao_id INTEGER;
begin
	open c1;
	fetch c1 into
	v_leilao_id, v_valor;
	UPDATE leilao
	SET precoatual = v_valor
	WHERE id = v_leilao_id;
	return new;
end;
$$;

CREATE trigger trigger_atualizar_precoatual
AFTER INSERT ON licitacao
for each ROW
EXECUTE PROCEDURE atualiza_preco_leilao();


--GUARDAR SNAPSHOT DE LEILAO DEPOIS DE SER EDITADO
CREATE OR REPLACE FUNCTION guarda_historico_leilao()
returns trigger
language plpgsql
as $$
begin
	INSERT INTO historico (titulo, descricao, precomin, dataacaba, leilao_id) VALUES (old.titulo, old.descricao, old.precomin, old.data, old.id);
	return new;
end;
$$;

create trigger trigger_guardar_historico
after update on leilao
for each row
execute procedure guarda_historico_leilao();

----------------
