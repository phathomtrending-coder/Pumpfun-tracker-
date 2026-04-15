create table if not exists posted_events (
  id bigint generated always as identity primary key,
  token_address text not null,
  token_symbol text,
  event_type text not null,
  destination text not null,
  created_at timestamptz default now()
);

create index if not exists idx_posted_events_token_address
on posted_events (token_address);

create index if not exists idx_posted_events_event_type
on posted_events (event_type);

create unique index if not exists uniq_posted_events_token_event_destination
on posted_events (token_address, event_type, destination);
