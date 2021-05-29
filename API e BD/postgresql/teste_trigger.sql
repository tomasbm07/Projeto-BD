create trigger trigger_guardar_historico
after update on leilao
for each row
execute procedure guarda_historico_leilao();

create or replace function guarda_historico_leilao()
returns trigger
language plpgsql
as $$
begin
	insert into historico (titulo, descricao, precomin, dataacaba, leilao_id) values (old.titulo, old.descricao, old.precomin, old.data, old.id);
	return new;
end;
$$;
