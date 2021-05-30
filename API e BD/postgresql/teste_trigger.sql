create trigger trigger_guardar_historico
after insert on licitacao
for each row
execute procedure enviar_notificacao_bid_ultrapassada();

create or replace function enviar_notificacao_bid_ultrapassada()
returns trigger
language plpgsql
as $$
begin
	insert into mensagens (mensagem, leilao_id, utilizador_userid) values ('Your bid has been overtaked!', new.leilao_id, new.utilizador_userid);
	return new;
end;
$$;
