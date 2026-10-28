# Documentación de la Fuente de Datos: Online Retail II

## 1. Descripción y Elección del Dataset

El conjunto de datos contiene **1.067.371 transacciones reales** de ventas ocurridas entre el 01/12/2009 y el 09/12/2011 para una tienda minorista online registrada en el Reino Unido. La empresa comercializa principalmente regalos originales y artículos para ocasiones especiales, contando con una importante base de clientes mayoristas.

### ¿Por qué elegimos este dataset?

Es una fuente ideal para abordar el problema de **clasificación ABC de inventario** y la **detección de productos clave en riesgo de rotura de stock**:

* **Representatividad comercial:** Refleja la rotación real de un e-commerce multicanal con diversidad de productos (5.305 productos distintos) y presencia global (43 países).
* **Granularidad temporal:** Cubre 2 años completos (01/12/2009 a 09/12/2011), permitiendo analizar patrones de compra repetidos, estacionalidad e impacto acumulado en el tiempo.
* **Comportamiento dinámico:** Incluye devoluciones, cancelaciones y variaciones bruscas de volumen por cliente/producto, clave para probar algoritmos de priorización y alertas de inventario.

## 2. Fuente, Autor, Cita y Licencia

* **Nombre del dataset:** Online Retail II
* **Repositorio:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
* **Autor / Donante:** Daqing Chen (School of Engineering, London South Bank University)
* **Licencia:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/legalcode)

> **Cita Oficial:**
>
> Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. DOI: [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D)

*Nota de corrección:* En la documentación técnica oficial de UCI, el nombre de la columna listado como `Price` en algunas exportaciones de usuario corresponde formalmente a `UnitPrice`, y la columna de factura se denomina `Invoice` o `InvoiceNo`.

## 3. Estructura de Columnas

El archivo original se distribuye en formato Excel (`online_retail_II.xlsx`) compuesto por dos hojas de cálculo: `Year 2009-2010` y `Year 2010-2011`.

| Nombre de Columna | Tipo de Dato | Descripción | Ejemplo |
| --- | --- | --- | --- |
| `Invoice` / `InvoiceNo` | Texto (Nominal) | Código único de 6 dígitos por transacción. Si empieza con 'C', es una cancelación. | `489434` / `C489449` |
| `StockCode` | Texto (Nominal) | Código identificador único del producto o artículo. | `85048` |
| `Description` | Texto (Nominal) | Nombre o descripción del artículo. | `15CM CHRISTMAS TREE TOP STAR` |
| `Quantity` | Entero (Numérico) | Cantidades de cada producto compradas por transacción. Valores negativos indican devoluciones. | `12` |
| `InvoiceDate` | Fecha / Hora | Fecha y hora exactas en que se generó la transacción. | `2009-12-01 07:45:00` |
| `Price` / `UnitPrice` | Decimal (Numérico) | Precio por unidad del producto expresado en libras esterlinas (£). | `6.95` |
| `Customer ID` | Texto / Entero | Identificador único de 5 dígitos asignado a cada cliente registrado. | `13085` |
| `Country` | Texto (Nominal) | Nombre del país de residencia del cliente. | `United Kingdom` |

## 4. Calidad de los Datos

El análisis del dataset reveló un total de **1.067.371 filas** (rango temporal de `2009-12-01 07:45:00` a `2011-12-09 12:50:00`), abarcando **5.305 productos distintos** y **43 países**.

### Nulos y vacíos por columna
* `customer_id`: **243.007 nulos**.
  * *Tratamiento:* Conservar en la tabla base para métricas globales de venta y volumen de inventario; excluir únicamente en análisis orientados a comportamiento individual de clientes (segmentación o RFM).
* `description`: **4.382 nulos**.
  * *Tratamiento:* Imputar como `"Desconocido"` o mediante correspondencia directa con `stock_code` cuando sea posible.
* `invoice`, `stock_code`, `country`, `quantity`, `invoice_date`, `price`, `es_cancelacion`, `importe`: **0 nulos**.

### Inconsistencias de negocio y anomalías
* **Duplicados exactos:** **32.907 grupos de filas duplicadas exactas**.
  * *Tratamiento:* Eliminar las filas duplicadas para evitar sobreestimación en las métricas de ingresos e inventario.
* **Precios <= 0:** **6.207 filas con `price` <= 0**.
  * *Tratamiento:* Filtrar y descartar estas filas para el cálculo de ingresos y la clasificación ABC basada en valor monetario, ya que corresponden a ajustes contables o muestras.
* **Cantidades negativas:** **22.950 filas con `quantity` negativa**.
  * *Tratamiento:* Separar del flujo normal de ventas brutas y catalogar como devoluciones/ajustes para no distorsionar el volumen real demandado.
* **Cancelaciones:** **19.494 registros marcados como cancelaciones** (`es_cancelacion` = 1).
  * *Tratamiento:* Excluir del cálculo del análisis ABC de ventas netas o asociar a sus órdenes correspondientes según la regla de negocio del proyecto.

## 5. Carga en Base de Datos

Cargado en Supabase (Postgres, plan gratuito, región eu-west-1) mediante `backend/cargar_datos.py`:

* Tabla `ventas` (`invoice`, `stock_code`, `description`, `quantity`, `invoice_date`, `price`, `customer_id`, `country`, `es_cancelacion`, `importe`), con índices en `stock_code` e `invoice_date`.
* Carga con `COPY` (psycopg2 `copy_expert`) en vez de `to_sql`, por volumen (~1 millón de filas).
* No se borra ni deduplica nada en la carga: las 1.067.371 filas del Excel quedan íntegras en la tabla base (verificado: mismo conteo en ambos lados). Los tratamientos de la sección 4 (excluir cancelaciones, `price<=0`, deduplicar) se aplican en las consultas de análisis (ver `backend/kpi_referencia.py`), no en la tabla fuente, para no perder trazabilidad de los datos originales.
* Conexión vía "Session pooler" (puerto 5432) — la conexión directa falla en redes con NAT/firewall restrictivo.

## 6. Limitaciones del Dataset

1. **Ausencia de stock en tiempo real:** Registra únicamente transacciones de venta completadas y canceladas. No incluye niveles de inventario en almacén, existencias mínimas ni tiempos de reabastecimiento (*lead time*) del proveedor.
2. **Sesgo por estacionalidad navideña:** La tienda vende principalmente artículos de regalo, lo que genera picos atípicos de demanda en los meses de noviembre y diciembre que pueden distorsionar la velocidad de venta regular.
3. **Datos de 2009-2011:** Los hábitos de consumo online, precios e inflación corresponden a un periodo histórico de hace más de una década, por lo que las conclusiones deben adaptarse antes de usarse en entornos de e-commerce actuales.
