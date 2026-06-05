const API = '/api';

async function request(url, options = {}) {
  const res = await fetch(`${API}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Error de red');
  return data;
}

export const api = {
  // Peliculas
  getPeliculas: () => request('/peliculas'),
  getPelicula: (id) => request(`/peliculas/${id}`),
  createPelicula: (data) => request('/peliculas', { method: 'POST', body: JSON.stringify(data) }),
  updatePelicula: (id, data) => request(`/peliculas/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePelicula: (id) => request(`/peliculas/${id}`, { method: 'DELETE' }),

  // Proyecciones
  getProyecciones: () => request('/proyecciones'),
  createProyeccion: (data) => request('/proyecciones', { method: 'POST', body: JSON.stringify(data) }),
  deleteProyeccion: (id) => request(`/proyecciones/${id}`, { method: 'DELETE' }),

  // Asistentes
  getAsistentes: () => request('/asistentes'),
  createAsistente: (data) => request('/asistentes', { method: 'POST', body: JSON.stringify(data) }),

  // Entradas
  getEntradas: () => request('/entradas'),
  comprarEntrada: (data) => request('/entradas', { method: 'POST', body: JSON.stringify(data) }),

  // Abonos
  getAbonos: () => request('/abonos'),
  venderAbono: (data) => request('/abonos', { method: 'POST', body: JSON.stringify(data) }),

  // Tarifas
  getTarifas: () => request('/tarifas'),

  // Sedes
  getSedes: () => request('/sedes'),
  createSede: (data) => request('/sedes', { method: 'POST', body: JSON.stringify(data) }),

  // Salas
  getSalas: () => request('/salas'),
  createSala: (data) => request('/salas', { method: 'POST', body: JSON.stringify(data) }),

  // Eventos
  getEventos: () => request('/eventos'),
  createEvento: (data) => request('/eventos', { method: 'POST', body: JSON.stringify(data) }),

  // Generos
  getGeneros: () => request('/generos'),

  // Personal
  getPersonal: () => request('/personal'),

  // Categorias
  getCategorias: () => request('/categorias'),

  // Jurados
  getJurados: () => request('/jurados'),

  // Evaluaciones
  getEvaluaciones: () => request('/evaluaciones'),
  createEvaluacion: (data) => request('/evaluaciones', { method: 'POST', body: JSON.stringify(data) }),

  // Patrocinadores
  getPatrocinadores: () => request('/patrocinadores'),
  createPatrocinador: (data) => request('/patrocinadores', { method: 'POST', body: JSON.stringify(data) }),
  getPatrocinios: () => request('/patrocinadores/patrocinios'),
  createPatrocinio: (data) => request('/patrocinadores/patrocinios', { method: 'POST', body: JSON.stringify(data) }),

  // Ediciones
  getEdiciones: () => request('/ediciones'),

  // Premios
  getPremios: () => request('/premios'),
  createPremio: (data) => request('/premios', { method: 'POST', body: JSON.stringify(data) }),

  // Hoteles
  getHoteles: () => request('/hoteles'),

  // Alojamientos
  getAlojamientos: () => request('/alojamientos'),
  createAlojamiento: (data) => request('/alojamientos', { method: 'POST', body: JSON.stringify(data) }),

  // Traslados
  getTraslados: () => request('/traslados'),
  createTraslado: (data) => request('/traslados', { method: 'POST', body: JSON.stringify(data) }),

  // Competencia
  getCompetencia: () => request('/competencia'),
  createCompetencia: (data) => request('/competencia', { method: 'POST', body: JSON.stringify(data) }),

  // Reportes
  getRanking: (idEdicion) => idEdicion ? request(`/reportes/ranking?id_edicion=${idEdicion}`) : request('/reportes/ranking'),
  getPremiacion: (idEdicion) => idEdicion ? request(`/reportes/premiacion?id_edicion=${idEdicion}`) : request('/reportes/premiacion'),
  getFinanciero: (idEdicion) => idEdicion ? request(`/reportes/financiero?id_edicion=${idEdicion}`) : request('/reportes/financiero'),
  getOcupacionSalas: () => request('/reportes/ocupacion-salas'),
  getVentasEdicion: (id) => request(`/reportes/ventas-edicion/${id}`),
};

export default api;
