import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminJurados() {
  const [jurados, setJurados] = useState([])
  const [categorias, setCategorias] = useState([])
  const [peliculas, setPeliculas] = useState([])
  const [evaluaciones, setEvaluaciones] = useState([])
  const [premios, setPremios] = useState([])
  const [ediciones, setEdiciones] = useState([])
  const [tab, setTab] = useState('jurados')
  const [formJ, setFormJ] = useState({ Nombre: '', Profesion: '', Pais: '', Email: '' })
  const [formEval, setFormEval] = useState({ IdMiembro: '', IdPelicula: '', IdCategoria: '', Puntuacion: '5', Comentario: '' })
  const [formPremio, setFormPremio] = useState({ IdCategoria: '', IdPelicula: '' })
  const [categoriasFiltradas, setCategoriasFiltradas] = useState([])
  const [peliculasFiltradas, setPeliculasFiltradas] = useState([])
  const [msg, setMsg] = useState('')

  useEffect(() => {
    Promise.all([
      api.getJurados(), api.getCategorias(), api.getPeliculas(),
      api.getEvaluaciones(), api.getPremios(), api.getEdiciones()
    ]).then(([j, c, p, ev, pr, ed]) => { setJurados(j); setCategorias(c); setPeliculas(p); setEvaluaciones(ev); setPremios(pr); setEdiciones(ed) })
  }, [])

  const crearJurado = async (e) => {
    e.preventDefault()
    try { 
      const r = await api.createJurado?.(formJ) || await (await fetch('/api/jurados', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formJ) })).json()
      setMsg('Miembro del jurado registrado exitosamente')
      setFormJ({ Nombre: '', Profesion: '', Pais: '', Email: '' })
      api.getJurados().then(setJurados)
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  const handleJuradoChange = async (e) => {
    const id = e.target.value
    setFormEval({ ...formEval, IdMiembro: id, IdCategoria: '', IdPelicula: '' })
    setCategoriasFiltradas([])
    setPeliculasFiltradas([])
    if (id) {
      const cats = await api.getCategoriasPorJurado(id)
      setCategoriasFiltradas(cats)
    }
  }

  const handleCategoriaChange = async (e) => {
    const id = e.target.value
    setFormEval({ ...formEval, IdCategoria: id, IdPelicula: '' })
    setPeliculasFiltradas([])
    if (id) {
      const pels = await api.getPeliculasPorCategoria(id)
      setPeliculasFiltradas(pels)
    }
  }

  const crearEvaluacion = async (e) => {
    e.preventDefault()
    try {
      const res = await api.createEvaluacion({
        ...formEval,
        IdMiembro: parseInt(formEval.IdMiembro),
        IdPelicula: parseInt(formEval.IdPelicula),
        IdCategoria: parseInt(formEval.IdCategoria),
        IdEdicion: 1,
        Puntuacion: parseInt(formEval.Puntuacion)
      })
      setMsg('Evaluación del jurado registrada exitosamente')
      setFormEval({ IdMiembro: '', IdPelicula: '', IdCategoria: '', Puntuacion: '5', Comentario: '' })
      setCategoriasFiltradas([])
      api.getEvaluaciones().then(setEvaluaciones)
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  const crearPremio = async (e) => {
    e.preventDefault()
    try {
      await api.createPremio({ ...formPremio, IdCategoria: parseInt(formPremio.IdCategoria), IdPelicula: parseInt(formPremio.IdPelicula) })
      setMsg('Galardón oficial otorgado exitosamente')
      setFormPremio({ IdCategoria: '', IdPelicula: '' })
      api.getPremios().then(setPremios)
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  const eliminarPremio = async (id) => {
    if (!window.confirm('¿Revocar este galardón? Esta acción no se puede deshacer.')) return
    try {
      await api.deletePremio(id)
      setMsg('Galardón revocado correctamente')
      api.getPremios().then(setPremios)
    } catch (err) { setMsg('Error: ' + err.message) }
  }

  const tabs = [
    { key: 'jurados', label: 'Miembros de Jurado' },
    { key: 'evaluaciones', label: 'Evaluaciones y Puntajes' },
    { key: 'premios', label: 'Palmarés y Premios' },
  ]

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Comisión de Evaluación y Premios</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            Gestione el jurado internacional, registre calificaciones y formalice el palmarés de ganadores.
          </p>
        </div>
        {msg && <div style={{ padding: '8px 16px', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 8, fontSize: 13, color: '#c084fc', fontWeight: 600 }}>{msg}</div>}
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => { setTab(t.key); setMsg(''); }}
            className="btn"
            style={{ 
              background: tab === t.key ? 'linear-gradient(135deg, var(--accent-purple), var(--accent-pink))' : 'rgba(255,255,255,0.05)', 
              color: '#fff',
              border: tab === t.key ? 'none' : '1px solid rgba(255,255,255,0.08)'
            }}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'jurados' && (
        <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>Registrar Jurado</h3>
            <form onSubmit={crearJurado}>
              <div className="form-group">
                <label className="form-label">Nombre Completo *</label>
                <input placeholder="Ej. Jane Doe" className="input" value={formJ.Nombre} onChange={e => setFormJ({ ...formJ, Nombre: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Profesión / Especialidad</label>
                <input placeholder="Ej. Crítica de Cine" className="input" value={formJ.Profesion} onChange={e => setFormJ({ ...formJ, Profesion: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">País de Origen</label>
                <input placeholder="Ej. Francia" className="input" value={formJ.Pais} onChange={e => setFormJ({ ...formJ, Pais: e.target.value })} />
              </div>
              <div className="form-group">
                <label className="form-label">Email de Contacto</label>
                <input placeholder="Ej. jdoe@jurado-festcine.org" type="email" className="input" value={formJ.Email} onChange={e => setFormJ({ ...formJ, Email: e.target.value })} />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>
                Registrar Jurado
              </button>
            </form>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Profesión</th>
                  <th>País de Origen</th>
                  <th>Contacto</th>
                </tr>
              </thead>
              <tbody>
                {jurados.length === 0 ? (
                  <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 20 }}>No hay miembros de jurado registrados.</td></tr>
                ) : (
                  jurados.map(j => (
                    <tr key={j.IdMiembro}>
                      <td style={{ fontWeight: 600 }}>{j.Nombre}</td>
                      <td>{j.Profesion || '-'}</td>
                      <td>{j.Pais || '-'}</td>
                      <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{j.Email || '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'evaluaciones' && (
        <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>Calificar Película</h3>
            <form onSubmit={crearEvaluacion}>
              <div className="form-group">
                <label className="form-label">Miembro de Jurado *</label>
                <select className="select" value={formEval.IdMiembro} onChange={handleJuradoChange} required>
                  <option value="">Seleccione jurado...</option>
                  {jurados.map(j => <option key={j.IdMiembro} value={j.IdMiembro}>{j.Nombre}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Película *</label>
                <select className="select" value={formEval.IdPelicula} onChange={e => setFormEval({ ...formEval, IdPelicula: e.target.value })} required>
                  <option value="">{formEval.IdCategoria ? 'Seleccione película...' : 'Primero seleccione categoría'}</option>
                  {peliculasFiltradas.map(p => <option key={p.IdPelicula} value={p.IdPelicula}>{p.Titulo}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Categoría Competitiva *</label>
                <select className="select" value={formEval.IdCategoria} onChange={handleCategoriaChange} required>
                  <option value="">{formEval.IdMiembro ? 'Seleccione categoría...' : 'Primero seleccione un jurado'}</option>
                  {categoriasFiltradas.map(c => <option key={c.IdCategoria} value={c.IdCategoria}>{c.NombreCategoria}</option>)}
                </select>
              </div>


              <div className="form-group">
                <label className="form-label">Puntuación (1 al 10) *</label>
                <input type="number" min="1" max="10" placeholder="Puntaje" className="input" value={formEval.Puntuacion} onChange={e => setFormEval({ ...formEval, Puntuacion: e.target.value })} required />
              </div>

              <div className="form-group">
                <label className="form-label">Comentarios / Crítica</label>
                <textarea placeholder="Reseña u observaciones del jurado..." rows={2} className="textarea" value={formEval.Comentario} onChange={e => setFormEval({ ...formEval, Comentario: e.target.value })} />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>
                Registrar Evaluación
              </button>
            </form>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Jurado</th>
                  <th>Película</th>
                  <th>Categoría</th>
                  <th style={{ textAlign: 'right' }}>Puntuación</th>
                </tr>
              </thead>
              <tbody>
                {evaluaciones.length === 0 ? (
                  <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 20 }}>No se registran calificaciones oficiales de películas.</td></tr>
                ) : (
                  evaluaciones.map(e => (
                    <tr key={e.IdEvaluacion}>
                      <td style={{ fontWeight: 600 }}>{e.Jurado}</td>
                      <td>{e.Pelicula}</td>
                      <td>
                        <span className="badge badge-postulada">{e.Categoria}</span>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 700, color: 'var(--accent-amber)' }}>
                        ★ {e.Puntuacion}/10
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'premios' && (
        <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 24, alignItems: 'start' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>Declarar Ganador</h3>
            <form onSubmit={crearPremio}>
              <div className="form-group">
                <label className="form-label">Categoría del Galardón *</label>
                <select className="select" value={formPremio.IdCategoria} onChange={e => setFormPremio({ ...formPremio, IdCategoria: e.target.value })} required>
                  <option value="">Seleccione categoría...</option>
                  {categorias.map(c => <option key={c.IdCategoria} value={c.IdCategoria}>{c.NombreCategoria}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Película Ganadora *</label>
                <select className="select" value={formPremio.IdPelicula} onChange={e => setFormPremio({ ...formPremio, IdPelicula: e.target.value })} required>
                  <option value="">Seleccione película...</option>
                  {peliculas.map(p => <option key={p.IdPelicula} value={p.IdPelicula}>{p.Titulo}</option>)}
                </select>
              </div>



              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 12 }}>
                Otorgar Premio
              </button>
            </form>
          </div>

          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Categoría</th>
                  <th>Película Ganadora</th>
                  <th>Edición</th>
                  <th style={{ textAlign: 'right' }}>Acción</th>
                </tr>
              </thead>
              <tbody>
                {premios.length === 0 ? (
                  <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 20 }}>No se registran premios para esta edición.</td></tr>
                ) : (
                  premios.map(p => (
                    <tr key={p.IdPremio}>
                      <td style={{ fontWeight: 600 }}>{p.NombreCategoria}</td>
                      <td>
                        <span className="badge badge-premiada" style={{ marginRight: 8 }}>🏆 PREMIO</span>
                        {p.Pelicula}
                      </td>
                      <td style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{p.NombreEdicion}</td>
                      <td style={{ textAlign: 'right' }}>
                        <button onClick={() => eliminarPremio(p.IdPremio)} className="btn" style={{ padding: '4px 10px', fontSize: 12, background: 'rgba(239,68,68,0.15)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)' }}>
                          Revocar
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

