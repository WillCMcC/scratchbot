const { Queue, Worker, QueueEvents } = require('bullmq');
const { RedisServer } = require('@redis/server');

(async () => {
  // Start an embedded Redis server
  const server = new RedisServer();
  await server.open();
  const connection = { host: '127.0.0.1', port: server.opts.port };

  const queueName = 'demo';
  const queue = new Queue(queueName, { connection });
  const events = new QueueEvents(queueName, { connection });

  events.on('waiting', ({ jobId }) => console.log(`pending ${jobId}`));
  events.on('active', ({ jobId }) => console.log(`running ${jobId}`));
  events.on('completed', ({ jobId }) => {
    console.log(`done ${jobId}`);
    server.close();
    process.exit(0);
  });

  new Worker(queueName, async job => {
    // Simulate work
    return { ok: true };
  }, { connection });

  await queue.add('test', { hello: 'world' });
})();
