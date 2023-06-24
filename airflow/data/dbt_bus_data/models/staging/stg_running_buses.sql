{{ config(materialized='view') }}

WITH catalog_data AS(
    SELECT * FROM {{ref('2-scrapped_data_v3')}}
),
regions AS(
    SELECT * FROM {{ref('sptrans_regions')}}
)

SELECT 
    t1.line_name, 
    CAST(t1.line_number as INT64) as line_number, 
    cd.company_name, 
    CAST(cd.region_id as INT64) as region_id,
    r.region_name,
    r.region_color, 
    CAST(t1.qtd_running_buses as INT64) as qtd_running_buses,
    t1.timestamp
FROM 
    {{ source('staging', 'external_table_running_buses') }} t1
INNER JOIN 
    catalog_data cd ON cd.line_sign_name = t1.line_name AND cd.line_number = t1.line_number
INNER JOIN 
    regions r ON r.region_id = cd.region_id
WHERE 
    timestamp = (
        SELECT 
            MAX(timestamp)
        FROM {{ source('staging', 'external_table_running_buses') }}
    )