import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { apiRouter } from './routes/api';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

// Routes
app.use('/api', apiRouter);

// Basic health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Local Test Generator Server is running.' });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
