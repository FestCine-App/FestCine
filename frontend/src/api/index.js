const API = '/api';

async function request(url, options = {}) {
  const res = await fetch(`${API}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch (err) {
    console.error(`Error de parsing JSON en ${url}. Respuesta recibida:`, text);
    throw new Error(`El servidor de backend respondió con un formato incorrecto (Código ${res.status}). Asegúrate de que el servidor Django esté corriendo en http://localhost:8080 y que la base de datos esté accesible.`);
  }
  if (!res.ok) throw new Error(data.error || 'Error de red');
  return data;
}

export const api = {
  // Peliculas
  getPeliculas: () => request('/peliculas/'),
  getPelicula: (id) => request(`/peliculas/${id}/`),
  createPelicula: (data) => request('/peliculas/', { method: 'POST', body: JSON.stringify(data) }),
  updatePelicula: (id, data) => request(`/peliculas/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePelicula: (id) => request(`/peliculas/${id}/`, { method: 'DELETE' }),

  // Proyecciones
  getProyecciones: () => request('/proyecciones/'),
  createProyeccion: (data) => request('/proyecciones/', { method: 'POST', body: JSON.stringify(data) }),
  deleteProyeccion: (id) => request(`/proyecciones/${id}/`, { method: 'DELETE' }),

  // Asistentes
  getAsistentes: () => request('/asistentes/'),
  createAsistente: (data) => request('/asistentes/', { method: 'POST', body: JSON.stringify(data) }),

  // Entradas
  getEntradas: () => request('/entradas/'),
  comprarEntrada: (data) => request('/entradas/', { method: 'POST', body: JSON.stringify(data) }),

  // Abonos
  getAbonos: () => request('/abonos/'),
  venderAbono: (data) => request('/abonos/', { method: 'POST', body: JSON.stringify(data) }),
  getTiposAbono: () => request('/tipos-abono/'),

  // Tarifas
  getTarifas: () => request('/tarifas/'),

  // Sedes
  getSedes: () => request('/sedes/'),
  createSede: (data) => request('/sedes/', { method: 'POST', body: JSON.stringify(data) }),
  updateSede: (id, data) => request(`/sedes/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteSede: (id) => request(`/sedes/${id}/`, { method: 'DELETE' }),

  // Salas
  getSalas: () => request('/salas/'),
  createSala: (data) => request('/salas/', { method: 'POST', body: JSON.stringify(data) }),
  updateSala: (id, data) => request(`/salas/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteSala: (id) => request(`/salas/${id}/`, { method: 'DELETE' }),

  // Eventos
  getEventos: () => request('/eventos/'),
  createEvento: (data) => request('/eventos/', { method: 'POST', body: JSON.stringify(data) }),
  updateEvento: (id, data) => request(`/eventos/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteEvento: (id) => request(`/eventos/${id}/`, { method: 'DELETE' }),

  // Generos
  getGeneros: () => request('/generos/'),

  // Personal
  getPersonal: () => request('/personal/'),
  createPersonal: (data) => request('/personal/', { method: 'POST', body: JSON.stringify(data) }),
  updatePersonal: (id, data) => request(`/personal/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePersonal: (id) => request(`/personal/${id}/`, { method: 'DELETE' }),

  // Categorias
  getCategorias: () => request('/categorias/'),
  getCategoriasPorJurado: (idMiembro) => request(`/categorias/?jurado=${idMiembro}`),
  getPeliculasPorCategoria: (idCategoria) => request(`/categorias/?categoria=${idCategoria}`),
  createCategoria: (data) => request('/categorias/', { method: 'POST', body: JSON.stringify(data) }),
  updateCategoria: (id, data) => request(`/categorias/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteCategoria: (id) => request(`/categorias/${id}/`, { method: 'DELETE' }),

  // Jurados
  getJurados: () => request('/jurados/'),
  createJurado: (data) => request('/jurados/', { method: 'POST', body: JSON.stringify(data) }),
  updateJurado: (id, data) => request(`/jurados/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteJurado: (id) => request(`/jurados/${id}/`, { method: 'DELETE' }),

  // Evaluaciones
  getEvaluaciones: () => request('/evaluaciones/'),
  createEvaluacion: (data) => request('/evaluaciones/', { method: 'POST', body: JSON.stringify(data) }),
  updateEvaluacion: (id, data) => request(`/evaluaciones/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteEvaluacion: (id) => request(`/evaluaciones/${id}/`, { method: 'DELETE' }),

  // Patrocinadores
  getPatrocinadores: () => request('/patrocinadores/'),
  createPatrocinador: (data) => request('/patrocinadores/', { method: 'POST', body: JSON.stringify(data) }),
  updatePatrocinador: (id, data) => request(`/patrocinadores/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePatrocinador: (id) => request(`/patrocinadores/${id}/`, { method: 'DELETE' }),
  getPatrocinios: () => request('/patrocinios/'),
  createPatrocinio: (data) => request('/patrocinios/', { method: 'POST', body: JSON.stringify(data) }),
  updatePatrocinio: (id, data) => request(`/patrocinios/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePatrocinio: (id) => request(`/patrocinios/${id}/`, { method: 'DELETE' }),

  // Ediciones
  getEdiciones: () => request('/ediciones/'),
  createEdicion: (data) => request('/ediciones/', { method: 'POST', body: JSON.stringify(data) }),
  updateEdicion: (id, data) => request(`/ediciones/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteEdicion: (id) => request(`/ediciones/${id}/`, { method: 'DELETE' }),

  // Premios
  getPremios: () => request('/premios/'),
  createPremio: (data) => request('/premios/', { method: 'POST', body: JSON.stringify(data) }),
  deletePremio: (id) => request(`/premios/${id}/`, { method: 'DELETE' }),
  updatePremio: (id, data) => request(`/premios/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePremio: (id) => request(`/premios/${id}/`, { method: 'DELETE' }),

  // Hoteles
  getHoteles: () => request('/hoteles/'),
  createHotel: (data) => request('/hoteles/', { method: 'POST', body: JSON.stringify(data) }),
  updateHotel: (id, data) => request(`/hoteles/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteHotel: (id) => request(`/hoteles/${id}/`, { method: 'DELETE' }),

  // Alojamientos
  getAlojamientos: () => request('/alojamientos/'),
  createAlojamiento: (data) => request('/alojamientos/', { method: 'POST', body: JSON.stringify(data) }),
  updateAlojamiento: (id, data) => request(`/alojamientos/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteAlojamiento: (id) => request(`/alojamientos/${id}/`, { method: 'DELETE' }),

  // Traslados
  getTraslados: () => request('/traslados/'),
  createTraslado: (data) => request('/traslados/', { method: 'POST', body: JSON.stringify(data) }),
  updateTraslado: (id, data) => request(`/traslados/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTraslado: (id) => request(`/traslados/${id}/`, { method: 'DELETE' }),

  // Competencia
  getCompetencia: () => request('/competencia/'),
  createCompetencia: (data) => request('/competencia/', { method: 'POST', body: JSON.stringify(data) }),
  deleteCompetencia: (peliculaId, categoriaId, edicionId) => request(`/competencia/?pelicula=${peliculaId}&categoria=${categoriaId}&edicion=${edicionId}`, { method: 'DELETE' }),

  // Roles
  getRoles: (personalId, peliculaId) => {
    if (personalId) return request(`/roles/?personal=${personalId}`);
    if (peliculaId) return request(`/roles/?pelicula=${peliculaId}`);
    return request('/roles/');
  },
  createRol: (data) => request('/roles/', { method: 'POST', body: JSON.stringify(data) }),
  deleteRol: (personalId, peliculaId, rol) => request(`/roles/?personal=${personalId}&pelicula=${peliculaId}&rol=${rol}`, { method: 'DELETE' }),

  // Reportes

  getRanking: (idEdicion) => idEdicion ? request(`/reportes/ranking/?id_edicion=${idEdicion}`) : request('/reportes/ranking/'),
  getPremiacion: (idEdicion) => idEdicion ? request(`/reportes/premiacion/?id_edicion=${idEdicion}`) : request('/reportes/premiacion/'),
  getFinanciero: (idEdicion) => idEdicion ? request(`/reportes/financiero/?id_edicion=${idEdicion}`) : request('/reportes/financiero/'),
  getOcupacionSalas: () => request('/reportes/ocupacion-salas/'),
  getVentasEdicion: (id) => request(`/reportes/ventas-edicion/${id}/`),
};

export default api;
