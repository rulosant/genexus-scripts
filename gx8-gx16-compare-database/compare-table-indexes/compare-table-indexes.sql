-- Replace DB1 and DB2 with your database names
-- Replace Server2 with your server name
-- Replace Tablename1 and Tablename2 with your table names

-- Declare table variables to store index information
DECLARE @DB1Indexes TABLE (
    TableName NVARCHAR(128),
    IndexName NVARCHAR(128)
)

DECLARE @DB2Indexes TABLE (
    TableName NVARCHAR(128),
    IndexName NVARCHAR(128)
)

-- Define the tables to compare
DECLARE @TableList TABLE (TableName NVARCHAR(128))
INSERT INTO @TableList (TableName)
VALUES ('TABLENAME1'),('TABLENAME2')

-- Get index details from DB1
INSERT INTO @DB1Indexes
SELECT
    t.TableName,
    i.name AS IndexName
FROM @TableList t
JOIN DB1.sys.tables tbl ON t.TableName = tbl.name
JOIN DB1.sys.indexes i ON tbl.object_id = i.object_id
WHERE i.type > 0 -- Ignore heap indexes

-- Get index details from DB2
INSERT INTO @DB2Indexes
SELECT
    t.TableName,
    i.name AS IndexName
FROM @TableList t
JOIN [SERVER2].[DB2].sys.tables tbl ON t.TableName = tbl.name
JOIN [SERVER2].[DB2].sys.indexes i ON tbl.object_id = i.object_id
WHERE i.type > 0 -- Ignore heap indexes

-- Compare indexes and generate output
SELECT
    COALESCE(d1.TableName, d2.TableName) AS TableName,
    COALESCE(d1.IndexName, d2.IndexName) AS IndexName,
    CASE WHEN d1.IndexName IS NOT NULL THEN 1 ELSE 0 END AS ExistsInDB1,
    CASE WHEN d2.IndexName IS NOT NULL THEN 1 ELSE 0 END AS ExistsInDB2,
    CASE WHEN (d1.IndexName IS NOT NULL AND d2.IndexName IS NULL) OR (d1.IndexName IS NULL AND d2.IndexName IS NOT NULL) THEN 1 ELSE 0 END AS IndexesChanged
FROM @DB1Indexes d1
FULL OUTER JOIN @DB2Indexes d2 ON d1.TableName = d2.TableName AND d1.IndexName = d2.IndexName
