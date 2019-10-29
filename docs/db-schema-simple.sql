CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);

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
    date_joined timestamp with time zone NOT NULL
);

CREATE TABLE public.auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);

CREATE TABLE public.auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
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

CREATE TABLE public.crypto_currencywallet (
    owner_id integer NOT NULL,
    amount numeric(19,2) NOT NULL
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

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);

