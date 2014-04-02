CREATE TABLE admin0 (
    name varchar(80) NOT NULL,   -- country name
    start_date date,           -- date of formation
    end_date date,          
    next_name varchar(80),       
    previous_name varchar(80),
    iso_a3 varchar(3), -- 3 letter country iso code http://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
    wikidata_item varchar(16) -- wikidata item code http://wikidata.org
);

-- Add list of countries (source:naturalearthdata)
\COPY admin0 (name) FROM 'admin0_names.txt';
