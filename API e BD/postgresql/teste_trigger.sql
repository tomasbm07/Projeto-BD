create trigger trigger_notificacao_fim_leilao
after update on leilao
for each row
WHEN (OLD.id_vencedor    IS DISTINCT FROM NEW.id_vencedor)
execute procedure envia_notificacao_fim_leilao();

create or replace function envia_notificacao_fim_leilao()
returns trigger
language plpgsql
as $$
declare
	user_id integer;
	titulo_leilao leilao.titulo%type := (select titulo from leilao where id = new.leilao_id);
begin
	for user_id in select utilizador_userid from licitacao where leilao_id = new.leilao_id
	LOOP
		insert into mensagens (mensagem, leilao_id, utilizador_userid) values (CONCAT('Auction ', titulo_leilao, ' ended!'), new.leilao_id, user_id);
	END LOOP;
	return new;
end;
$$;
