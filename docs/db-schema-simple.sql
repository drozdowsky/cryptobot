CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
	amount numeric(19,2) NOT NULL
);

CREATE TABLE public.crypto_cryptomodel (
    id integer NOT NULL,
    short_name character varying(11) NOT NULL,
    long_name character varying(32) NOT NULL
);

CREATE TABLE public.crypto_cryptowallet (
    id integer NOT NULL,
    amount numeric(19,8) NOT NULL,
    crypto_id integer NOT NULL,
    owner_id integer NOT NULL,
    date timestamp with time zone NOT NULL
);

CREATE TABLE public.crypto_markethistoric (
    id integer NOT NULL,
    price numeric(19,2) NOT NULL,
    response_json jsonb NOT NULL,
    date timestamp with time zone NOT NULL,
    crypto_id integer NOT NULL,
    asks_value double precision NOT NULL,
    avg_transaction_value double precision NOT NULL,
    bids_value double precision NOT NULL
);

CREATE TABLE public.crypto_rule (
    id integer NOT NULL,
    value double precision NOT NULL,
    type_of_rule character varying(3) NOT NULL,
    rule_set_id integer NOT NULL
);

CREATE TABLE public.crypto_ruleset (
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    type_of_ruleset character varying(1) NOT NULL,
    crypto_id integer NOT NULL,
    owner_id integer NOT NULL
);

CREATE TABLE public.crypto_socialhistoric (
    id integer NOT NULL,
    date timestamp with time zone NOT NULL,
    crypto_id integer NOT NULL,
    gtrends_top_7d double precision NOT NULL
);

CREATE TABLE public.crypto_trade (
    id integer NOT NULL,
    date timestamp with time zone NOT NULL,
    type_of_trade character varying(1) NOT NULL,
    amount numeric(19,8) NOT NULL,
    price numeric(19,2) NOT NULL,
    rule_set_id integer
);
