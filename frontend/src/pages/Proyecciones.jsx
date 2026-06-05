import { useState, useEffect } from 'react'
import api from '../api'

export default function Proyecciones() {
  const [proyecciones, setProyecciones] = useState([])
  const [sedes, setSedes] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedSede, setSelectedSede] = useState('All')

  useEffect(() => {
    Promise.all([
      api.getProyecciones(),
      api.getSedes()
    ]).then(([proy, sed]) => {
      setProyecciones(proy)
      setSedes(sed)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const filteredProyecciones = proyecciones.filter(p => {
    const matchesSede = selectedSede === 'All' || p.NombreSede === selectedSede
    return matchesSede
  })

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Programación de Funciones</h2>
        
        {/* Filters */}
        <div style={{ display: 'flex', gap: 12 }}>

          <select className="select" value={selectedSede} onChange={e => setSelectedSede(e.target.value)} style={{ width: 180, padding: '8px 12px' }}>
            <option value="All">Todas las Sedes</option>
            {sedes.map(s => <option key={s.IdSede} value={s.NombreSede}>{s.NombreSede}</option>)}
          </select>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <div style={{ display: 'inline-block', width: 40, height: 40, border: '4px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--accent-purple)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
          <p style={{ marginTop: 12, color: 'var(--text-secondary)' }}>Cargando programación oficial...</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 24 }}>
          {filteredProyecciones.length === 0 ? (
            <div className="glass-card" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: 40, color: 'var(--text-secondary)' }}>
              No hay funciones programadas para los filtros seleccionados.
            </div>
          ) : (
            filteredProyecciones.map(p => {
              const capPercentage = Math.round((p.AforoDisponible / p.Capacidad) * 100)
              const isLowCapacity = p.AforoDisponible <= 10

              return (
                <div key={p.IdProyeccion} className="glass-card animate-scale-in" style={{
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  background: 'rgba(21, 30, 48, 0.4)',
                  borderLeft: '4px solid var(--accent-purple)'
                }}>
                  {/* Q&A Ribbon */}
                  {p.TieneQA && (
                    <span style={{
                      position: 'absolute',
                      top: 16,
                      right: 16,
                      fontSize: 10,
                      fontWeight: 800,
                      background: 'rgba(16, 185, 129, 0.15)',
                      color: '#10b981',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                      padding: '3px 8px',
                      borderRadius: 4,
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em'
                    }}>
                      Incluye Q&A
                    </span>
                  )}

                  <div>
                    <h3 style={{ fontSize: 19, fontWeight: 800, margin: '0 0 8px 0', paddingRight: p.TieneQA ? 90 : 0 }}>
                      {p.Titulo}
                    </h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>
                      Duración: {p.Duracion} min
                    </p>

                    {/* Venue & Hall */}
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 16 }}>
                      <div style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: 'var(--accent-pink)'
                      }}></div>
                      <span style={{ fontSize: 14, fontWeight: 600 }}>{p.NombreSede}</span>
                      <span style={{ color: 'var(--text-secondary)' }}>·</span>
                      <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>{p.NombreSala}</span>
                    </div>

                    {/* Date/Time badge */}
                    <div style={{
                      background: 'rgba(255,255,255,0.03)',
                      border: '1px solid rgba(255,255,255,0.05)',
                      borderRadius: 8,
                      padding: '8px 12px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: 20
                    }}>
                      <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Fecha y Hora</span>
                      <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
                        {new Date(p.FechaHora).toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'short' })} a las {new Date(p.FechaHora).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>

                  {/* Capacity Info */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Asientos disponibles</span>
                      <span style={{ fontWeight: 700, color: isLowCapacity ? 'var(--accent-rose)' : 'var(--text-primary)' }}>
                        {p.AforoDisponible} / {p.Capacidad}
                      </span>
                    </div>

                    {/* Progress bar */}
                    <div style={{
                      height: 6,
                      background: 'rgba(255,255,255,0.06)',
                      borderRadius: 3,
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${capPercentage}%`,
                        height: '100%',
                        background: isLowCapacity 
                          ? 'linear-gradient(to right, var(--accent-rose), #be123c)' 
                          : 'linear-gradient(to right, var(--accent-purple), var(--accent-pink))',
                        borderRadius: 3,
                        transition: 'width 0.4s ease-in-out'
                      }}></div>
                    </div>

                    {isLowCapacity && (
                      <p style={{ fontSize: 11, color: 'var(--accent-rose)', fontWeight: 600, marginTop: 6, textAlign: 'right' }}>
                        {p.AforoDisponible === 0 ? 'Función agotada' : '¡Últimas entradas disponibles!'}
                      </p>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
      )}
      
      {/* Spinner rotation style */}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
