create trigger trigger_enviar_notificacao_mensagem
after insert or update on comentario
for each row
execute procedure enviar_notificacao_mensagem();

create or replace function enviar_notificacao_mensagem()
returns trigger
language plpgsql
as $$
declare
	user_id integer;
	titulo_leilao leilao.titulo%type := (select titulo from leilao where id = new.leilao_id);
begin
	for user_id in select utilizador_userid from comentario where leilao_id = new.leilao_id
	LOOP
		insert into mensagens (mensagem, leilao_id, utilizador_userid) values (CONCAT('New message on ', titulo_leilao), new.leilao_id, user_id);
	END LOOP;
	return new;
end;
$$;
