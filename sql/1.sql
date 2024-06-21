CREATE TABLE public.orders (
	type_battery varchar(40) NULL,
	size_battery varchar(40) NULL,
	createdate varchar(40) NULL
);

INSERT INTO public.orders (type_battery, size_battery, createdate) 
VALUES ('ионный', '200', date_trunc('second', now()) ) ;