CREATE AGGREGATE sum (hll)
(
  sfunc = hll_union_trans,
  stype = internal,
  finalfunc = hll_pack
);

CREATE OR REPLACE FUNCTION hstore_merge(left HSTORE, right HSTORE) RETURNS HSTORE AS $$
  SELECT coalesce($1, '') || coalesce($2, '');
  $$ LANGUAGE SQL;

CREATE AGGREGATE hstore_merge (HSTORE) (
    SFUNC = hstore_merge,
    STYPE = HSTORE,
    INITCOND = ''
);

--select create_jsonb_flat_view('example', 'id, name', 'params');
create or replace function create_jsonb_flat_view
    (table_name text, regular_columns text, json_column text)
    returns text language plpgsql as $$
declare
    cols text;
begin
    execute format ($ex$
        select string_agg(format('%2$s->>%%1$L "%%1$s"', key), ', ')
        from (
            select distinct key
            from %1$s, jsonb_each(%2$s)
            order by 1
            ) s;
        $ex$, table_name, json_column)
    into cols;
    execute format($ex$
        drop view if exists %1$s_view;
        create view %1$s_view as
        select %2$s, %3$s from %1$s
        $ex$, table_name, regular_columns, cols);
    return cols;
end $$;

create table tokens(context text, name text, value text);

create table contents(name text, data text);

create table pgsql_prompts (
 keyword text unique
);

create index pgsql_prompts_idx on pgsql_prompts using gist(keyword gist_trgm_ops);
insert into pgsql_prompts (keyword)
    values ('select'), ('from'), ('table'),
    ('create'), ('update'), ('count'), ('distinct');

create table prompts_ngrams(ngram text unique, freq int);
CREATE INDEX prompts_ngram_idx  ON prompts_ngrams USING GIN (to_tsvector('english', ngram));

-- select ngram from prompts_ngrams where tsquery('charges' || ':*') @@ to_tsvector(ngram)  limit 10
