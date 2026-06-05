# Consultas DQL — Fase 3: Reportes

## 1. Ranking de Películas (más vistas + % ocupación)

```sql
SELECT p.Titulo,
       COUNT(e.IdEntrada)                                                  AS TotalAsistentes,
       SUM(s.Capacidad)                                                    AS CapacidadTotal,
       ROUND(COUNT(e.IdEntrada) * 100.0 / NULLIF(SUM(s.Capacidad), 0), 2) AS PorcentajeOcupacion
FROM Peliculas p
    INNER JOIN Proyecciones pr ON pr.IdPelicula = p.IdPelicula
    INNER JOIN Salas s         ON s.IdSala      = pr.IdSala
    LEFT  JOIN Entradas e      ON e.IdProyeccion = pr.IdProyeccion
GROUP BY p.IdPelicula, p.Titulo
ORDER BY TotalAsistentes DESC, PorcentajeOcupacion DESC;
```

**Explicación**: Cuenta las entradas vendidas por película (sumando todas sus proyecciones) y las divide entre la capacidad total de las salas donde se proyectó. `NULLIF` evita división por cero. El `LEFT JOIN` en Entradas asegura que películas sin ventas también aparezcan.

**Llamada desde la app**: `SELECT * FROM fn_ReporteRanking()`

---

## 2. Acta de Premiación

```sql
SELECT c.NombreCategoria,
       p.Titulo                      AS PeliculaGanadora,
       ROUND(AVG(ev.Puntuacion), 2)  AS PromedioJurado,
       COUNT(ev.IdEvaluacion)        AS VotosRecibidos,
       e.Anio
FROM Premios pr
    INNER JOIN Categorias c    ON c.IdCategoria = pr.IdCategoria
    INNER JOIN Peliculas p     ON p.IdPelicula  = pr.IdPelicula
    INNER JOIN Ediciones e     ON e.IdEdicion   = pr.IdEdicion
    INNER JOIN Evaluaciones ev ON ev.IdPelicula  = pr.IdPelicula
                              AND ev.IdCategoria = pr.IdCategoria
GROUP BY c.NombreCategoria, p.Titulo, e.Anio
ORDER BY e.Anio, c.NombreCategoria;
```

**Explicación**: Obtiene las películas ganadoras desde la tabla `Premios` y calcula el promedio de puntuación que recibieron de los miembros del jurado en sus evaluaciones. Agrupa por categoría y año de edición.

**Llamada desde la app**: `SELECT * FROM fn_ReportePremiacion()`

---

## 3. Informe Financiero

### Desglosado por tarifa y tipo de abono

```sql
SELECT 'Entrada Individual' AS TipoVenta,
       t.NombreTarifa       AS Detalle,
       COUNT(e.IdEntrada)   AS CantidadVentas,
       SUM(t.Precio)        AS TotalRecaudado
FROM Entradas e
    INNER JOIN Tarifas t ON t.IdTarifa = e.IdTarifa
GROUP BY t.NombreTarifa
UNION ALL
SELECT 'Abono',
       ta.NombreAbono,
       COUNT(a.IdAbono),
       SUM(ta.Precio)
FROM Abonos a
    INNER JOIN TiposAbono ta ON ta.IdTipoAbono = a.IdTipoAbono
WHERE a.Pagado = TRUE
GROUP BY ta.NombreAbono
ORDER BY TipoVenta, TotalRecaudado DESC;
```

### Resumen total

```sql
SELECT 'Entradas Individuales' AS Tipo, SUM(t.Precio) AS Total
FROM Entradas e JOIN Tarifas t ON t.IdTarifa = e.IdTarifa
UNION ALL
SELECT 'Abonos', SUM(ta.Precio)
FROM Abonos a JOIN TiposAbono ta ON ta.IdTipoAbono = a.IdTipoAbono
WHERE a.Pagado = TRUE;
```

**Explicación**: La primera consulta desglosa ingresos por tarifa individual y tipo de abono. La segunda da el total por categoría (entradas vs abonos). Solo se cuentan abonos pagados.

**Llamada desde la app**: `SELECT * FROM fn_ReporteFinanciero()`

---

## 4. Reporte de Ocupación de Salas

```sql
SELECT s.NombreSala,
       se.NombreSede,
       s.Capacidad,
       COUNT(e.IdEntrada) AS EntradasVendidas,
       ROUND(COUNT(e.IdEntrada) * 100.0 / NULLIF(s.Capacidad, 0), 2) AS PorcentajeOcupacion
FROM Salas s
    JOIN Sedes se ON se.IdSede = s.IdSede
    LEFT JOIN Proyecciones pr ON pr.IdSala = s.IdSala
    LEFT JOIN Entradas e ON e.IdProyeccion = pr.IdProyeccion
GROUP BY s.IdSala, se.NombreSede
ORDER BY PorcentajeOcupacion DESC;
```

**Endpoint**: `GET /api/reportes/ocupacion-salas`

---

## 5. Reporte de Ventas por Edición

```sql
-- Entradas
SELECT COUNT(*) AS Cantidad, SUM(t.Precio) AS Total
FROM Entradas e
    JOIN Tarifas t ON t.IdTarifa = e.IdTarifa
    JOIN Proyecciones pr ON pr.IdProyeccion = e.IdProyeccion
WHERE pr.IdEdicion = $1;

-- Abonos
SELECT COUNT(*) AS Cantidad, SUM(ta.Precio) AS Total
FROM Abonos a
    JOIN TiposAbono ta ON ta.IdTipoAbono = a.IdTipoAbono
WHERE a.Pagado = TRUE
  AND a.IdEdicion = $1;
```

**Endpoint**: `GET /api/reportes/ventas-edicion/:id`
