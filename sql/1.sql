CREATE TABLE public.orders (
	order_id    serial primary key,
	type_battery varchar(40) NULL,
	size_battery varchar(40) NULL,
	createdate date NULL
);