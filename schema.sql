drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  name text not null,
  why text not null,
  fun text not null
);
