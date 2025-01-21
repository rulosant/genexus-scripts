DECLARE @ProcedureName NVARCHAR(128) = 'STORE_PROCEDURE_NAME';

DECLARE @list TABLE (value SYSNAME COLLATE Latin1_General_CI_AS_KS_WS);
INSERT INTO @list (value) VALUES ('USER_TABLE'), ('SQL_STORED_PROCEDURE')  -- Tablas y SPs
--INSERT INTO @list (value) VALUES ('SQL_STORED_PROCEDURE')                  -- Solo SPs

SELECT 
    OBJECT_NAME(referencing_id) AS ParentObjectName, '-->' Link,
    referenced_entity_name,
    o.type_desc
FROM sys.sql_expression_dependencies d
INNER JOIN sys.objects o ON o.name = d.referenced_entity_name
WHERE OBJECT_NAME(referencing_id) = @ProcedureName                    -- Filtro por tipo de objeto
and type_desc IN (SELECT value FROM @list)
union 
-- Segundo nivel
SELECT 
    OBJECT_NAME(d.referencing_id) AS ParentObjectName, '-->' Link,
    d.referenced_entity_name,
    o.type_desc
FROM sys.sql_expression_dependencies d
INNER JOIN sys.objects o ON o.name = d.referenced_entity_name
WHERE OBJECT_NAME(d.referencing_id) IN (
    SELECT d.referenced_entity_name
    FROM sys.sql_expression_dependencies d
    INNER JOIN sys.objects o ON o.name = d.referenced_entity_name
    WHERE OBJECT_NAME(d.referencing_id) = @ProcedureName 
	
) 
and type_desc IN (SELECT value FROM @list);					        -- Filtro por tipo de objeto