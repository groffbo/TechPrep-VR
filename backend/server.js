require('dotenv').config();
const express = require('express');
const WebSocket = require('ws');
const { GeminiClient } = require('./geminiClient');

const app = express();
const port = 3000;

app.use(express.static('../frontend'));

const server = app.listen(port, () => console.log(`Server running at http://localhost:${port}`));

const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
  console.log('Client connected');
  const gemini = new GeminiClient(process.env.GEMINI_KEY);

  ws.on('message', async (msg) => {
    // msg is Float32Array buffer
    const responseAudio = await gemini.sendAudio(msg);
    ws.send(responseAudio);
  });

  ws.on('close', () => console.log('Client disconnected'));
});
