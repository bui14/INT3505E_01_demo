const winston = require('winston');

const logger = winston.createLogger({
  level: 'info', // 1. Chỉ ghi từ mức Info trở lên
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json() // 2. Quan trọng: Format log thành JSON
  ),
  transports: [
    new winston.transports.Console(), // Hiện ra terminal
    new winston.transports.File({ filename: 'app.log' }) // 3. Lưu vĩnh viễn vào file
  ],
});