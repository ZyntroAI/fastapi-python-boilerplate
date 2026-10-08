import { useState } from 'react';
import { useWebhookAdmin } from '../hooks/useWebhookAdmin';

export default function WebhookDashboard() {
  const {
    loading,
    error,
    status,
    failedDeliveries,
    replayDelivery,
    runMaintenance,
    getPayload,
  } = useWebhookAdmin();

  const [selectedPayload, setSelectedPayload] = useState(null);

  const handleReplay = async (id, service) => {
    if (!confirm(`Replay ${id} to ${service}?`)) return;
    await replayDelivery(id, service);
    alert('✅ Replay initiated');
  };

  const handleShowPayload = async (id) => {
    const data = await getPayload(id);
    setSelectedPayload(data);
  };

  if (loading && !status) return <div className="p-4">⏳ Loading...</div>;
  if (error) return <div className="p-4 text-red-500">❌ {error}</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-6">🔧 Webhook Admin Dashboard</h1>

      {status && (
        <div className="bg-white rounded-lg shadow p-5 mb-6">
          <h2 className="font-semibold text-lg mb-3">System Status</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Maintenance</p>
              <p className="font-medium">{status.maintenanceEnabled ? '✅ Enabled' : '❌ Disabled'}</p>
            </div>
            <div>
              <p className="text-gray-500">Dry Run</p>
              <p className="font-medium">{status.dryRun ? '⚠️ Yes — no deletions' : '✅ No'}</p>
            </div>
            <div>
              <p className="text-gray-500">Payloads</p>
              <p className="font-medium">{status.payloadCount} ({status.payloadSizeMB} MB)</p>
            </div>
            <div>
              <p className="text-gray-500">Log Retention</p>
              <p className="font-medium">{status.logRetentionDays} days</p>
            </div>
            <div>
              <p className="text-gray-500">Payload Retention</p>
              <p className="font-medium">{status.payloadRetentionDays} days</p>
            </div>
            <div>
              <p className="text-gray-500">Next Run</p>
              <p className="font-medium text-xs">{status.nextRun}</p>
            </div>
          </div>
          <button
            onClick={runMaintenance}
            disabled={loading}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? '⏳ Running...' : '🧹 Run Maintenance Now'}
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-5 mb-6">
        <h2 className="font-semibold text-lg mb-3">
          Failed Deliveries ({failedDeliveries.length})
        </h2>
        {failedDeliveries.length === 0 ? (
          <p className="text-green-600">✅ No failed deliveries</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Delivery ID</th>
                  <th className="text-left p-2">Service</th>
                  <th className="text-left p-2">Error</th>
                  <th className="text-right p-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {failedDeliveries.map((item) => (
                  <tr key={item.deliveryId} className="border-b">
                    <td className="p-2 font-mono text-xs">{item.deliveryId}</td>
                    <td className="p-2">{item.service}</td>
                    <td className="p-2 text-red-600 max-w-xs truncate">{item.error}</td>
                    <td className="p-2 text-right space-x-2">
                      <button
                        onClick={() => handleShowPayload(item.deliveryId)}
                        className="text-blue-600 hover:underline"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleReplay(item.deliveryId, item.service)}
                        className="text-green-600 hover:underline"
                      >
                        Replay
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedPayload && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-5 max-w-2xl w-full max-h-[80vh] overflow-auto">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-semibold">Stored Payload</h3>
              <button onClick={() => setSelectedPayload(null)} className="text-gray-500">✕</button>
            </div>
            <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
              {JSON.stringify(selectedPayload, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
