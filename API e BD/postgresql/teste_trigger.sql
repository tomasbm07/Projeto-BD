create trigger trigger_atualizar_precoatual
after insert on licitacao
for each row
execute procedure atualiza_preco_leilao();

create or replace function ex3()
returns trigger
language plpgsql
as $$
		
begin
	
end;
$$;
