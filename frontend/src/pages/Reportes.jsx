import { useState, useEffect } from 'react'
import api from '../api'

export default function Reportes() {
  const [tab, setTab] = useState('ranking')
  const [ediciones, setEdiciones] = useState([])
  const [idEdicion, setIdEdicion] = useState('')
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getEdiciones().then(e => {
      setEdiciones(e)
      if (e.length > 0) setIdEdicion(e[0].IdEdicion.toString())
    })
  }, [])

  useEffect(() => {
    setLoading(true)
    const ed = idEdicion ? parseInt(idEdicion) : null
    const fetchers = {
      ranking: () => api.getRanking(ed),
      premiacion: () => api.getPremiacion(ed),
      financiero: () => api.getFinanciero(ed),
      ocupacion: () => api.getOcupacionSalas(),
    }
    fetchers[tab]().then(d => { setData(d); setLoading(false) })
  }, [tab, idEdicion])

  const tabs = [
    { key: 'ranking', label: 'Ranking Películas' },
    { key: 'premiacion', label: 'Acta Premiación' },
    { key: 'financiero', label: 'Informe Financiero' },
    { key: 'ocupacion', label: 'Ocupación Salas' },
  ]

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ fontSize: 28, fontWeight: 800, margin: 0 }}>Reportes y Estadísticas</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            Monitoree la asistencia, premiaciones, finanzas y ocupación física de salas.
          </p>
        </div>
        {tab !== 'ocupacion' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)' }}>Edición:</span>
            <select value={idEdicion} onChange={e => setIdEdicion(e.target.value)} className="select" style={{ width: 220, padding: '8px 12px' }}>
              <option value="">Todas las ediciones</option>
              {ediciones.map(e => <option key={e.IdEdicion} value={e.IdEdicion}>{e.NombreEdicion}</option>)}
            </select>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
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

      {loading ? (
        <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-secondary)' }}>
          Cargando reporte...
        </div>
      ) : (
        <div className="glass-card" style={{ padding: 20 }}>
          {tab === 'ranking' && <RankingTable data={data} />}
          {tab === 'premiacion' && <PremiacionTable data={data} />}
          {tab === 'financiero' && <FinancieroTable data={data} />}
          {tab === 'ocupacion' && <OcupacionTable data={data} />}
        </div>
      )}
    </div>
  )
}

function RankingTable({ data }) {
  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Película</th>
            <th>Espectadores</th>
            <th>Capacidad Max</th>
            <th style={{ textAlign: 'right' }}>Porcentaje Ocupación</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Sin registros en esta edición</td></tr>
          ) : (
            data.map((r, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600 }}>{r.Titulo}</td>
                <td>{r.Asistentes}</td>
                <td>{r.CapacidadTotal}</td>
                <td style={{ textAlign: 'right' }}>
                  <span className={`badge ${r.PctOcupacion >= 80 ? 'badge-premiada' : r.PctOcupacion >= 50 ? 'badge-seleccionada' : 'badge-postulada'}`}>
                    {r.PctOcupacion}%
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

function PremiacionTable({ data }) {
  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Categoría</th>
            <th>Película Ganadora</th>
            <th>Promedio Jurado</th>
            <th style={{ textAlign: 'right' }}>Año Edición</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No se registran ganadores oficiales para esta edición</td></tr>
          ) : (
            data.map((r, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600 }}>{r.NombreCategoria}</td>
                <td>
                  <span className="badge badge-premiada" style={{ marginRight: 8 }}>🏆 GANADORA</span>
                  {r.PeliculaGanadora}
                </td>
                <td>
                  <span style={{ color: 'var(--accent-amber)', fontWeight: 700 }}>★ {parseFloat(r.PromedioJurado).toFixed(2)}</span>
                </td>
                <td style={{ textAlign: 'right', color: 'var(--text-secondary)' }}>{r.Anio}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

function FinancieroTable({ data }) {
  const total = data.reduce((s, r) => s + parseFloat(r.Subtotal || 0), 0)
  return (
    <div>
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Tarifa / Tipo Venta</th>
              <th>Cantidad Vendida</th>
              <th style={{ textAlign: 'right' }}>Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {data.length === 0 ? (
              <tr><td colSpan={3} style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Sin ingresos registrados</td></tr>
            ) : (
              data.map((r, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{r.NombreTarifa}</td>
                  <td>{r.Cantidad}</td>
                  <td style={{ textAlign: 'right', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                    Bs. {parseFloat(r.Subtotal).toFixed(2)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 16, padding: '12px 20px', background: 'rgba(16, 185, 129, 0.08)', borderRadius: 8, border: '1px solid rgba(16, 185, 129, 0.15)' }}>
        <span style={{ fontSize: 16, fontWeight: 800, color: '#fff' }}>
          TOTAL RECAUDADO: <span style={{ color: 'var(--accent-emerald)', marginLeft: 8 }}>Bs. {total.toFixed(2)}</span>
        </span>
      </div>
    </div>
  )
}

function OcupacionTable({ data }) {
  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>Sala</th>
            <th>Sede</th>
            <th>Capacidad Máxima</th>
            <th>Boletos Emitidos</th>
            <th style={{ textAlign: 'right' }}>Porcentaje Ocupación</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>No hay datos de ocupación de salas</td></tr>
          ) : (
            data.map((r, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600 }}>{r.NombreSala}</td>
                <td>{r.NombreSede}</td>
                <td>{r.Capacidad}</td>
                <td>{r.EntradasVendidas}</td>
                <td style={{ textAlign: 'right' }}>
                  <span className={`badge ${r.PorcentajeOcupacion >= 80 ? 'badge-premiada' : r.PorcentajeOcupacion >= 50 ? 'badge-seleccionada' : 'badge-postulada'}`}>
                    {r.PorcentajeOcupacion}%
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

