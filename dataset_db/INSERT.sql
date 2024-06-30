DROP TABLE IF EXISTS temp.dataset_temp;
DROP TABLE IF EXISTS temp.diseases_temp;
DROP TABLE IF EXISTS temp.precautions_temp;
DROP TABLE IF EXISTS temp.symptoms_temp;

CREATE TEMP TABLE diseases_temp(
    Disease TEXT,
    Description TEXT,
    ru_name TEXT
);

CREATE TEMP TABLE symptoms_temp(
    Symptom TEXT,
    weight INTEGER,
    ru_name TEXT
);

.import --csv --schema temp ./../datasets/dataset.csv dataset_temp
.import --csv --schema temp ./../datasets/symptom_Description_ru.csv diseases_temp
.import --csv --schema temp ./../datasets/symptom_precaution.csv precautions_temp
.import --csv --schema temp "./../datasets/Symptom-severity_ru.csv" symptoms_temp


INSERT INTO symptoms (en_name, ru_name, weight)
SELECT
    Symptom,
    ru_name,
    weight
FROM symptoms_temp;

INSERT INTO diseases (en_name, description, ru_name)
SELECT 
    Disease,
    Description,
    ru_name
FROM diseases_temp;

INSERT INTO precautions (description)
SELECT DISTINCT
    precaution
FROM (
    SELECT Precaution_1 AS precaution FROM precautions_temp UNION
    SELECT Precaution_2 AS precaution FROM precautions_temp UNION
    SELECT Precaution_3 AS precaution FROM precautions_temp UNION
    SELECT Precaution_4 AS precaution FROM precautions_temp
) WHERE precaution IS NOT NULL AND precaution != '';

INSERT INTO disease_precaution (disease_id, precaution_id)
SELECT
    d.id,
    p.id
FROM (
    SELECT Disease, Precaution_1 AS precaution FROM precautions_temp UNION ALL
    SELECT Disease, Precaution_2 AS precaution FROM precautions_temp UNION ALL
    SELECT Disease, Precaution_3 AS precaution FROM precautions_temp UNION ALL
    SELECT Disease, Precaution_4 AS precaution FROM precautions_temp
) JOIN diseases AS d ON Disease = d.en_name
JOIN precautions AS p ON precaution = p.description
WHERE precaution IS NOT NULL AND precaution != '';

INSERT INTO disease_symptom (record_number, disease_id, symptom_id)
SELECT 
    rowid AS record_number,
    d.id,
    s.id
FROM (
    SELECT rowid, Disease, Symptom_1 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_2 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_3 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_4 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_5 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_6 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_7 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_8 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_9 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_10 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_11 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_12 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_13 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_14 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_15 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_16 AS symptom_en FROM dataset_temp UNION ALL
    SELECT rowid, Disease, Symptom_17 AS symptom_en FROM dataset_temp
) JOIN diseases AS d ON Disease = d.en_name
JOIN symptoms AS s ON symptom_en = s.en_name
WHERE symptom_en IS NOT NULL AND symptom_en != '';