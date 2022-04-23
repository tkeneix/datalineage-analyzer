INSERT INTO members
SELECT
    X1.person_id
    ,X1.last_name
    ,X2.address
FROM persons X1
LEFT OUTER JOIN address_of_member X2
    ON X1.PersonID = X2.PersonID
;