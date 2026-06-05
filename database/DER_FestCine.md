# Modelo Entidad-Relación — FestCine

## Diagrama de Tablas y Relaciones

```
┌──────────────┐       ┌──────────────────┐
│   Generos    │       │   Peliculas      │
│──────────────│       │──────────────────│
│ PK IdGenero  │◄──┐   │ PK IdPelicula    │──┐
│    Nombre    │   │   │    Titulo        │  │
└──────────────┘   │   │    AnioProd      │  │
                   │   │    Duracion      │  │
┌──────────────────┘   │    PaisOrigen    │  │
│  PeliculaGenero      │    Sinopsis      │  │
│─────────────────┐    │    Clasificacion │  │
│ PK,FK IdPelicula│    │    Formato       │  │
│ PK,FK IdGenero  │    │    Estado        │  │
└─────────────────┘    └────────┬─────────┘  │
                               │            │
                      ┌────────▼─────────┐  │
                      │  RolesPelicula   │  │
                      │──────────────────│  │
                      │ PK,FK IdPersonal │  │
                      │ PK,FK IdPelicula │──┘
                      │ PK    Rol        │
                      └──────────────────┘
                               ▲
                      ┌────────┴─────────┐
                      │    Personal      │
                      │──────────────────│
                      │ PK IdPersonal    │
                      │    Nombre        │
                      │    Biografia     │
                      │    Email         │
                      └──────────────────┘

┌──────────────────┐
│   Ediciones      │
│──────────────────│
│ PK IdEdicion     │───◇──┐
│    Anio          │      │
│    NombreEdicion │      │
│    FechaInicio   │      │
│    FechaFin      │      │
└──────────────────┘      │
                          │
┌──────────────────┐      │     ┌──────────────────┐
│   Sedes          │      │     │   Proyecciones   │
│──────────────────│      │     │──────────────────│
│ PK IdSede        │──┐   ├─────│ PK IdProyeccion  │
│    NombreSede    │  │   │     │ FK IdPelicula    │
│    Direccion     │  │   │     │ FK IdSala        │
└──────────────────┘  │   │     │ FK IdEdicion     │
                      │   │     │    FechaHora     │
┌──────────────────┐  │   │     │    TieneQA       │
│   Salas          │  │   │     │    AforoDisponible│
│──────────────────│  │   │     └──────────────────┘
│ PK IdSala        │◄─┘   │
│ FK IdSede        │      │
│    NombreSala    │      │     ┌──────────────────┐
│    Capacidad     │      │     │ EventosParalelos │
└──────────────────┘      ├─────│──────────────────│
                          │     │ PK IdEvento      │
┌──────────────────┐      │     │ FK IdEdicion     │
│   ExpositorEvento│      │     │    NombreEvento  │
│──────────────────│      │     │    TipoEvento    │
│ PK,FK IdEvento   │◄─────┤     │    FechaHora     │
│ PK,FK IdPersonal │◄──┐  │     │    Aforo         │
└──────────────────┘   │  │     └──────────────────┘
                       │  │
                       │  │     ┌──────────────────┐
                       │  │     │  CompetenciaPeli. │
                       │  │     │──────────────────│
                       │  │     │ PK,FK IdPelicula  │──◇──┐
                       │  │     │ PK,FK IdCategoria │     │
                       │  │     └──────────────────┘     │
                       │  │                              │
                       │  │     ┌──────────────────┐     │
                       │  │     │   Categorias     │     │
                       │  │     │──────────────────│     │
                       │  │     │ PK IdCategoria   │◄────┘
                       │  │     │    NombreCat     │
                       │  │     └──────────────────┘
                       │  │              ▲
                       │  │     ┌────────┴──────────┐
                       │  │     │  JuradoCategoria   │
                       │  │     │───────────────────│
                       │  │     │ PK,FK IdMiembro    │
                       │  │     │ PK,FK IdCategoria  │
                       │  │     └───────────────────┘
                       │  │               ▲
                       │  │     ┌─────────┴──────────┐
                       │  │     │  MiembrosJurado    │
                       │  │     │───────────────────│
                       │  │     │ PK IdMiembro       │
                       │  │     │    Nombre          │
                       │  │     └───────────────────┘
                       │  │
                       │  │     ┌──────────────────┐
                       │  │     │  Evaluaciones    │
                       │  │     │──────────────────│
                       │  │     │ PK IdEvaluacion  │
                       │  │     │ FK IdMiembro     │
                       │  │     │ FK IdPelicula    │
                       │  │     │ FK IdCategoria   │
                       │  │     │    Puntuacion    │
                       │  │     │    Comentario    │
                       │  │     └──────────────────┘
                       │  │
                       │  │     ┌──────────────────┐
                       │  │     │   Premios        │
                       │  │     │──────────────────│
                       │  ├─────│ FK IdEdicion     │
                       │  │     │ FK IdCategoria   │
                       │  │     │ FK IdPelicula    │
                       │  │     └──────────────────┘
                       │  │
                       │  │     ┌──────────────────┐
                       │  │     │   Abonos         │
                       │  ├─────│──────────────────│
                       │  │     │ PK IdAbono       │
                       │  │     │ FK IdAsistente   │
                       │  │     │ FK IdTipoAbono   │
                       │  │     │ FK IdEdicion     │
                       │  │     │    CodigoAcceso  │
                       │  │     │    Pagado        │
                       │  │     └──────────────────┘
                       │  │
          ┌────────────┘  │     ┌──────────────────┐
          │               │     │  TiposAbono      │
          │               │     │──────────────────│
          │               │     │ PK IdTipoAbono   │
          │               │     │    NombreAbono   │
          │               │     │    Precio        │
          │               │     └──────────────────┘
          │               │
┌─────────▼──────────┐    │     ┌──────────────────┐
│   Entradas         │    │     │  PatrocinioEdicion│
│────────────────────│    │     │──────────────────│
│ PK IdEntrada       │    ├─────│ PK IdPatrocinio  │
│ FK IdAsistente     │    │     │ FK IdPatrocinador│
│ FK IdProyeccion?   │    │     │ FK IdEdicion     │
│ FK IdEvento?       │    │     │    TipoAporte    │
│ FK IdTarifa        │    │     └──────────────────┘
└────────────────────┘    │               ▲
                          │     ┌─────────┴──────────┐
┌──────────────────┐      │     │  Patrocinadores    │
│   Asistentes     │      │     │───────────────────│
│──────────────────│      │     │ PK IdPatrocinador  │
│ PK IdAsistente   │◄─────┘     │    NombreEmpresa  │
│    Nombre        │            └───────────────────┘
│    Email (UQ)    │
│    TipoAsistente │            ┌──────────────────┐
└──────────────────┘            │   Hoteles        │
                                │──────────────────│
┌──────────────────┐            │ PK IdHotel       │
│   Tarifas        │            │    NombreHotel   │
│──────────────────│            └──────────────────┘
│ PK IdTarifa      │                      ▲
│    NombreTarifa  │            ┌─────────┴──────────┐
│    Precio        │            │  Alojamientos      │
└──────────────────┘            │───────────────────│
                                │ PK IdAlojamiento  │
┌──────────────────┐            │ FK IdPersonal     │
│   Traslados      │            │ FK IdHotel        │
│──────────────────│            │ FK IdEdicion      │
│ PK IdTraslado    │            │    NroHabitacion  │
│ FK IdPersonal    │            │    CheckIn        │
│ FK IdEdicion     │            │    CheckOut       │
│    TipoTraslado  │            └──────────────────┘
│    Origen/Destino│
└──────────────────┘
```

## Normalización (3FN)

**1FN**: Todos los atributos son atómicos. No hay grupos repetitivos (las relaciones N:M se gestionan con tablas intermedias: `PeliculaGenero`, `RolesPelicula`, `ExpositorEvento`, `JuradoCategoria`, `CompetenciaPelicula`).

**2FN**: Todas las tablas tienen clave primaria simple o compuesta. Los atributos no clave dependen completamente de la PK. Ejemplo: en `RolesPelicula` (PK: IdPersonal, IdPelicula, Rol), no hay atributos no clave.

**3FN**: No hay dependencias transitivas. Ejemplo: en `Proyecciones`, `AforoDisponible` depende de `IdProyeccion`, no de `IdSala` o `IdPelicula`.

**Desnormalización**: No se aplicó desnormalización. El esquema está completamente en 3FN.

## Asunciones Documentadas

1. Un asistente VIP o Jurado tiene tarifa $0 pero igual se registra la entrada para control de aforo.
2. La "pasarela de pago" en la venta de abonos se simula con el parámetro `p_PagoExitoso`. Si es FALSE se lanza EXCEPTION y PostgreSQL aplica ROLLBACK automático.
3. Los abonos no especifican proyecciones concretas; dan acceso general según su tipo.
4. Las habitaciones de hotel se modelan como texto simple (no se gestiona inventario de habitaciones).
5. La política de reembolsos queda fuera del alcance del sistema.
6. El trigger `TR_ControlAgenda` valida cruce de horarios considerando duración de película + 30 min de limpieza.

## Convenciones de Nomenclatura

- Tablas: PascalCase en español (ej. `PeliculaGenero`, `MiembrosJurado`)
- Columnas: CamelCase con prefijo del tipo (ej. `IdPelicula`, `NombreGenero`)
- PK: `PK_` + prefijo (ej. `PK_Pel`)
- FK: `FK_` + tabla1 + _ + tabla2 (ej. `FK_PelGen_Pel`)
- Vistas: prefijo `vw_`
- Functions: prefijo `fn_`
- Triggers: prefijo `TR_`
- Stored Procedures: prefijo `sp_`
