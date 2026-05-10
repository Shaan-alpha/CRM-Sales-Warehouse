SELECT
    account,
    sector,
    revenue,
    employees
FROM {{ ref('stg_accounts') }}
WHERE revenue IS NOT NULL