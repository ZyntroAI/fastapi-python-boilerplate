import { Registry, Counter, Gauge, Histogram } from 'prom-client';

const registry = new Registry();

export const batchJobTotal = new Counter({
  name: 'zyntroai_batch_job_total',
  help: 'Total batch jobs processed',
  registers: [registry],
  labelNames: ['status']
});

export const batchJobFailed = new Counter({
  name: 'zyntroai_batch_job_failed_total',
  help: 'Total failed batch jobs',
  registers: [registry]
});

export const queueDepth = new Gauge({
  name: 'zyntroai_queue_depth',
  help: 'Current batch queue depth',
  registers: [registry],
  labelNames: ['queue']
});

export const httpDuration = new Histogram({
  name: 'zyntroai_http_request_duration_seconds',
  help: 'HTTP request duration',
  buckets: [0.1, 0.5, 1, 5, 10, 30, 60],
  registers: [registry]
});

export { registry };
