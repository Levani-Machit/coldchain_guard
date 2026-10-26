-- Table: public.storage_locations

-- DROP TABLE IF EXISTS public.storage_locations;

CREATE TABLE IF NOT EXISTS public.storage_locations
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name text COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    is_active boolean NOT NULL DEFAULT true,
    CONSTRAINT storage_locations_pkey PRIMARY KEY (id),
    CONSTRAINT storage_locations_name_key UNIQUE (name)
);

-- Table: public.sensors

-- DROP TABLE IF EXISTS public.sensors;

CREATE TABLE IF NOT EXISTS public.sensors
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    storage_location_id integer NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    identifier text COLLATE pg_catalog."default" NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    installed_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT sensors_pkey PRIMARY KEY (id),
    CONSTRAINT sensors_identifier_key UNIQUE (identifier),
    CONSTRAINT sensors_storage_location_id_fkey FOREIGN KEY (storage_location_id)
        REFERENCES public.storage_locations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
);

-- Table: public.batches

-- DROP TABLE IF EXISTS public.batches;

CREATE TABLE IF NOT EXISTS public.batches
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    product_name text COLLATE pg_catalog."default" NOT NULL,
    batch_number text COLLATE pg_catalog."default" NOT NULL,
    storage_location_id integer NOT NULL,
    min_temperature numeric NOT NULL,
    max_temperature numeric NOT NULL,
    stored_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT batches_pkey PRIMARY KEY (id),
    CONSTRAINT batches_batch_number_key UNIQUE (batch_number),
    CONSTRAINT batches_storage_location_id_fkey FOREIGN KEY (storage_location_id)
        REFERENCES public.storage_locations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE RESTRICT,
    CONSTRAINT batches_check CHECK (min_temperature < max_temperature)
);

-- Table: public.temperature_readings

-- DROP TABLE IF EXISTS public.temperature_readings;

CREATE TABLE IF NOT EXISTS public.temperature_readings
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    sensor_id integer NOT NULL,
    temperature numeric NOT NULL,
    recorded_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT temperature_readings_pkey PRIMARY KEY (id),
    CONSTRAINT temperature_readings_sensor_id_fkey FOREIGN KEY (sensor_id)
        REFERENCES public.sensors (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
);

-- Table: public.violations

-- DROP TABLE IF EXISTS public.violations;

CREATE TABLE IF NOT EXISTS public.violations
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    batch_id integer NOT NULL,
    temperature_reading_id integer NOT NULL,
    violation_type text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT violations_pkey PRIMARY KEY (id),
    CONSTRAINT violations_batch_id_temperature_reading_id_key UNIQUE (batch_id, temperature_reading_id),
    CONSTRAINT violations_batch_id_fkey FOREIGN KEY (batch_id)
        REFERENCES public.batches (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE RESTRICT,
    CONSTRAINT violations_temperature_reading_id_fkey FOREIGN KEY (temperature_reading_id)
        REFERENCES public.temperature_readings (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE RESTRICT,
    CONSTRAINT violations_violation_type_check CHECK (violation_type = ANY (ARRAY['too_low'::text, 'too_high'::text]))
);
