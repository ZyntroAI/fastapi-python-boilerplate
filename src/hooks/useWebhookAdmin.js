import { useState, useCallback, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_WEBHOOK_API_URL || '';
const ADMIN_KEY = import.meta.env.VITE_ADMIN_KEY || '';

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'X-Admin-Key': ADMIN_KEY,
});

export function useWebhookAdmin() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(null);
  const [failedDeliveries, setFailedDeliveries] = useState([]);

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/maintenance-status`, {
        headers: getHeaders(),
      });
      if (!res.ok) throw new Error('Failed to fetch status');
      const data = await res.json();
      setStatus(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchFailed = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/replay-failed`, {
        headers: getHeaders(),
      });
      if (!res.ok) throw new Error('Failed to list failed deliveries');
      const data = await res.json();
      setFailedDeliveries(data.failed || []);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const replayDelivery = useCallback(async (deliveryId, service) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/replay-failed`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ deliveryId, service }),
      });
      if (!res.ok) throw new Error('Replay failed');
      await fetchFailed();
      return await res.json();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchFailed]);

  const runMaintenance = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/maintenance-run`, {
        method: 'POST',
        headers: getHeaders(),
      });
      if (!res.ok) throw new Error('Maintenance run failed');
      await fetchStatus();
      return await res.json();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchStatus]);

  const getPayload = useCallback(async (deliveryId) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/payload/${deliveryId}`, {
        headers: getHeaders(),
      });
      if (!res.ok) throw new Error('Payload not found');
      return await res.json();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    fetchFailed();
  }, [fetchStatus, fetchFailed]);

  return {
    loading,
    error,
    status,
    failedDeliveries,
    fetchStatus,
    fetchFailed,
    replayDelivery,
    runMaintenance,
    getPayload,
  };
}
