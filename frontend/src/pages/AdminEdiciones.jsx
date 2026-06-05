import { useState, useEffect } from 'react'
import api from '../api'

export default function AdminEdiciones() {
  const [ediciones, setEdiciones] = useState([])
  const [form, setForm] = useState({ Anio: '', NombreEdicion: '', FechaInicio: '', FechaFin: '' })
  const [editing, setEditing] = useState(null)
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)

  const loadEdiciones = async () => {
    setLoading(true)
    try {
      const data = await api.getEdiciones()
      setEdiciones(data)
    } catch (err) {
      setMsg('Error al cargar ediciones: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadEdiciones()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMsg('')
    
    // Validations
    if (new Date(form.FechaFin) <= new Date(form.FechaInicio)) {
      setMsg('Error: La fecha de finalización debe ser posterior a la de inicio.')
      return
    }

    try {
      const payload = {
        ...form,
        Anio: parseInt(form.Anio)
      }
      if (editing) {
        await api.updateEdicion(editing, payload)
        setMsg('Edición actualizada con éxito')
      } else {
        await api.createEdicion(payload)
        setMsg('Edición creada con éxito')
      }
      setForm({ Anio: '', NombreEdicion: '', FechaInicio: '', FechaFin: '' })
      setEditing(null)
      loadEdiciones()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  const handleEdit = (ed) => {
    setEditing(ed.IdEdicion)
    setForm({
      Anio: String(ed.Anio),
      NombreEdicion: ed.NombreEdicion,
      FechaInicio: ed.FechaInicio,
      FechaFin: ed.FechaFin
    })
  }

  const handleDelete = async (id) => {
    if (!window.confirm('¡ATENCIÓN! Eliminar esta edición eliminará en cascada todas sus proyecciones, eventos paralelos, alojamientos, traslados, abonos y ventas de esta edición. ¿Realmente desea continuar?')) return
    setMsg('')
    try {
      await api.deleteEdicion(id)
      setMsg('Edición eliminada con éxito')
      if (editing === id) {
        setEditing(null)
        setForm({ Anio: '', NombreEdicion: '', FechaInicio: '', FechaFin: '' })
      }
      loadEdiciones()
    } catch (err) {
      setMsg('Error: ' + err.message)
    }
  }

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Ediciones del Festival</h2>
        {msg && <div style={{ padding: '8px 16px', background: 'rgba(139, 92, 246, 0.15)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 8, fontSize: 13, color: '#c084fc', fontWeight: 600 }}>{msg}</div>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: 24, alignItems: 'start' }}>
        <div className="glass-card">
          <h3 style={{ fontSize: 18, marginBottom: 16 }}>{editing ? 'Editar Edición' : 'Registrar Nueva Edición'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Año de la Edición *</label>
              <input className="input" type="number" min="2000" max="2100" placeholder="Ej. 2026" value={form.Anio} onChange={e => setForm({ ...form, Anio: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">Nombre Comercial *</label>
              <input className="input" placeholder="Ej. FestCine 2026 - III Edición" value={form.NombreEdicion} onChange={e => setForm({ ...form, NombreEdicion: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">Fecha de Inicio *</label>
              <input className="input" type="date" value={form.FechaInicio} onChange={e => setForm({ ...form, FechaInicio: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">Fecha de Finalización *</label>
              <input className="input" type="date" value={form.FechaFin} onChange={e => setForm({ ...form, FechaFin: e.target.value })} required />
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 24 }}>
              <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>{editing ? 'Actualizar' : 'Guardar'}</button>
              {editing && (
                <button type="button" className="btn btn-secondary" onClick={() => { setEditing(null); setForm({ Anio: '', NombreEdicion: '', FechaInicio: '', FechaFin: '' }) }}>
                  Cancelar
                </button>
              )}
            </div>
          </form>
        </div>

        <div>
          {loading && <p style={{ color: 'var(--text-secondary)' }}>Cargando ediciones...</p>}
          
          {!loading && (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Año</th>
                    <th>Nombre de Edición</th>
                    <th>Fecha Inicio</th>
                    <th>Fecha Fin</th>
                    <th style={{ textAlign: 'right' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {ediciones.length === 0 ? (
                    <tr>
                      <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 30 }}>
                        No hay ediciones registradas.
                      </td>
                    </tr>
                  ) : (
                    ediciones.map(ed => (
                      <tr key={ed.IdEdicion}>
                        <td style={{ fontWeight: 700, color: 'var(--accent-pink)' }}>{ed.Anio}</td>
                        <td style={{ fontWeight: 600 }}>{ed.NombreEdicion}</td>
                        <td>{new Date(ed.FechaInicio).toLocaleDateString('es-ES', { timeZone: 'UTC' })}</td>
                        <td>{new Date(ed.FechaFin).toLocaleDateString('es-ES', { timeZone: 'UTC' })}</td>
                        <td style={{ textAlign: 'right' }}>
                          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                            <button onClick={() => handleEdit(ed)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 12 }}>Editar</button>
                            <button onClick={() => handleDelete(ed.IdEdicion)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: 12 }}>Eliminar</button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
