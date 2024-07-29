create database fin_doc_sum
    with owner root;

create table public.documents
(
    document_id   uuid default gen_random_uuid(),
    title         varchar,
    ticker        varchar,
    document_type varchar,
    year          varchar,
    tokens        integer,
    src_url       varchar,
    doc           text
);

alter table public.documents
    owner to root;

