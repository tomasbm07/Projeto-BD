create trigger trigger_atualizar_precoatual
after insert on licitacao
for each row
execute procedure atualiza_preco_leilao();

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
	precoatual = v_valor
	WHERE id = v_leilao_id;
	return new;
end;
$$;
