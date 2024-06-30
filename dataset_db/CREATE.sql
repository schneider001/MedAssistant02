PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS disease_symptom;
DROP TABLE IF EXISTS disease_precaution;
DROP TABLE IF EXISTS symptoms;
DROP TABLE IF EXISTS precautions;
DROP TABLE IF EXISTS diseases;

CREATE TABLE diseases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en_name TEXT UNIQUE NOT NULL,
    ru_name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE precautions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT UNIQUE NOT NULL
);

CREATE TABLE disease_precaution(
    disease_id INTEGER NOT NULL,
    precaution_id INTEGER NOT NULL,
    PRIMARY KEY (disease_id, precaution_id),
    FOREIGN KEY (disease_id) REFERENCES diseases (id) ON DELETE CASCADE,
    FOREIGN KEY (precaution_id) REFERENCES precautions (id) ON DELETE CASCADE
);

CREATE TABLE symptoms(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en_name TEXT UNIQUE NOT NULL,
    ru_name TEXT UNIQUE NOT NULL,
    weight INTEGER
);

CREATE TABLE disease_symptom(
    record_number INTEGER NOT NULL,
    disease_id INTEGER NOT NULL,
    symptom_id INTEGER NOT NULL,
    PRIMARY KEY (record_number, disease_id, symptom_id),
    FOREIGN KEY (symptom_id) REFERENCES symptoms (id) ON DELETE CASCADE,
    FOREIGN KEY (disease_id) REFERENCES diseases (id) ON DELETE CASCADE
);
