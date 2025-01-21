-- Create table variables instead of temp tables
DECLARE @TableList TABLE (TableName NVARCHAR(128))

-- Insert your table names
INSERT INTO @TableList (TableName)
VALUES 
    ('Table1'),
	('Table2')-- Add your other tables here

-- Create table variables for each database's schema
DECLARE @DB1Schema TABLE (
    TableName NVARCHAR(128),
    FieldName NVARCHAR(128),
    FieldType NVARCHAR(128)
)

DECLARE @DB2Schema TABLE (
    TableName NVARCHAR(128),
    FieldName NVARCHAR(128),
    FieldType NVARCHAR(128)
)

-- Get schema from DB1
INSERT INTO @DB1Schema
SELECT 
    t.TableName,
    c.COLUMN_NAME,
    c.DATA_TYPE
FROM @TableList t
------------------------------ DATABASE 1
INNER JOIN DATABASE_1.INFORMATION_SCHEMA.TABLES ist ON t.TableName = ist.TABLE_NAME
INNER JOIN DATABASE_1.INFORMATION_SCHEMA.COLUMNS c ON ist.TABLE_NAME = c.TABLE_NAME

-- Get schema from DB2
INSERT INTO @DB2Schema
SELECT 
    t.TableName,
    c.COLUMN_NAME,
    c.DATA_TYPE
FROM @TableList t
------------------------------- DATABASE 2
------------------------------- Must be included in  sys.servers
INNER JOIN [SERVER_2].[DATABASE_2].INFORMATION_SCHEMA.TABLES ist ON t.TableName = ist.TABLE_NAME
INNER JOIN [SERVER_2].[DATABASE_2].INFORMATION_SCHEMA.COLUMNS c ON ist.TABLE_NAME = c.TABLE_NAME

-- Get the combined results with proper joining
SELECT 
    COALESCE(db1.TableName, db2.TableName) AS TableName,
    CASE WHEN db1.TableName IS NOT NULL THEN 1 ELSE 0 END AS TablePresentInDB1,
    CASE WHEN db2.TableName IS NOT NULL THEN 1 ELSE 0 END AS TablePresentInDB2,
    COALESCE(db1.FieldName, db2.FieldName) AS FieldName,
    CASE WHEN db1.FieldName IS NOT NULL THEN 1 ELSE 0 END AS FieldPresentInDB1,
    CASE WHEN db2.FieldName IS NOT NULL THEN 1 ELSE 0 END AS FieldPresentInDB2,
    ISNULL(db1.FieldType, 'N/A') AS FieldTypeInDB1,
    ISNULL(db2.FieldType, 'N/A') AS FieldTypeInDB2,
    CASE 
        WHEN (db1.TableName IS NULL OR db2.TableName IS NULL)
            OR (db1.FieldName IS NULL OR db2.FieldName IS NULL)
            OR (db1.FieldType <> db2.FieldType AND db1.FieldType IS NOT NULL AND db2.FieldType IS NOT NULL)
        THEN 1 
        ELSE 0 
    END AS has_changed
FROM @DB1Schema db1
FULL OUTER JOIN @DB2Schema db2 
    ON db1.TableName = db2.TableName 
    AND db1.FieldName = db2.FieldName

-- Este WHERE permite filtrar solo las filas que cambiaron
--/*
WHERE 
    CASE 
        WHEN (db1.TableName IS NULL OR db2.TableName IS NULL)
            OR (db1.FieldName IS NULL OR db2.FieldName IS NULL)
            OR (db1.FieldType <> db2.FieldType AND db1.FieldType IS NOT NULL AND db2.FieldType IS NOT NULL)
        THEN 1 
        ELSE 0 
    END = 1
----------------------- */

ORDER BY 
    COALESCE(db1.TableName, db2.TableName),
    COALESCE(db1.FieldName, db2.FieldName)