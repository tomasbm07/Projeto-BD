SET TIMEZONE='Portugal';

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
	PRIMARY KEY(userid)
);

CREATE TABLE leilao (
	id		 SERIAL,
	titulo		 VARCHAR(512) NOT NULL,
	descricao	 VARCHAR(1024),
	precomin		 INTEGER NOT NULL,
	precoatual	 INTEGER NOT NULL DEFAULT 0,
	id_vencedor	 INTEGER,
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
	leilao_id	 INTEGER,
	utilizador_userid INTEGER,
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



ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (artigos_id) REFERENCES artigos(id);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE authtokens ADD CONSTRAINT authtokens_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE historico ADD CONSTRAINT historico_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE mensagens ADD CONSTRAINT mensagens_fk1 FOREIGN KEY (leilao_id) REFERENCES leilao(id);
ALTER TABLE mensagens ADD CONSTRAINT mensagens_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);

----------------------------------
--------------ARTIGOS-------------	
----------------------------------

INSERT INTO artigos (nome, descricao) VALUES ('PS5', '');
INSERT INTO artigos (nome, descricao) VALUES ('Batata', '');
INSERT INTO artigos (nome, descricao) VALUES ('Torradeira', '');
INSERT INTO artigos (nome, descricao) VALUES ('Gaming PC', '');
INSERT INTO artigos (nome, descricao) VALUES ('Sof??', '');
INSERT INTO artigos (nome, descricao) VALUES ('Ryzen 9 5950X', '');
INSERT INTO artigos (nome, descricao) VALUES ('ROG RTX 3090', '');
INSERT INTO artigos (nome, descricao) VALUES ('EVGA RTX 3080', '');
INSERT INTO artigos (nome, descricao) VALUES ('NVIDIA RTX 3060', '');
INSERT INTO artigos (nome, descricao) VALUES ('Intel Core i9-11900K', '');
INSERT INTO artigos (nome, descricao) VALUES ('MSI X570-A PRO', '');


---------------------------------------------------------
--------------FUN??OES/PROCEDIMENTOS/TRIGGERS-------------
---------------------------------------------------------

--Fun????o que devolve o username apartir de um userid
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


--Fun????o que devolve o username apartir de um token
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
WHEN (OLD.titulo    IS DISTINCT FROM NEW.titulo
   OR OLD.descricao IS DISTINCT FROM NEW.descricao
   OR OLD.precomin IS DISTINCT FROM NEW.precomin
   OR OLD.data IS DISTINCT FROM NEW.data)
execute procedure guarda_historico_leilao();


--NOTIFICACAO BID ULTRAPASSADA
create or replace function enviar_notificacao_bid_ultrapassada()
returns trigger
language plpgsql
as $$
declare
	c100 cursor for
		select utilizador_userid from licitacao where leilao_id = new.leilao_id and data = (select max(data) from licitacao where leilao_id=new.leilao_id and data < (select max(data) from licitacao));
	v_userid INTEGER;
begin
	open c100;
	fetch c100
	into v_userid;
	if (v_userid != 0) then
		insert into mensagens (mensagem, leilao_id, utilizador_userid) values ('Your bid has been overtaked!', new.leilao_id, v_userid);
	end if;
	return new;
end;
$$;

create trigger trigger_guardar_historico
after insert on licitacao
for each row
execute procedure enviar_notificacao_bid_ultrapassada();


--NOTIFICACAO DE MENSAGENS PARA TODOS OS UTILIZADORES QUE PARTICIPEM NO MURAL DE UM LEILAO
create or replace function enviar_notificacao_mensagem()
returns trigger
language plpgsql
as $$
declare
	user_id integer;
	titulo_leilao leilao.titulo%type := (select titulo from leilao where id = new.leilao_id);
	owner_leilao leilao.utilizador_userid%type := (select utilizador_userid from leilao where id = new.leilao_id);
begin
	for user_id in select utilizador_userid from comentario where leilao_id = new.leilao_id and utilizador_userid != new.utilizador_userid
	LOOP
		insert into mensagens (mensagem, leilao_id, utilizador_userid) values (CONCAT('New message on ', titulo_leilao), new.leilao_id, user_id);
	END LOOP;
	insert into mensagens (mensagem, leilao_id, utilizador_userid) values (CONCAT('New message on your auction, ', titulo_leilao), new.leilao_id, owner_leilao);
	return new;
end;
$$;

create trigger trigger_enviar_notificacao_mensagem
after insert or update on comentario
for each row
execute procedure enviar_notificacao_mensagem();


--NOTIFICACAO DE FIM DE LEILAO
create or replace function envia_notificacao_fim_leilao()
returns trigger
language plpgsql
as $$
declare
	user_id integer;
	titulo_leilao leilao.titulo%type := (select titulo from leilao where id = new.id);
	owner_leilao leilao.utilizador_userid%type := (select utilizador_userid from leilao where id = new.id);
begin
	for user_id in select utilizador_userid from licitacao where leilao_id = new.id
	LOOP
		insert into mensagens (mensagem, leilao_id, utilizador_userid) values (CONCAT('Auction ', titulo_leilao, ' ended!'), new.id, user_id);
	END LOOP;
	insert into mensagens (mensagem, leilao_id, utilizador_userid) values (CONCAT('Your auction, ', titulo_leilao, ' ended!'), new.id, owner_leilao);
	return new;
end;
$$;

create trigger trigger_notificacao_fim_leilao
after update on leilao
for each row
WHEN (OLD.id_vencedor    IS DISTINCT FROM NEW.id_vencedor)
execute procedure envia_notificacao_fim_leilao();
