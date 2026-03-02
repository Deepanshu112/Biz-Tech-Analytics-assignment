import React, { useState } from 'react';
import { Activity, Users, Monitor, Settings, RefreshCw, BarChart2, Package } from 'lucide-react';
import { useMetrics, seedData } from './api';

const Header = ({ onRefresh }) => (
  <header className="glass-panel" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <div style={{ background: 'var(--primary-accent)', padding: '0.5rem', borderRadius: '0.5rem' }}>
        <Activity size={24} color="white" />
      </div>
      <h2>AI Productivity Dashboard</h2>
    </div>
    <button onClick={onRefresh} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <RefreshCw size={16} /> Seed/Refresh Data
    </button>
  </header>
);

const FactorySummary = ({ metrics }) => (
  <div className="glass-panel animate-fade-in stagger-1" style={{ marginBottom: '2rem' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
      <BarChart2 size={24} color="var(--primary-accent)" />
      <h3>Factory Summary</h3>
    </div>
    <div className="grid grid-cols-4">
      <div className="metric-card">
        <span className="metric-label">Total Productive Time</span>
        <span className="metric-value">{(metrics.total_productive_time_s / 3600).toFixed(1)} hrs</span>
      </div>
      <div className="metric-card">
        <span className="metric-label">Total Production Count</span>
        <span className="metric-value">{metrics.total_production_count}</span>
      </div>
      <div className="metric-card">
        <span className="metric-label">Avg Units/Hour</span>
        <span className="metric-value">{metrics.avg_production_rate_per_hour.toFixed(2)}</span>
      </div>
      <div className="metric-card">
        <span className="metric-label">Avg Utilization</span>
        <span className="metric-value">{metrics.avg_utilization_percentage.toFixed(1)}%</span>
        <div className="progress-bg">
          <div className="progress-fill primary" style={{ width: `${metrics.avg_utilization_percentage}%` }}></div>
        </div>
      </div>
    </div>
  </div>
);

const WorkerList = ({ workers, filterId }) => {
  const filtered = filterId ? workers.filter(w => w.worker_id === filterId) : workers;

  return (
    <div className="glass-panel animate-fade-in stagger-2">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <Users size={24} color="var(--secondary-accent)" />
        <h3>Worker Performance</h3>
      </div>
      <div className="grid grid-cols-3">
        {filtered.map(w => (
          <div key={w.worker_id} style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div style={{ fontWeight: 600 }}>{w.name}</div>
              <span className={`badge ${w.utilization_percentage > 70 ? 'success' : w.utilization_percentage > 50 ? 'warning' : 'danger'}`}>
                {w.utilization_percentage.toFixed(0)}%
              </span>
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              <div>Active: {(w.total_active_time_s / 60).toFixed(0)} min</div>
              <div>Idle: {(w.total_idle_time_s / 60).toFixed(0)} min</div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Units</div>
                <div style={{ fontWeight: 600 }}>{w.total_units_produced}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>UPH</div>
                <div style={{ fontWeight: 600 }}>{w.units_per_hour}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const WorkstationList = ({ stations, filterId }) => {
  const filtered = filterId ? stations.filter(s => s.workstation_id === filterId) : stations;

  return (
    <div className="glass-panel animate-fade-in stagger-3">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <Monitor size={24} color="var(--warning-accent)" />
        <h3>Workstation Metrics</h3>
      </div>
      <div className="grid grid-cols-3">
        {filtered.map(s => (
          <div key={s.workstation_id} style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div style={{ fontWeight: 600 }}>{s.name}</div>
              <span className="badge info">Rate: {s.throughput_rate_per_hour} UPH</span>
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Occupancy: {(s.occupancy_time_s / 60).toFixed(0)} min
            </div>
            <div className="progress-bg">
              <div className="progress-fill success" style={{ width: `${s.utilization_percentage}%` }}></div>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem', textAlign: 'right' }}>
              {s.utilization_percentage.toFixed(0)}% Utilized
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

function App() {
  const { factory, workers, workstations, loading, error, refetch } = useMetrics();
  const [selectedWorker, setSelectedWorker] = useState('');
  const [selectedStation, setSelectedStation] = useState('');
  const [seedLoading, setSeedLoading] = useState(false);

  const handleRefresh = async () => {
    setSeedLoading(true);
    await seedData();
    await refetch();
    setSeedLoading(false);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div className="badge info" style={{ fontSize: '1rem', padding: '1rem 2rem' }}>Loading Dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div className="glass-panel" style={{ textAlign: 'center' }}>
          <h2 style={{ color: 'var(--danger-accent)' }}>Connection Error</h2>
          <p>{error}</p>
          <button onClick={refetch} style={{ marginTop: '1rem' }}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <Header onRefresh={handleRefresh} />

      {factory && <FactorySummary metrics={factory} />}

      <div className="glass-panel animate-fade-in stagger-2" style={{ marginBottom: '2rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <span style={{ fontWeight: 500 }}>Filters:</span>
        <select value={selectedWorker} onChange={e => setSelectedWorker(e.target.value)}>
          <option value="">All Workers</option>
          {workers.map(w => <option key={w.worker_id} value={w.worker_id}>{w.name}</option>)}
        </select>
        <select value={selectedStation} onChange={e => setSelectedStation(e.target.value)}>
          <option value="">All Workstations</option>
          {workstations.map(s => <option key={s.workstation_id} value={s.workstation_id}>{s.name}</option>)}
        </select>
      </div>

      <div style={{ display: 'grid', gap: '2rem' }}>
        <WorkerList workers={workers} filterId={selectedWorker} />
        <WorkstationList stations={workstations} filterId={selectedStation} />
      </div>
    </div>
  );
}

export default App;
