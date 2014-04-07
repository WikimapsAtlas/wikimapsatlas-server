SET CLIENT_ENCODING TO UTF8;
SET STANDARD_CONFORMING_STRINGS TO ON;
DROP TABLE IF EXISTS "adm0";
BEGIN;
CREATE TABLE "adm0" (
    name varchar(80) NOT NULL,	-- country name
    start_date date,		-- date of formation
    end_date date,
    next_name varchar(80),       
    previous_name varchar(80),
    wikidata_item varchar(16)	-- wikidata item code http://wikidata.org
);

SELECT * FROM naturalearth.adm0_polygon_l.admin;

SELECT naturalearth.adm0_polygon_l (admin) from adm0_polygon_l
