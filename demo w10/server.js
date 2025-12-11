const express = require('express');
const winston = require('winston');
const client = require('prom-client');

const app = express();

// --- PHẦN 1: CẤU HÌNH WINSTON (LOGGER) ---
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json() // Format JSON
  ),
  transports: [
    new winston.transports.Console(), // Hiện ra terminal
    new winston.transports.File({ filename: 'app.log' }) // Lưu vào file
  ],
});

// --- PHẦN 2: CẤU HÌNH PROMETHEUS (METRICS) ---
const register = new client.Registry();
client.collectDefaultMetrics({ register }); // Tự đo CPU, RAM...

// Tạo một biến đếm số lượng request
const httpRequestCounter = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
});
register.registerMetric(httpRequestCounter);

// --- PHẦN 3: KẾT NỐI VÀO EXPRESS ---

// Middleware: Chặn mọi request để đếm và log
app.use((req, res, next) => {
  // 1. Ghi log khi có người gọi vào
  logger.info(`Incoming request: ${req.method} ${req.url}`);

  // 2. Đếm request cho Prometheus (lắng nghe sự kiện khi response trả về xong)
  res.on('finish', () => {
    httpRequestCounter.inc({
      method: req.method,
      route: req.path,
      status_code: res.statusCode,
    });
  });

  next();
});

// Route bình thường
app.get('/', (req, res) => {
  res.send('Hello World! Server is healthy.');
});

// Route giả lập lỗi (để test log Error)
app.get('/error', (req, res) => {
  logger.error('Database connection failed!'); // Ghi log lỗi
  res.status(500).send('Something broke!');
});

// Route để xem Metrics (Prometheus sẽ "cào" dữ liệu ở đây)
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

app.listen(3000, () => {
  console.log('Server chạy tại http://localhost:3000');
});