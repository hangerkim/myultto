drop table if exists results;
create table results (
    id integer primary key autoincrement,
    created_at text not null,
    candidates text not null,
    winners text not null,
    seed integer not null
);
