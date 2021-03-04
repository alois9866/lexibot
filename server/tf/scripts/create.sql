create table links
(
    id         serial primary key, /* todo: consider making id non-numeric, so it would be harder to manually change statistics */
    chat_id    varchar(20)  not null,
    word       varchar(50)  not null,
    start_date date         not null,
    end_date   date         not null,
    provider   varchar(120) not null,
    clicks     integer      not null default 0
);

create table bots
(
    token uuid primary key
)