INSERT INTO address_stat
SELECT
    address
    ,count(0)
FROM members
GROUP BY address
;

INSERT INTO city_stat
SELECT
    city
    ,count(0)
FROM persons
GROUP BY city
;
