const client = require('prom-client');

// 1. Tự động thu thập CPU, RAM, Event Loop
client.collectDefaultMetrics();

// 2. Định nghĩa metric tùy chỉnh: Đếm số lượng request
const httpRequestCounter = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'status_code'] // Phân loại theo GET/POST, 200/500
});

// Cách dùng trong code xử lý: httpRequestCounter.inc();