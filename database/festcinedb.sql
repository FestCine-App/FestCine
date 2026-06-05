/* ============================================================
   FESTCINE - Sistema de Gestion de Festival de Cine
   Motor: PostgreSQL 18
   ============================================================ */

DROP DATABASE IF EXISTS FestCine;
CREATE DATABASE FestCine;

\c festcine

/* ============================================================
   A. CATALOGO CINEMATOGRAFICO Y PERSONAL
   ============================================================ */

CREATE TABLE Generos
(
    IdGenero        SERIAL,
    NombreGenero    VARCHAR(30)  NOT NULL,
    CONSTRAINT PK_Gen    PRIMARY KEY (IdGenero),
    CONSTRAINT UQ_GenNom UNIQUE      (NombreGenero)
);

CREATE TABLE Peliculas
(
    IdPelicula      SERIAL,
    Titulo          VARCHAR(150) NOT NULL,
    AnioProd        INT          NOT NULL CHECK (AnioProd > 1888),
    Duracion        INT          NOT NULL CHECK (Duracion > 0),
    PaisOrigen      VARCHAR(60)  NOT NULL,
    Sinopsis        TEXT,
    Clasificacion   VARCHAR(10)  NOT NULL
                        CHECK (Clasificacion IN ('G','PG','PG-13','R','NC-17','ATP')),
    Formato         VARCHAR(10)  NOT NULL
                        CHECK (Formato IN ('Digital','35mm','IMAX')),
    Estado          VARCHAR(15)  NOT NULL DEFAULT 'Postulada'
                        CHECK (Estado IN ('Postulada','Seleccionada','Rechazada','Premiada')),
    CONSTRAINT PK_Pel PRIMARY KEY (IdPelicula)
);

CREATE TABLE PeliculaGenero
(
    IdPelicula  INT NOT NULL,
    IdGenero    INT NOT NULL,
    CONSTRAINT PK_PelGen     PRIMARY KEY (IdPelicula, IdGenero),
    CONSTRAINT FK_PelGen_Pel FOREIGN KEY (IdPelicula) REFERENCES Peliculas,
    CONSTRAINT FK_PelGen_Gen FOREIGN KEY (IdGenero)   REFERENCES Generos
);

CREATE TABLE Personal
(
    IdPersonal  SERIAL,
    Nombre      VARCHAR(100) NOT NULL,
    Biografia   TEXT,
    Email       VARCHAR(100),
    Telefono    VARCHAR(20),
    CONSTRAINT PK_Per PRIMARY KEY (IdPersonal)
);

CREATE TABLE RolesPelicula
(
    IdPersonal  INT         NOT NULL,
    IdPelicula  INT         NOT NULL,
    Rol         VARCHAR(20) NOT NULL
                    CHECK (Rol IN ('Director','Actor','Guionista','Productor')),
    CONSTRAINT PK_RolPel     PRIMARY KEY (IdPersonal, IdPelicula, Rol),
    CONSTRAINT FK_RolPel_Per FOREIGN KEY (IdPersonal) REFERENCES Personal,
    CONSTRAINT FK_RolPel_Pel FOREIGN KEY (IdPelicula) REFERENCES Peliculas
);

/* ============================================================
   B. EDICIONES (necesaria antes de proyecciones, eventos, etc.)
   ============================================================ */

CREATE TABLE Ediciones
(
    IdEdicion   SERIAL,
    Anio        INT          NOT NULL,
    NombreEdicion VARCHAR(100),
    FechaInicio DATE         NOT NULL,
    FechaFin    DATE         NOT NULL,
    CONSTRAINT PK_Edi        PRIMARY KEY (IdEdicion),
    CONSTRAINT UQ_EdiAnio    UNIQUE      (Anio),
    CONSTRAINT CK_Edi_Fechas CHECK       (FechaFin > FechaInicio)
);

/* ============================================================
   C. SEDES, SALAS, PROYECCIONES Y EVENTOS PARALELOS
   ============================================================ */

CREATE TABLE Sedes
(
    IdSede      SERIAL,
    NombreSede  VARCHAR(100) NOT NULL,
    Direccion   VARCHAR(200),
    Ciudad      VARCHAR(60),
    CONSTRAINT PK_Sed PRIMARY KEY (IdSede)
);

CREATE TABLE Salas
(
    IdSala      SERIAL,
    NombreSala  VARCHAR(60) NOT NULL,
    Capacidad   INT         NOT NULL CHECK (Capacidad > 0),
    IdSede      INT         NOT NULL,
    CONSTRAINT PK_Sal     PRIMARY KEY (IdSala),
    CONSTRAINT FK_Sal_Sed FOREIGN KEY (IdSede) REFERENCES Sedes
);

CREATE TABLE Proyecciones
(
    IdProyeccion    SERIAL,
    IdPelicula      INT       NOT NULL,
    IdSala          INT       NOT NULL,
    IdEdicion       INT       NOT NULL,
    FechaHora       TIMESTAMP NOT NULL,
    TieneQA         BOOLEAN   DEFAULT FALSE,
    AforoDisponible INT       NOT NULL CHECK (AforoDisponible >= 0),
    CONSTRAINT PK_Proy     PRIMARY KEY (IdProyeccion),
    CONSTRAINT FK_Proy_Pel FOREIGN KEY (IdPelicula) REFERENCES Peliculas,
    CONSTRAINT FK_Proy_Sal FOREIGN KEY (IdSala)     REFERENCES Salas,
    CONSTRAINT FK_Proy_Edi FOREIGN KEY (IdEdicion)  REFERENCES Ediciones
);

CREATE TABLE EventosParalelos
(
    IdEvento         SERIAL,
    IdEdicion        INT          NOT NULL,
    NombreEvento     VARCHAR(150) NOT NULL,
    TipoEvento       VARCHAR(15)  NOT NULL
                         CHECK (TipoEvento IN ('Masterclass','Taller','Coctel')),
    FechaHora        TIMESTAMP    NOT NULL,
    Aforo            INT          NOT NULL CHECK (Aforo > 0),
    CostoInscripcion NUMERIC(10,2) DEFAULT 0 CHECK (CostoInscripcion >= 0),
    CONSTRAINT PK_Evt     PRIMARY KEY (IdEvento),
    CONSTRAINT FK_Evt_Edi FOREIGN KEY (IdEdicion) REFERENCES Ediciones
);

CREATE TABLE ExpositorEvento
(
    IdEvento    INT NOT NULL,
    IdPersonal  INT NOT NULL,
    CONSTRAINT PK_ExpEvt     PRIMARY KEY (IdEvento, IdPersonal),
    CONSTRAINT FK_ExpEvt_Evt FOREIGN KEY (IdEvento)   REFERENCES EventosParalelos,
    CONSTRAINT FK_ExpEvt_Per FOREIGN KEY (IdPersonal) REFERENCES Personal
);

/* ============================================================
   D. COMPETICION, JURADOS Y PREMIOS
   ============================================================ */

CREATE TABLE Categorias
(
    IdCategoria     SERIAL,
    NombreCategoria VARCHAR(80)  NOT NULL,
    Descripcion     VARCHAR(200),
    CONSTRAINT PK_Cat PRIMARY KEY (IdCategoria)
);

CREATE TABLE MiembrosJurado
(
    IdMiembro   SERIAL,
    Nombre      VARCHAR(100) NOT NULL,
    Profesion   VARCHAR(60),
    Pais        VARCHAR(60),
    Email       VARCHAR(100),
    CONSTRAINT PK_MJ PRIMARY KEY (IdMiembro)
);

CREATE TABLE JuradoCategoria
(
    IdMiembro   INT NOT NULL,
    IdCategoria INT NOT NULL,
    CONSTRAINT PK_JurCat     PRIMARY KEY (IdMiembro, IdCategoria),
    CONSTRAINT FK_JurCat_MJ  FOREIGN KEY (IdMiembro)   REFERENCES MiembrosJurado,
    CONSTRAINT FK_JurCat_Cat FOREIGN KEY (IdCategoria) REFERENCES Categorias
);

CREATE TABLE CompetenciaPelicula
(
    IdPelicula  INT NOT NULL,
    IdCategoria INT NOT NULL,
    IdEdicion   INT NOT NULL,
    CONSTRAINT PK_CompPel          PRIMARY KEY (IdPelicula, IdCategoria, IdEdicion),
    CONSTRAINT FK_CompPel_Pel      FOREIGN KEY (IdPelicula)  REFERENCES Peliculas,
    CONSTRAINT FK_CompPel_Cat      FOREIGN KEY (IdCategoria) REFERENCES Categorias,
    CONSTRAINT FK_CompPel_Edi      FOREIGN KEY (IdEdicion)   REFERENCES Ediciones
);

CREATE TABLE Evaluaciones
(
    IdEvaluacion    SERIAL,
    IdMiembro       INT  NOT NULL,
    IdPelicula      INT  NOT NULL,
    IdCategoria     INT  NOT NULL,
    IdEdicion       INT  NOT NULL,
    Puntuacion      INT  NOT NULL CHECK (Puntuacion BETWEEN 1 AND 10),
    Comentario      TEXT,
    CONSTRAINT PK_Eval    PRIMARY KEY (IdEvaluacion),
    CONSTRAINT UQ_Eval    UNIQUE      (IdMiembro, IdPelicula, IdCategoria, IdEdicion),
    CONSTRAINT FK_Eval_JC FOREIGN KEY (IdMiembro, IdCategoria)
                              REFERENCES JuradoCategoria (IdMiembro, IdCategoria),
    CONSTRAINT FK_Eval_CP FOREIGN KEY (IdPelicula, IdCategoria, IdEdicion)
                              REFERENCES CompetenciaPelicula (IdPelicula, IdCategoria, IdEdicion),
    CONSTRAINT FK_Eval_Edi FOREIGN KEY (IdEdicion) REFERENCES Ediciones
);

CREATE TABLE Premios
(
    IdPremio    SERIAL,
    IdCategoria INT NOT NULL,
    IdPelicula  INT NOT NULL,
    IdEdicion   INT NOT NULL,
    CONSTRAINT PK_Pre       PRIMARY KEY (IdPremio),
    CONSTRAINT UQ_PreCatEdi UNIQUE      (IdCategoria, IdEdicion),
    CONSTRAINT FK_Pre_Cat   FOREIGN KEY (IdCategoria) REFERENCES Categorias,
    CONSTRAINT FK_Pre_Pel   FOREIGN KEY (IdPelicula)  REFERENCES Peliculas,
    CONSTRAINT FK_Pre_Edi   FOREIGN KEY (IdEdicion)   REFERENCES Ediciones
);

/* ============================================================
   E. ASISTENTES, TARIFAS, ENTRADAS Y ABONOS
   ============================================================ */

CREATE TABLE Asistentes
(
    IdAsistente     SERIAL,
    Nombre          VARCHAR(100) NOT NULL,
    Email           VARCHAR(100) NOT NULL,
    Telefono        VARCHAR(20),
    TipoAsistente   VARCHAR(15)  NOT NULL DEFAULT 'General'
                        CHECK (TipoAsistente IN ('General','Prensa','Industria','VIP','Jurado')),
    CONSTRAINT PK_Asi      PRIMARY KEY (IdAsistente),
    CONSTRAINT UQ_AsiEmail UNIQUE      (Email)
);

CREATE TABLE Tarifas
(
    IdTarifa    SERIAL,
    NombreTarifa VARCHAR(30)   NOT NULL,
    Precio       NUMERIC(10,2) NOT NULL CHECK (Precio >= 0),
    CONSTRAINT PK_Tar PRIMARY KEY (IdTarifa)
);

CREATE TABLE Entradas
(
    IdEntrada    SERIAL,
    IdAsistente  INT       NOT NULL,
    IdProyeccion INT,
    IdEvento     INT,
    IdTarifa     INT       NOT NULL,
    FechaCompra  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT PK_Ent          PRIMARY KEY (IdEntrada),
    CONSTRAINT CK_Ent_Destino  CHECK (
                                   (IdProyeccion IS NOT NULL AND IdEvento IS NULL) OR
                                   (IdProyeccion IS NULL     AND IdEvento IS NOT NULL)
                               ),
    CONSTRAINT FK_Ent_Asi      FOREIGN KEY (IdAsistente)  REFERENCES Asistentes,
    CONSTRAINT FK_Ent_Proy     FOREIGN KEY (IdProyeccion) REFERENCES Proyecciones,
    CONSTRAINT FK_Ent_Evt      FOREIGN KEY (IdEvento)     REFERENCES EventosParalelos,
    CONSTRAINT FK_Ent_Tar      FOREIGN KEY (IdTarifa)     REFERENCES Tarifas
);

CREATE UNIQUE INDEX UX_Ent_AsiProy
    ON Entradas (IdAsistente, IdProyeccion)
    WHERE IdProyeccion IS NOT NULL;

CREATE UNIQUE INDEX UX_Ent_AsiEvt
    ON Entradas (IdAsistente, IdEvento)
    WHERE IdEvento IS NOT NULL;

CREATE TABLE TiposAbono
(
    IdTipoAbono SERIAL,
    NombreAbono VARCHAR(60)   NOT NULL,
    Descripcion VARCHAR(200),
    Precio      NUMERIC(10,2) NOT NULL CHECK (Precio >= 0),
    CONSTRAINT PK_TipoAb PRIMARY KEY (IdTipoAbono)
);

CREATE TABLE Abonos
(
    IdAbono     SERIAL,
    IdAsistente INT         NOT NULL,
    IdTipoAbono INT         NOT NULL,
    IdEdicion   INT         NOT NULL,
    FechaCompra TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CodigoAcceso VARCHAR(20) NOT NULL,
    Pagado      BOOLEAN     NOT NULL DEFAULT FALSE,
    CONSTRAINT PK_Ab      PRIMARY KEY (IdAbono),
    CONSTRAINT UQ_AbCod   UNIQUE      (CodigoAcceso),
    CONSTRAINT FK_Ab_Asi  FOREIGN KEY (IdAsistente) REFERENCES Asistentes,
    CONSTRAINT FK_Ab_Tipo FOREIGN KEY (IdTipoAbono) REFERENCES TiposAbono,
    CONSTRAINT FK_Ab_Edi  FOREIGN KEY (IdEdicion)   REFERENCES Ediciones
);

/* ============================================================
   F. LOGISTICA Y PATROCINIOS
   ============================================================ */

CREATE TABLE Hoteles
(
    IdHotel     SERIAL,
    NombreHotel VARCHAR(100) NOT NULL,
    Direccion   VARCHAR(200),
    Estrellas   INT CHECK (Estrellas BETWEEN 1 AND 5),
    CONSTRAINT PK_Hot PRIMARY KEY (IdHotel)
);

CREATE TABLE Alojamientos
(
    IdAlojamiento   SERIAL,
    IdPersonal      INT         NOT NULL,
    IdHotel         INT         NOT NULL,
    IdEdicion       INT         NOT NULL,
    NroHabitacion   VARCHAR(10) NOT NULL,
    CheckIn         DATE        NOT NULL,
    CheckOut        DATE        NOT NULL,
    CONSTRAINT PK_Aloj        PRIMARY KEY (IdAlojamiento),
    CONSTRAINT CK_Aloj_Fechas CHECK       (CheckOut > CheckIn),
    CONSTRAINT FK_Aloj_Per    FOREIGN KEY (IdPersonal) REFERENCES Personal,
    CONSTRAINT FK_Aloj_Hot    FOREIGN KEY (IdHotel)    REFERENCES Hoteles,
    CONSTRAINT FK_Aloj_Edi    FOREIGN KEY (IdEdicion)  REFERENCES Ediciones
);

CREATE TABLE Traslados
(
    IdTraslado   SERIAL,
    IdPersonal   INT          NOT NULL,
    IdEdicion    INT          NOT NULL,
    TipoTraslado VARCHAR(10)  NOT NULL CHECK (TipoTraslado IN ('Vuelo','Transfer')),
    Origen       VARCHAR(100) NOT NULL,
    Destino      VARCHAR(100) NOT NULL,
    FechaHora    TIMESTAMP    NOT NULL,
    NroVuelo     VARCHAR(20),
    CONSTRAINT PK_Tras     PRIMARY KEY (IdTraslado),
    CONSTRAINT FK_Tras_Per FOREIGN KEY (IdPersonal) REFERENCES Personal,
    CONSTRAINT FK_Tras_Edi FOREIGN KEY (IdEdicion)  REFERENCES Ediciones
);

CREATE TABLE Patrocinadores
(
    IdPatrocinador SERIAL,
    NombreEmpresa  VARCHAR(100) NOT NULL,
    Contacto       VARCHAR(100),
    Email          VARCHAR(100),
    CONSTRAINT PK_Patr PRIMARY KEY (IdPatrocinador)
);

CREATE TABLE PatrocinioEdicion
(
    IdPatrocinio    SERIAL,
    IdPatrocinador  INT          NOT NULL,
    IdEdicion       INT          NOT NULL,
    TipoAporte      VARCHAR(10)  NOT NULL CHECK (TipoAporte IN ('Economico','Especie')),
    Monto           NUMERIC(12,2),
    DescripcionAporte VARCHAR(200),
    CONSTRAINT PK_PatEdi     PRIMARY KEY (IdPatrocinio),
    CONSTRAINT FK_PatEdi_Pat FOREIGN KEY (IdPatrocinador) REFERENCES Patrocinadores,
    CONSTRAINT FK_PatEdi_Edi FOREIGN KEY (IdEdicion)      REFERENCES Ediciones
);

/* ============================================================
   ALTER TABLE - columnas adicionales
   ============================================================ */

ALTER TABLE Sedes ADD COLUMN SitioWeb VARCHAR(100);
ALTER TABLE Patrocinadores ADD COLUMN RedesSociales VARCHAR(150);
ALTER TABLE Personal ADD COLUMN Nacionalidad VARCHAR(60);
ALTER TABLE Abonos ADD CONSTRAINT UQ_Ab_AsiTipo UNIQUE (IdAsistente, IdTipoAbono);

/* ============================================================
   DATOS DE PRUEBA
   ============================================================ */

INSERT INTO Generos (NombreGenero) VALUES
    ('Drama'), ('Sci-Fi'), ('Documental'),
    ('Thriller'), ('Comedia'), ('Animacion');

INSERT INTO Peliculas (Titulo, AnioProd, Duracion, PaisOrigen, Sinopsis, Clasificacion, Formato, Estado) VALUES
    ('El Ultimo Tren del Sur',  2024, 112, 'Argentina', 'Un viaje ferroviario que cambia la vida de sus pasajeros.',      'PG',    'Digital',  'Seleccionada'),
    ('Memoria de Cenizas',      2023,  98, 'Bolivia',   'Un anciano busca recuperar su historia antes de morir.',         'PG-13', 'Digital',  'Seleccionada'),
    ('Mas Alla del Horizonte',  2024, 134, 'Mexico',    'Una mision espacial enfrenta el dilema de volver a casa.',       'PG-13', 'IMAX',     'Seleccionada'),
    ('La Sal de la Tierra',     2023,  87, 'Colombia',  'Documental sobre comunidades afrodescendientes del Pacifico.',   'ATP',   '35mm',     'Seleccionada'),
    ('Ruido Blanco',            2024, 105, 'Chile',     'Un compositor pierde el oido y busca otra forma de crear.',      'PG',    'Digital',  'Seleccionada'),
    ('El Jardin de los Suenos', 2023,  76, 'Peru',      'Animacion que explora el inconsciente colectivo andino.',        'ATP',   'Digital',  'Premiada'),
    ('Codigo Rojo',             2024, 118, 'Brasil',    'Thriller politico en los pasillos del poder latinoamericano.',   'R',     'Digital',  'Seleccionada');

INSERT INTO PeliculaGenero (IdPelicula, IdGenero) VALUES
    (1,1),(1,4),(2,1),(2,3),(3,2),(3,4),(4,3),(5,1),(5,6),(6,6),(7,4);

INSERT INTO Personal (Nombre, Biografia, Email, Telefono, Nacionalidad) VALUES
    ('Maria Fernanda Rios',  'Directora argentina premiada en Sundance.',        'mfrios@cine.ar',    '+54911000001', 'Argentina'),
    ('Jorge Luis Mamani',    'Director boliviano, documental y ficcion.',         'jmamani@cine.bo',   '+59176000002', 'Bolivia'),
    ('Valentina Cruz',       'Actriz mexicana con 15 anos de trayectoria.',       'vcruz@cine.mx',     '+52155000003', 'Mexico'),
    ('Carlos Herrera',       'Guionista colombiano, especialista en documental.', 'cherrera@cine.co',  '+57310000004', 'Colombia'),
    ('Ana Sofia Delgado',    'Productora chilena, 10 filmes internacionales.',    'asdelgado@cine.cl', '+56992000005', 'Chile'),
    ('Diego Ramos',          'Actor y director peruano, cine de animacion.',      'dramos@cine.pe',    '+51987000006', 'Peru'),
    ('Luisa Montoya',        'Actriz brasilena, teatro y cine.',                  'lmontoya@cine.br',  '+55119000007', 'Brasil'),
    ('Fernando Quiroga',     'Director de fotografia, Bolivia.',                  'fquiroga@cine.bo',  '+59172000008', 'Bolivia');

INSERT INTO RolesPelicula (IdPersonal, IdPelicula, Rol) VALUES
    (1,1,'Director'),(3,1,'Actor'),
    (2,2,'Director'),(2,2,'Guionista'),
    (3,3,'Actor'),(5,3,'Productor'),
    (4,4,'Guionista'),(8,4,'Director'),
    (5,5,'Productor'),(1,5,'Director'),
    (6,6,'Director'),(6,6,'Actor'),
    (7,7,'Actor'),(4,7,'Guionista');

INSERT INTO Ediciones (Anio, NombreEdicion, FechaInicio, FechaFin) VALUES
    (2024, 'FestCine 2024 - I Edicion',   '2024-06-15', '2024-06-22'),
    (2025, 'FestCine 2025 - II Edicion',  '2025-06-14', '2025-06-21'),
    (2026, 'FestCine 2026 - III Edicion', '2026-06-20', '2026-06-27');

INSERT INTO Sedes (NombreSede, Direccion, Ciudad, SitioWeb) VALUES
    ('Cine Centro',      'Av. Monsenor Rivero 345',    'Santa Cruz de la Sierra', 'www.cinecentro.bo'),
    ('Teatro Municipal', 'Plaza 24 de Septiembre s/n', 'Santa Cruz de la Sierra', 'www.teatromunicipal.bo'),
    ('Multicine Norte',  'Av. Banzer km 5',            'Santa Cruz de la Sierra', 'www.multicinorte.bo');

INSERT INTO Salas (NombreSala, Capacidad, IdSede) VALUES
    ('Sala Lumiere',    120, 1),
    ('Sala Eisenstein',  80, 1),
    ('Sala Principal',  200, 2),
    ('Sala Municipal',   60, 2),
    ('Sala Norte A',    150, 3),
    ('Sala Norte B',     90, 3);

INSERT INTO Proyecciones (IdPelicula, IdSala, IdEdicion, FechaHora, TieneQA, AforoDisponible) VALUES
    (1, 1, 3, '2026-06-20 19:00:00', TRUE,  120),
    (2, 2, 3, '2026-06-20 20:00:00', FALSE,  80),
    (3, 3, 3, '2026-06-21 18:00:00', TRUE,  200),
    (4, 4, 3, '2026-06-21 20:30:00', FALSE,  60),
    (5, 5, 3, '2026-06-22 19:00:00', FALSE, 150),
    (6, 6, 3, '2026-06-22 17:00:00', TRUE,   90),
    (7, 1, 3, '2026-06-23 21:00:00', FALSE, 120),
    (1, 3, 3, '2026-06-24 19:00:00', FALSE, 200),
    (3, 5, 3, '2026-06-24 21:00:00', TRUE,  150),
    (2, 6, 3, '2026-06-25 18:30:00', FALSE,  90),
    (5, 2, 3, '2026-06-25 20:00:00', TRUE,   80),
    (6, 4, 3, '2026-06-26 17:00:00', FALSE,  60);

INSERT INTO EventosParalelos (IdEdicion, NombreEvento, TipoEvento, FechaHora, Aforo, CostoInscripcion) VALUES
    (3, 'Masterclass: Narrativa Visual en el Cine Latinoamericano', 'Masterclass', '2026-06-21 10:00:00', 50,  0),
    (3, 'Taller: Guion para Cine Independiente',                    'Taller',      '2026-06-22 09:00:00', 30, 50),
    (3, 'Coctel de Inauguracion FestCine 2026',                     'Coctel',      '2026-06-20 21:00:00',100,  0),
    (3, 'Taller: Direccion de Actores',                             'Taller',      '2026-06-23 10:00:00', 25, 80);

INSERT INTO ExpositorEvento (IdEvento, IdPersonal) VALUES
    (1,1),(1,2),(2,4),(3,5),(4,1);

INSERT INTO Categorias (NombreCategoria, Descripcion) VALUES
    ('Mejor Pelicula',     'La mejor obra del festival en su conjunto.'),
    ('Mejor Director',     'La direccion mas destacada del festival.'),
    ('Mejor Cortometraje', 'Obra de menos de 30 minutos.'),
    ('Premio del Publico', 'Votado por los asistentes al festival.'),
    ('Mejor Documental',   'La mejor obra de no ficcion.');

INSERT INTO MiembrosJurado (Nombre, Profesion, Pais, Email) VALUES
    ('Roberto Calderon', 'Critico de Cine',      'Espana',    'rcalderon@critica.es'),
    ('Isabel Vargas',    'Directora de Cine',    'Argentina', 'ivargas@cine.ar'),
    ('Michael Brown',    'Productor',            'USA',       'mbrown@films.us'),
    ('Claudia Mendez',   'Periodista Cultural',  'Mexico',    'cmendez@cultura.mx'),
    ('Remy Fontaine',    'Director de Festival', 'Francia',   'rfontaine@festival.fr');

INSERT INTO JuradoCategoria (IdMiembro, IdCategoria) VALUES
    (1,1),(1,2),(2,1),(2,3),(3,1),(3,4),(4,2),(4,5),(5,3),(5,5);

INSERT INTO CompetenciaPelicula (IdPelicula, IdCategoria, IdEdicion) VALUES
    (1,1,1),(2,1,1),(3,1,1),(4,1,1),
    (1,2,1),(3,2,1),
    (4,5,1),(2,5,1),
    (6,3,1),
    (1,4,1),(2,4,1),(3,4,1);

INSERT INTO Evaluaciones (IdMiembro, IdPelicula, IdCategoria, IdEdicion, Puntuacion, Comentario) VALUES
    (1,1,1,1,9,'Narrativa impecable y actuaciones sublimes.'),
    (1,2,1,1,7,'Buena historia, ritmo algo lento.'),
    (1,3,1,1,8,'Visualmente deslumbrante.'),
    (1,4,1,1,6,'Correcto pero sin grandes sorpresas.'),
    (2,1,1,1,8,'Gran direccion de actores.'),
    (2,2,1,1,9,'Conmovedora y necesaria.'),
    (2,3,1,1,7,'Ambiciosa aunque irregular.'),
    (2,4,1,1,8,'Documental honesto y revelador.'),
    (3,1,1,1,7,'Solida propuesta cinematografica.'),
    (3,2,1,1,8,'Emotiva y bien construida.'),
    (3,3,1,1,9,'Ciencia ficcion con alma.'),
    (3,4,1,1,6,'Tema importante, ejecucion regular.'),
    (1,1,2,1,9,'Direccion magistral.'),
    (1,3,2,1,8,'Gran control del ritmo.'),
    (4,1,2,1,8,'Domina los espacios con maestria.'),
    (4,3,2,1,9,'Referencia del cine de genero.'),
    (2,6,3,1,10,'Animacion que supera expectativas.'),
    (5,6,3,1,9,'Original y poetico.'),
    (3,1,4,1,8,'El publico la ama.'),
    (3,2,4,1,7,'Emotiva y accesible.'),
    (3,3,4,1,9,'Espectacular experiencia.'),
    (4,4,5,1,8,'Documental necesario.'),
    (4,2,5,1,9,'Profundo y bien investigado.'),
    (5,4,5,1,7,'Solido aunque predecible.'),
    (5,2,5,1,8,'Emotivo y revelador.');

INSERT INTO Premios (IdCategoria, IdPelicula, IdEdicion) VALUES
    (1,2,3),(2,3,3),(3,6,3),(5,2,3);

INSERT INTO Tarifas (NombreTarifa, Precio) VALUES
    ('General',    35.00),
    ('Estudiante', 20.00),
    ('Jubilado',   15.00),
    ('Acreditado',  0.00);

INSERT INTO Asistentes (Nombre, Email, Telefono, TipoAsistente) VALUES
    ('Juan Pablo Torrez',  'jptorrez@gmail.com',   '72000001', 'General'),
    ('Carla Suarez',       'csuarez@gmail.com',    '72000002', 'General'),
    ('Pedro Flores',       'pflores@gmail.com',    '72000003', 'General'),
    ('Lucia Mendoza',      'lmendoza@gmail.com',   '72000004', 'General'),
    ('Roberto Vaca',       'rvaca@gmail.com',       '72000005', 'General'),
    ('Patricia Guzman',    'pguzman@gmail.com',    '72000006', 'Prensa'),
    ('Carlos Diaz',        'cdiaz@gmail.com',      '72000007', 'Prensa'),
    ('Andres Salinas',     'asalinas@gmail.com',   '72000008', 'General'),
    ('Monica Pereira',     'mpereira@gmail.com',   '72000009', 'General'),
    ('Fernando Castro',    'fcastro@gmail.com',    '72000010', 'Industria'),
    ('Silvana Torres',     'storres@gmail.com',    '72000011', 'VIP'),
    ('Marcos Quispe',      'mquispe@gmail.com',    '72000012', 'General'),
    ('Elena Rodriguez',    'erodriguez@gmail.com', '72000013', 'General'),
    ('Hugo Alvarado',      'halvarado@gmail.com',  '72000014', 'General'),
    ('Natalia Benitez',    'nbenitez@gmail.com',   '72000015', 'General'),
    ('Gabriel Chavez',     'gchavez@gmail.com',    '72000016', 'General'),
    ('Rosa Mamani',        'rmamani@gmail.com',    '72000017', 'General'),
    ('Sebastian Lopez',    'slopez@gmail.com',     '72000018', 'General'),
    ('Daniela Pinto',      'dpinto@gmail.com',     '72000019', 'Jurado'),
    ('Oscar Medina',       'omedina@gmail.com',    '72000020', 'General'),
    ('Valeria Nunez',      'vnunez@gmail.com',     '72000021', 'Industria'),
    ('Tomas Arce',         'tarce@gmail.com',      '72000022', 'General');

INSERT INTO Entradas (IdAsistente, IdProyeccion, IdEvento, IdTarifa) VALUES
    (1,  1, NULL, 1), (2,  1, NULL, 1), (3,  1, NULL, 2),
    (4,  2, NULL, 2), (5,  2, NULL, 1), (6,  2, NULL, 4),
    (7,  3, NULL, 4), (8,  3, NULL, 1), (9,  3, NULL, 1),
    (10, 4, NULL, 4), (11, 4, NULL, 4), (12, 4, NULL, 1),
    (13, 5, NULL, 2), (14, 5, NULL, 1), (15, 5, NULL, 3),
    (16, 6, NULL, 2), (17, 6, NULL, 1), (18, 6, NULL, 1),
    (19, 7, NULL, 4), (20, 7, NULL, 1);

INSERT INTO Entradas (IdAsistente, IdProyeccion, IdEvento, IdTarifa) VALUES
    (8,  NULL, 1, 4),
    (9,  NULL, 2, 1),
    (10, NULL, 2, 4);

INSERT INTO TiposAbono (NombreAbono, Descripcion, Precio) VALUES
    ('Abono Fin de Semana', 'Acceso ilimitado sabado y domingo.',  150.00),
    ('Abono Total',         'Acceso a todas las proyecciones.',    400.00),
    ('Abono Prensa',        'Acceso completo para medios.',          0.00);

INSERT INTO Abonos (IdAsistente, IdTipoAbono, IdEdicion, CodigoAcceso, Pagado) VALUES
    (21, 1, 3, 'AB-2026-001', TRUE),
    (22, 2, 3, 'AB-2026-002', TRUE),
    (6,  3, 3, 'AB-2026-003', TRUE),
    (7,  3, 3, 'AB-2026-004', TRUE),
    (10, 1, 3, 'AB-2026-005', TRUE);

INSERT INTO Hoteles (NombreHotel, Direccion, Estrellas) VALUES
    ('Los Tajibos Hotel',   'Av. San Martin 455, Santa Cruz', 5),
    ('Hotel Cortez',        'Av. Cristobal de Mendoza 280',   4),
    ('Marriott Santa Cruz', 'Av. San Martin 1700',            5);

INSERT INTO Alojamientos (IdPersonal, IdHotel, IdEdicion, NroHabitacion, CheckIn, CheckOut) VALUES
    (1, 1, 3, '401', '2026-06-19', '2026-06-27'),
    (2, 2, 3, '205', '2026-06-19', '2026-06-27'),
    (3, 1, 3, '402', '2026-06-20', '2026-06-26'),
    (6, 3, 3, '310', '2026-06-18', '2026-06-28');

INSERT INTO Traslados (IdPersonal, IdEdicion, TipoTraslado, Origen, Destino, FechaHora, NroVuelo) VALUES
    (1, 3, 'Vuelo',    'Buenos Aires (EZE)', 'Santa Cruz (VVI)', '2026-06-19 08:00:00', 'LA832'),
    (2, 3, 'Vuelo',    'La Paz (LPB)',       'Santa Cruz (VVI)', '2026-06-19 10:30:00', 'OB101'),
    (3, 3, 'Vuelo',    'Ciudad de Mexico',   'Santa Cruz (VVI)', '2026-06-20 06:00:00', 'AM543'),
    (6, 3, 'Vuelo',    'Lima (LIM)',         'Santa Cruz (VVI)', '2026-06-18 14:00:00', 'LA2081'),
    (1, 3, 'Transfer', 'Santa Cruz (VVI)',   'Los Tajibos Hotel','2026-06-19 11:00:00', NULL);

INSERT INTO Patrocinadores (NombreEmpresa, Contacto, Email, RedesSociales) VALUES
    ('Banco Union',          'Lic. Patricia Heredia', 'pheredia@bancounion.com.bo', '@bancounionbo'),
    ('YPFB',                 'Ing. Carlos Morales',   'cmorales@ypfb.com.bo',       '@ypfboficial'),
    ('Tigo Bolivia',         'Lic. Andres Vidal',     'avidal@tigo.com.bo',         '@tigobolivia'),
    ('Cerveceria Boliviana', 'Sr. Pedro Roca',        'proca@cbba.com.bo',          '@cbbaoficial');

INSERT INTO PatrocinioEdicion (IdPatrocinador, IdEdicion, TipoAporte, Monto, DescripcionAporte) VALUES
    (1,1,'Economico',50000, 'Patrocinio principal I edicion'),
    (2,1,'Especie',  NULL,  'Logistica de combustible'),
    (1,2,'Economico',60000, 'Patrocinio principal II edicion'),
    (3,2,'Economico',20000, 'Patrocinio tecnologia'),
    (1,3,'Economico',75000, 'Patrocinio principal III edicion'),
    (2,3,'Economico',30000, 'Patrocinio energia'),
    (3,3,'Especie',  NULL,  'Conectividad del evento'),
    (4,3,'Especie',  NULL,  'Bebidas para eventos');

/* ============================================================
   VISTAS
   ============================================================ */

CREATE OR REPLACE VIEW vw_Peliculas AS
    SELECT p.IdPelicula, p.Titulo, p.AnioProd, p.Duracion,
           p.PaisOrigen, p.Clasificacion, p.Formato, p.Estado,
           COALESCE(STRING_AGG(g.NombreGenero, ', '), '') AS Generos
      FROM Peliculas p
      LEFT JOIN PeliculaGenero pg ON pg.IdPelicula = p.IdPelicula
      LEFT JOIN Generos g         ON g.IdGenero    = pg.IdGenero
     WHERE p.Estado IN ('Seleccionada', 'Premiada')
     GROUP BY p.IdPelicula
     ORDER BY p.Titulo;

CREATE OR REPLACE VIEW vw_Proyecciones AS
    SELECT pr.IdProyeccion, pe.IdPelicula, pe.Titulo, pe.Duracion,
           sa.IdSala, sa.NombreSala, se.NombreSede,
           pr.FechaHora, pr.AforoDisponible, sa.Capacidad,
           pr.TieneQA, pr.IdEdicion,
           ed.Anio, ed.NombreEdicion
      FROM Proyecciones pr
      INNER JOIN Peliculas pe ON pe.IdPelicula = pr.IdPelicula
      INNER JOIN Salas sa     ON sa.IdSala     = pr.IdSala
      INNER JOIN Sedes se     ON se.IdSede     = sa.IdSede
      INNER JOIN Ediciones ed ON ed.IdEdicion  = pr.IdEdicion
     ORDER BY pr.FechaHora;

CREATE OR REPLACE VIEW vw_Tarifas AS
    SELECT IdTarifa, NombreTarifa, Precio
      FROM Tarifas ORDER BY Precio DESC;

CREATE OR REPLACE VIEW vw_Asistentes AS
    SELECT IdAsistente, Nombre, Email, TipoAsistente
      FROM Asistentes;

CREATE OR REPLACE VIEW vw_TiposAbono AS
    SELECT IdTipoAbono, NombreAbono, Descripcion, Precio
      FROM TiposAbono;

CREATE OR REPLACE VIEW vw_Salas AS
    SELECT sa.IdSala, sa.NombreSala, sa.Capacidad,
           se.IdSede, se.NombreSede
      FROM Salas sa
      INNER JOIN Sedes se ON se.IdSede = sa.IdSede;

CREATE OR REPLACE VIEW vw_Eventos AS
    SELECT e.IdEvento, e.IdEdicion, e.NombreEvento, e.TipoEvento,
           e.FechaHora, e.Aforo, e.CostoInscripcion,
           ed.Anio, ed.NombreEdicion,
           COALESCE(STRING_AGG(p.Nombre, ', '), '') AS Expositores
      FROM EventosParalelos e
      INNER JOIN Ediciones ed ON ed.IdEdicion = e.IdEdicion
      LEFT JOIN ExpositorEvento ee ON ee.IdEvento = e.IdEvento
      LEFT JOIN Personal p         ON p.IdPersonal = ee.IdPersonal
     GROUP BY e.IdEvento, ed.Anio, ed.NombreEdicion
     ORDER BY e.FechaHora;

CREATE OR REPLACE VIEW vw_Abonos AS
    SELECT a.IdAbono, a.IdAsistente, asis.Nombre AS NombreAsistente,
           a.IdTipoAbono, ta.NombreAbono, ta.Descripcion, ta.Precio,
           a.IdEdicion, ed.Anio, ed.NombreEdicion,
           a.CodigoAcceso, a.Pagado, a.FechaCompra
      FROM Abonos a
      INNER JOIN Asistentes asis ON asis.IdAsistente = a.IdAsistente
      INNER JOIN TiposAbono ta   ON ta.IdTipoAbono   = a.IdTipoAbono
      INNER JOIN Ediciones ed    ON ed.IdEdicion     = a.IdEdicion
     ORDER BY a.FechaCompra DESC;

CREATE OR REPLACE VIEW vw_Premios AS
    SELECT pre.IdPremio, pre.IdCategoria, c.NombreCategoria,
           pre.IdPelicula, p.Titulo AS TituloPelicula,
           pre.IdEdicion, ed.Anio, ed.NombreEdicion
      FROM Premios pre
      INNER JOIN Categorias c ON c.IdCategoria  = pre.IdCategoria
      INNER JOIN Peliculas p  ON p.IdPelicula   = pre.IdPelicula
      INNER JOIN Ediciones ed ON ed.IdEdicion   = pre.IdEdicion
     ORDER BY ed.Anio DESC, c.NombreCategoria;

/* ============================================================
   PROCEDIMIENTO: ComprarEntrada
   ============================================================ */

CREATE OR REPLACE PROCEDURE ComprarEntrada(
    IN  p_IdAsistente  INT,
    IN  p_IdProyeccion INT,
    IN  p_IdTarifa     INT,
    OUT p_Respuesta    VARCHAR(300)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_Aforo     INT;
    v_Titulo    VARCHAR(150);
    v_FechaHora TIMESTAMP;
    v_YaCompro  INT;
BEGIN
    SELECT pr.AforoDisponible, pe.Titulo, pr.FechaHora
        INTO v_Aforo, v_Titulo, v_FechaHora
        FROM Proyecciones pr
        INNER JOIN Peliculas pe ON pe.IdPelicula = pr.IdPelicula
        WHERE pr.IdProyeccion = p_IdProyeccion;
    IF NOT FOUND THEN
        p_Respuesta := 'Error: La proyeccion indicada no existe.'; RETURN;
    END IF;
    SELECT COUNT(*) INTO v_YaCompro
        FROM Entradas
        WHERE IdAsistente = p_IdAsistente AND IdProyeccion = p_IdProyeccion;
    IF v_YaCompro > 0 THEN
        p_Respuesta := 'Error: El asistente ya tiene una entrada para esta proyeccion.'; RETURN;
    END IF;
    IF v_Aforo <= 0 THEN
        p_Respuesta := 'Lo sentimos, no hay aforo disponible para esta funcion.'; RETURN;
    END IF;
    INSERT INTO Entradas (IdAsistente, IdProyeccion, IdTarifa)
        VALUES (p_IdAsistente, p_IdProyeccion, p_IdTarifa);
    UPDATE Proyecciones
        SET AforoDisponible = AforoDisponible - 1
        WHERE IdProyeccion = p_IdProyeccion;
    p_Respuesta := 'Entrada registrada exitosamente para "' || v_Titulo ||
                   '" el ' || TO_CHAR(v_FechaHora, 'DD/MM/YYYY HH24:MI') || '.';
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error inesperado: ' || SQLERRM;
END; $$;

/* ============================================================
   PROCEDIMIENTO: VenderAbono
   ============================================================ */

CREATE OR REPLACE PROCEDURE VenderAbono(
    IN  p_IdAsistente  INT,
    IN  p_IdTipoAbono  INT,
    IN  p_IdEdicion    INT,
    IN  p_PagoExitoso  BOOLEAN,
    OUT p_Respuesta    VARCHAR(300)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_CodigoAcceso VARCHAR(20);
    v_NombreAbono  VARCHAR(60);
    v_Precio       NUMERIC(10,2);
    v_NombreAsist  VARCHAR(100);
    v_NroAbono     INT;
BEGIN
    SELECT NombreAbono, Precio INTO v_NombreAbono, v_Precio
        FROM TiposAbono WHERE IdTipoAbono = p_IdTipoAbono;
    IF NOT FOUND THEN
        p_Respuesta := 'Error: El tipo de abono indicado no existe.'; RETURN;
    END IF;
    SELECT Nombre INTO v_NombreAsist
        FROM Asistentes WHERE IdAsistente = p_IdAsistente;
    IF NOT FOUND THEN
        p_Respuesta := 'Error: El asistente indicado no existe.'; RETURN;
    END IF;
    v_CodigoAcceso := 'AB-' || TO_CHAR(CURRENT_DATE, 'YYYY') || '-' ||
                      LPAD(CAST(FLOOR(RANDOM() * 90000 + 10000) AS TEXT), 5, '0');
    IF p_PagoExitoso = FALSE THEN
        RAISE EXCEPTION 'Pasarela de pago fallida. Operacion cancelada.';
    END IF;
    INSERT INTO Abonos (IdAsistente, IdTipoAbono, IdEdicion, CodigoAcceso, Pagado)
        VALUES (p_IdAsistente, p_IdTipoAbono, p_IdEdicion, v_CodigoAcceso, TRUE)
        RETURNING IdAbono INTO v_NroAbono;
    p_Respuesta := 'Abono registrado. Cod. acceso: ' || v_CodigoAcceso;
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error: ' || SQLERRM;
END; $$;

/* ============================================================
   PROCEDIMIENTO: ProgramarProyeccion
   ============================================================ */

CREATE OR REPLACE PROCEDURE ProgramarProyeccion(
    IN  p_IdPelicula  INT,
    IN  p_IdSala      INT,
    IN  p_IdEdicion   INT,
    IN  p_FechaHora   TIMESTAMP,
    IN  p_TieneQA     BOOLEAN,
    OUT p_IdNuevo     INT,
    OUT p_Respuesta   VARCHAR(300)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_Capacidad INT;
BEGIN
    SELECT Capacidad INTO v_Capacidad FROM Salas WHERE IdSala = p_IdSala;
    IF NOT FOUND THEN
        p_IdNuevo := NULL; p_Respuesta := 'Error: La sala indicada no existe.'; RETURN;
    END IF;
    INSERT INTO Proyecciones (IdPelicula, IdSala, IdEdicion, FechaHora, TieneQA, AforoDisponible)
        VALUES (p_IdPelicula, p_IdSala, p_IdEdicion, p_FechaHora, p_TieneQA, v_Capacidad)
        RETURNING IdProyeccion INTO p_IdNuevo;
    p_Respuesta := 'Proyeccion programada exitosamente. ID: ' || p_IdNuevo::TEXT;
EXCEPTION WHEN OTHERS THEN
    p_IdNuevo := NULL; p_Respuesta := 'Error: ' || SQLERRM;
END; $$;

/* ============================================================
   TRIGGER: ControlAgenda
   ============================================================ */

CREATE OR REPLACE FUNCTION fn_ControlAgenda()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_Duracion    INT;
    v_FinNueva    TIMESTAMP;
    v_Conflicto   INT;
    v_TituloOcupa VARCHAR(150);
BEGIN
    SELECT Duracion INTO v_Duracion FROM Peliculas WHERE IdPelicula = NEW.IdPelicula;
    v_FinNueva := NEW.FechaHora + (v_Duracion + 30) * INTERVAL '1 minute';
    SELECT COUNT(*), MAX(pe.Titulo) INTO v_Conflicto, v_TituloOcupa
        FROM Proyecciones pr
        INNER JOIN Peliculas pe ON pe.IdPelicula = pr.IdPelicula
        WHERE pr.IdSala = NEW.IdSala
          AND pr.IdProyeccion <> COALESCE(NEW.IdProyeccion, -1)
          AND NEW.FechaHora < (pr.FechaHora + (pe.Duracion + 30) * INTERVAL '1 minute')
          AND v_FinNueva > pr.FechaHora;
    IF v_Conflicto > 0 THEN
        RAISE EXCEPTION
            'Control de Agenda: La sala ya esta ocupada por "%" en ese horario (incluidos 30 min de limpieza).',
            v_TituloOcupa;
    END IF;
    RETURN NEW;
END; $$;

CREATE OR REPLACE TRIGGER TR_ControlAgenda
    BEFORE INSERT OR UPDATE ON Proyecciones
    FOR EACH ROW EXECUTE FUNCTION fn_ControlAgenda();

/* ============================================================
   PROCEDIMIENTOS DE REPORTE (via RAISE NOTICE)
   ============================================================ */

CREATE OR REPLACE PROCEDURE sp_ReporteRanking(
    IN  p_IdEdicion  INT,
    OUT p_Respuesta  VARCHAR(200)
)
LANGUAGE plpgsql AS $$
DECLARE r RECORD;
BEGIN
    RAISE NOTICE '=== RANKING DE PELICULAS (Edicion: %) ===', COALESCE(p_IdEdicion::TEXT, 'TODAS');
    FOR r IN (
        SELECT p.Titulo,
               COUNT(e.IdEntrada) AS Asistentes,
               SUM(s.Capacidad) AS CapacidadTotal,
               ROUND(COUNT(e.IdEntrada) * 100.0 / NULLIF(SUM(s.Capacidad), 0), 2) AS PctOcupacion
          FROM Peliculas p
          INNER JOIN Proyecciones pr ON pr.IdPelicula = p.IdPelicula
          INNER JOIN Salas s ON s.IdSala = pr.IdSala
          LEFT JOIN Entradas e ON e.IdProyeccion = pr.IdProyeccion
         WHERE (p_IdEdicion IS NULL OR pr.IdEdicion = p_IdEdicion)
         GROUP BY p.Titulo
         ORDER BY Asistentes DESC
    ) LOOP
        RAISE NOTICE 'Pelicula: % | Asistentes: % | Ocupacion: %', r.Titulo, r.Asistentes, r.PctOcupacion || '%';
    END LOOP;
    p_Respuesta := 'Ranking generado exitosamente.';
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error al generar ranking: ' || SQLERRM;
END; $$;

CREATE OR REPLACE PROCEDURE sp_ReportePremiacion(
    IN  p_IdEdicion  INT,
    OUT p_Respuesta  VARCHAR(200)
)
LANGUAGE plpgsql AS $$
DECLARE r RECORD;
BEGIN
    RAISE NOTICE '=== ACTA DE PREMIACION (Edicion: %) ===', COALESCE(p_IdEdicion::TEXT, 'TODAS');
    FOR r IN (
        SELECT c.NombreCategoria, p.Titulo AS PeliculaGanadora,
               ROUND(AVG(ev.Puntuacion), 2) AS PromedioJurado, e.Anio
          FROM Premios pre
          INNER JOIN Categorias c ON c.IdCategoria = pre.IdCategoria
          INNER JOIN Peliculas p ON p.IdPelicula = pre.IdPelicula
          INNER JOIN Ediciones e ON e.IdEdicion = pre.IdEdicion
          INNER JOIN Evaluaciones ev ON ev.IdPelicula = pre.IdPelicula AND ev.IdCategoria = pre.IdCategoria AND ev.IdEdicion = pre.IdEdicion
         WHERE (p_IdEdicion IS NULL OR pre.IdEdicion = p_IdEdicion)
         GROUP BY c.NombreCategoria, p.Titulo, e.Anio
         ORDER BY c.NombreCategoria
    ) LOOP
        RAISE NOTICE 'Categoria: % | Ganadora: % | Promedio Jurado: %', r.NombreCategoria, r.PeliculaGanadora, r.PromedioJurado;
    END LOOP;
    p_Respuesta := 'Acta de premiacion generada exitosamente.';
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error al generar acta: ' || SQLERRM;
END; $$;

CREATE OR REPLACE PROCEDURE sp_ReporteFinanciero(
    IN  p_IdEdicion  INT,
    OUT p_Respuesta  VARCHAR(200)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_TotalEntradas NUMERIC := 0;
    v_TotalAbonos NUMERIC := 0;
    r RECORD;
BEGIN
    RAISE NOTICE '=== INFORME FINANCIERO (Edicion: %) ===', COALESCE(p_IdEdicion::TEXT, 'TODAS');
    FOR r IN (
        SELECT t.NombreTarifa, COUNT(e.IdEntrada) AS Cantidad, SUM(t.Precio) AS Subtotal
          FROM Entradas e
          INNER JOIN Proyecciones pr ON pr.IdProyeccion = e.IdProyeccion
          INNER JOIN Tarifas t ON t.IdTarifa = e.IdTarifa
         WHERE (p_IdEdicion IS NULL OR pr.IdEdicion = p_IdEdicion)
         GROUP BY t.NombreTarifa ORDER BY Subtotal DESC
    ) LOOP
        RAISE NOTICE 'Entrada - % | Cant: % | Subtotal: Bs. %', r.NombreTarifa, r.Cantidad, r.Subtotal;
        v_TotalEntradas := v_TotalEntradas + r.Subtotal;
    END LOOP;
    FOR r IN (
        SELECT ta.NombreAbono, COUNT(a.IdAbono) AS Cantidad, SUM(ta.Precio) AS Subtotal
          FROM Abonos a INNER JOIN TiposAbono ta ON ta.IdTipoAbono = a.IdTipoAbono
         WHERE a.Pagado = TRUE AND (p_IdEdicion IS NULL OR a.IdEdicion = p_IdEdicion)
         GROUP BY ta.NombreAbono ORDER BY Subtotal DESC
    ) LOOP
        RAISE NOTICE 'Abono - % | Cant: % | Subtotal: Bs. %', r.NombreAbono, r.Cantidad, r.Subtotal;
        v_TotalAbonos := v_TotalAbonos + r.Subtotal;
    END LOOP;
    RAISE NOTICE 'TOTAL GENERAL: Bs. %', v_TotalEntradas + v_TotalAbonos;
    p_Respuesta := 'Total general: Bs. ' || (v_TotalEntradas + v_TotalAbonos)::TEXT;
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error al generar informe: ' || SQLERRM;
END; $$;

/* ============================================================
   FUNCIONES WRAPPER para backend
   ============================================================ */

CREATE OR REPLACE FUNCTION fn_call_comprarentrada(
    p_IdAsistente INT, p_IdProyeccion INT, p_IdTarifa INT
) RETURNS TABLE (respuesta VARCHAR(300)) LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL ComprarEntrada(p_IdAsistente, p_IdProyeccion, p_IdTarifa, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

CREATE OR REPLACE FUNCTION fn_call_venderabono(
    p_IdAsistente INT, p_IdTipoAbono INT, p_IdEdicion INT, p_PagoExitoso BOOLEAN
) RETURNS TABLE (respuesta VARCHAR(300)) LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL VenderAbono(p_IdAsistente, p_IdTipoAbono, p_IdEdicion, p_PagoExitoso, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

CREATE OR REPLACE FUNCTION fn_call_programarproyeccion(
    p_IdPelicula INT, p_IdSala INT, p_IdEdicion INT, p_FechaHora TEXT, p_TieneQA BOOLEAN
) RETURNS TABLE (respuesta VARCHAR(300)) LANGUAGE plpgsql AS $$
DECLARE v_id INT; v_resp VARCHAR(300);
BEGIN
    CALL ProgramarProyeccion(p_IdPelicula, p_IdSala, p_IdEdicion, p_FechaHora::TIMESTAMP, p_TieneQA, v_id, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

CREATE OR REPLACE FUNCTION fn_call_reporteranking(
    p_IdEdicion INT DEFAULT NULL
) RETURNS TABLE (respuesta VARCHAR(300)) LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL sp_ReporteRanking(p_IdEdicion, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

CREATE OR REPLACE FUNCTION fn_call_reportepremiacion(
    p_IdEdicion INT DEFAULT NULL
) RETURNS TABLE (respuesta VARCHAR(300)) LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL sp_ReportePremiacion(p_IdEdicion, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

CREATE OR REPLACE FUNCTION fn_call_reporterinanciero(
    p_IdEdicion INT DEFAULT NULL
) RETURNS TABLE (respuesta VARCHAR(300)) LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL sp_ReporteFinanciero(p_IdEdicion, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

/* ============================================================
   CONSULTAS DE VERIFICACION
   ============================================================ */

SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
SELECT COUNT(*) AS TotalPeliculas FROM Peliculas;
SELECT COUNT(*) AS TotalProyecciones FROM Proyecciones;
SELECT COUNT(*) AS TotalAsistentes FROM Asistentes;
SELECT COUNT(*) AS TotalEntradas FROM Entradas;
SELECT * FROM vw_Peliculas;
SELECT * FROM vw_Proyecciones;
SELECT * FROM vw_Salas;
SELECT * FROM vw_Eventos;
SELECT * FROM vw_Abonos;
SELECT * FROM vw_Premios;
