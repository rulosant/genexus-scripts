import pyodbc
import pandas as pd
import warnings

# Suprimir warnings de pandas sobre SQLAlchemy
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy connectable')

# --- CONFIGURACIÓN INICIAL ---
# Lista de columnas a ignorar durante la comparación
# Estas columnas no se verificarán ni se incluirán en la comparación
COLUMNAS_A_IGNORAR = [
    # Ejemplos de columnas que podrías querer ignorar:
    # 'FAlt',    # Fecha de alta
    # 'UAlt',    # Usuario de alta
]

# --- CONFIGURACIÓN DE CLAVE PRIMARIA ---
# Especifica las columnas que forman la clave primaria para la comparación
# Si está vacío, el script intentará detectar automáticamente la clave
CLAVE_PRIMARIA = [
    # 'Empr',    # Empresa
    # 'Doc',    # Paquete
]

# Si quieres que detecte automáticamente, deja CLAVE_PRIMARIA vacío
# El script buscará columnas que contengan palabras clave como: ID, Key, Cod, Emp, etc.

#--- Configuración de conexiones ---
conn1 = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SERVER1;"
    "DATABASE=DB1;"
    "Trusted_Connection=yes;"
)


conn2 = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SERVER2;"
    "DATABASE=DB2;"
    "Trusted_Connection=yes;"
)

# --- Nombre de la tabla ---
tabla = "TableNane"

# --- Cargar datos de cada base en DataFrames ---
query = f"SELECT * FROM {tabla}"

df1 = pd.read_sql(query, conn1)
df2 = pd.read_sql(query, conn2)

# --- Filtrar columnas a ignorar ---
if COLUMNAS_A_IGNORAR:
    print(f"🔧 Filtrando {len(COLUMNAS_A_IGNORAR)} columnas ignoradas: {COLUMNAS_A_IGNORAR}")
    
    # Filtrar columnas de df1
    columnas_originales_df1 = list(df1.columns)
    df1 = df1.drop(columns=[col for col in COLUMNAS_A_IGNORAR if col in df1.columns])
    columnas_filtradas_df1 = [col for col in COLUMNAS_A_IGNORAR if col in columnas_originales_df1]
    
    # Filtrar columnas de df2
    columnas_originales_df2 = list(df2.columns)
    df2 = df2.drop(columns=[col for col in COLUMNAS_A_IGNORAR if col in df2.columns])
    columnas_filtradas_df2 = [col for col in COLUMNAS_A_IGNORAR if col in columnas_originales_df2]
    
    print(f"   DB1: Se filtraron {len(columnas_filtradas_df1)} columnas: {columnas_filtradas_df1}")
    print(f"   DB2: Se filtraron {len(columnas_filtradas_df2)} columnas: {columnas_filtradas_df2}")
    print(f"   DB1: Columnas restantes: {len(df1.columns)}")
    print(f"   DB2: Columnas restantes: {len(df2.columns)}")
else:
    print("🔧 No hay columnas configuradas para ignorar")

# --- Comparar cantidad de registros ---
if df1.shape[0] != df2.shape[0]:
    print(f"❌ Diferencia en cantidad de filas: {df1.shape[0]} vs {df2.shape[0]}")
else:
    print("✔ Cantidad de filas idéntica")

# --- Comparar estructura ---
if list(df1.columns) != list(df2.columns):
    print("❌ Diferencia en columnas")
    print("DB1:", df1.columns)
    print("DB2:", df2.columns)
else:
    print("✔ Columnas idénticas")

# --- IDENTIFICAR CLAVE PRIMARIA ---
def detectar_clave_primaria(df1, df2):
    """Detecta automáticamente la clave primaria basándose en patrones comunes"""
    if CLAVE_PRIMARIA:
        print(f"🔑 Usando clave primaria configurada: {CLAVE_PRIMARIA}")
        return CLAVE_PRIMARIA
    
    # Buscar columnas que podrían ser clave primaria
    palabras_clave = ['ID', 'Key', 'Cod', 'Emp', 'Pqt', 'Num', 'Nro', 'Codigo', 'Codigo']
    columnas_candidatas = []
    
    for col in df1.columns:
        col_upper = col.upper()
        if any(palabra in col_upper for palabra in palabras_clave):
            columnas_candidatas.append(col)
    
    if columnas_candidatas:
        print(f"🔍 Clave primaria detectada automáticamente: {columnas_candidatas}")
        return columnas_candidatas
    else:
        # Si no se detecta, usar las primeras columnas como clave
        clave_por_defecto = list(df1.columns)[:2] if len(df1.columns) >= 2 else list(df1.columns)
        print(f"⚠️  No se pudo detectar clave primaria. Usando por defecto: {clave_por_defecto}")
        return clave_por_defecto

clave_primaria = detectar_clave_primaria(df1, df2)

# Verificar que la clave primaria existe en ambas bases
clave_existe_db1 = all(col in df1.columns for col in clave_primaria)
clave_existe_db2 = all(col in df2.columns for col in clave_primaria)

if not clave_existe_db1 or not clave_existe_db2:
    print("❌ Error: La clave primaria no existe en ambas bases de datos")
    print(f"Clave: {clave_primaria}")
    print(f"Existe en DB1: {clave_existe_db1}")
    print(f"Existe en DB2: {clave_existe_db2}")
    exit(1)

# --- COMPARACIÓN BASADA EN CLAVE PRIMARIA ---
print(f"\n🔍 Iniciando comparación basada en clave primaria: {clave_primaria}")

# Crear índices basados en la clave primaria
df1_indexed = df1.set_index(clave_primaria)
df2_indexed = df2.set_index(clave_primaria)

# Obtener claves únicas de cada base
claves_db1 = set(df1_indexed.index)
claves_db2 = set(df2_indexed.index)

print(f"📊 Registros en DB1: {len(claves_db1)}")
print(f"📊 Registros en DB2: {len(claves_db2)}")

# Identificar registros únicos
solo_en_db1 = claves_db1 - claves_db2
solo_en_db2 = claves_db2 - claves_db1
comunes = claves_db1 & claves_db2

print(f"📊 Registros solo en DB1: {len(solo_en_db1)}")
print(f"📊 Registros solo en DB2: {len(solo_en_db2)}")
print(f"📊 Registros comunes: {len(comunes)}")

# Mostrar registros únicos
if solo_en_db1:
    print(f"\n❌ REGISTROS QUE SOLO EXISTEN EN DB1 ({len(solo_en_db1)}):")
    for clave in sorted(solo_en_db1):
        print(f"   • {clave}")

if solo_en_db2:
    print(f"\n❌ REGISTROS QUE SOLO EXISTEN EN DB2 ({len(solo_en_db2)}):")
    for clave in sorted(solo_en_db2):
        print(f"   • {clave}")

# Comparar registros comunes
if comunes:
    print(f"\n🔍 COMPARANDO REGISTROS COMUNES ({len(comunes)}):")
    
    columnas_comunes = list(set(df1.columns) & set(df2.columns))
    columnas_comunes = [col for col in columnas_comunes if col not in clave_primaria]
    
    registros_diferentes = []
    
    for clave in sorted(comunes):
        registro_db1 = df1_indexed.loc[clave]
        registro_db2 = df2_indexed.loc[clave]
        
        # Comparar columnas comunes
        diferencias = []
        for col in columnas_comunes:
            if col in registro_db1.index and col in registro_db2.index:
                val1 = registro_db1[col]
                val2 = registro_db2[col]
                
                # Manejar valores NaN
                if pd.isna(val1) and pd.isna(val2):
                    continue
                elif pd.isna(val1) or pd.isna(val2) or val1 != val2:
                    diferencias.append({
                        'columna': col,
                        'valor_db1': val1,
                        'valor_db2': val2
                    })
        
        if diferencias:
            registros_diferentes.append({
                'clave': clave,
                'diferencias': diferencias,
                'registro_db1': registro_db1,
                'registro_db2': registro_db2
            })
    
    if registros_diferentes:
        print(f"❌ Se encontraron {len(registros_diferentes)} registros con diferencias:")
        
        for i, reg in enumerate(registros_diferentes, 1):
            print(f"\n🔍 REGISTRO #{i} - Clave: {reg['clave']}")
            print("-" * 60)
            print(f"📋 Columnas con diferencias: {len(reg['diferencias'])}")
            
            for diff in reg['diferencias']:
                val1_str = "NULL" if pd.isna(diff['valor_db1']) else str(diff['valor_db1'])
                val2_str = "NULL" if pd.isna(diff['valor_db2']) else str(diff['valor_db2'])
                
                print(f"   • {diff['columna']}:")
                print(f"     DB1: {val1_str}")
                print(f"     DB2: {val2_str}")
    else:
        print("✔ Todos los registros comunes son idénticos")
else:
    print("⚠️  No hay registros comunes para comparar")

# --- RESUMEN FINAL ---
total_diferencias = len(solo_en_db1) + len(solo_en_db2) + len(registros_diferentes) if 'registros_diferentes' in locals() else len(solo_en_db1) + len(solo_en_db2)

if total_diferencias > 0:
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   • Registros solo en DB1: {len(solo_en_db1)}")
    print(f"   • Registros solo en DB2: {len(solo_en_db2)}")
    if 'registros_diferentes' in locals():
        print(f"   • Registros con diferencias: {len(registros_diferentes)}")
    print(f"   • Total de inconsistencias: {total_diferencias}")
else:
    print(f"\n✔ RESUMEN FINAL: Las bases de datos son idénticas")

# --- Cerrar conexiones ---
conn1.close()
conn2.close()
