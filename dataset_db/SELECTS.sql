.mode box
SELECT 'Symptoms cuont', COUNT() FROM symptoms;
SELECT 'Used symptoms count', COUNT(DISTINCT symptom_id) FROM disease_symptom;
SELECT 'Diseases cuont', COUNT() FROM diseases;
SELECT 'Used diseases count', COUNT(DISTINCT disease_id) FROM disease_symptom;

SELECT 'Precautions for Allergy', d.en_name, p.description FROM precautions AS p
JOIN disease_precaution AS dp ON dp.precaution_id = p.id
JOIN diseases AS d ON dp.disease_id = d.id
WHERE d.en_name = 'Allergy';
.mode column