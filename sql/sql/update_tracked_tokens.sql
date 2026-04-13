create table if not exists board_state (
  id bigint generated always as identity primary key,
  board_name text unique not null,
  last_posted_at timestamptz
);

sql
