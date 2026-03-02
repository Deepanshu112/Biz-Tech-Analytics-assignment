import { useState, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const useMetrics = () => {
  const [factory, setFactory] = useState(null);
  const [workers, setWorkers] = useState([]);
  const [workstations, setWorkstations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      const [factoryRes, workersRes, workstationsRes] = await Promise.all([
        fetch(`${API_BASE}/metrics/factory`),
        fetch(`${API_BASE}/metrics/workers`),
        fetch(`${API_BASE}/metrics/workstations`)
      ]);

      if (!factoryRes.ok || !workersRes.ok || !workstationsRes.ok) {
        throw new Error('Failed to fetch metrics data');
      }

      setFactory(await factoryRes.json());
      setWorkers(await workersRes.json());
      setWorkstations(await workstationsRes.json());
      setError(null);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 5000);
    return () => clearInterval(intervalId);
  }, []);

  return { factory, workers, workstations, loading, error, refetch: fetchData };
};

export const seedData = async () => {
  const res = await fetch(`${API_BASE}/seed`, { method: 'POST' });
  return await res.json();
};
