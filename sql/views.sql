CREATE OR REPLACE VIEW avg_temp_por_local AS
SELECT location, ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
       COUNT(*) AS total_leituras
FROM temperature_readings
GROUP BY location;

CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT EXTRACT(HOUR FROM noted_at)::integer AS hora,
       COUNT(*) AS contagem
FROM temperature_readings
GROUP BY EXTRACT(HOUR FROM noted_at)
ORDER BY hora;

CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT DATE(noted_at) AS data,
       ROUND(MAX(temperature)::numeric, 2) AS temp_max,
       ROUND(MIN(temperature)::numeric, 2) AS temp_min,
       ROUND(AVG(temperature)::numeric, 2) AS temp_media
FROM temperature_readings
GROUP BY DATE(noted_at)
ORDER BY data;
