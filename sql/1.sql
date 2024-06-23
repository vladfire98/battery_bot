CREATE TABLE public.orders (
	order_id    serial primary key,
	type_battery varchar(40) NULL,
	size_battery varchar(40) NULL,
	voltage_battery int4 null,
	lenghts_battery int4 null,
	FIO	varchar(40) null,
	number_phone varchar(40) null,
	createdate date NULL
);

CREATE TABLE public.elements (
	element_type varchar(40) not NULL
);