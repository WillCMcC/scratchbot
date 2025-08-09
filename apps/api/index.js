const fastify = require('fastify');
const crypto = require('crypto');
const { Queue } = require('bullmq');

const app = fastify();

// Connect to the Redis instance specified by the REDIS_URL environment variable.
const connectionUrl = process.env.REDIS_URL || 'redis://localhost:6379';
const queueName = 'scratchbot-jobs';
const queue = new Queue(queueName, { connection: connectionUrl });

console.log(`API service connected to Redis at ${connectionUrl} and queue "${queueName}"`);


app.addContentTypeParser('*', { parseAs: 'buffer' }, function (req, body, done) {
  done(null, body);
});

function verifySignature(signature, payload) {
  const secret = process.env.GITHUB_WEBHOOK_SECRET || '';
  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');
  return (
    signature &&
    crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(digest))
  );
}

app.post('/webhooks/github', async (req, reply) => {
  const signature = req.headers['x-hub-signature-256'];
  const payload = req.body;
  if (!verifySignature(signature, payload)) {
    reply.code(401).send({ error: 'Invalid signature' });
    return;
  }

  // Enqueue a job for the worker to process.
  const eventName = req.headers['x-github-event'];
  const data = JSON.parse(payload.toString());
  const job = await queue.add(eventName, data);

  console.log(`Enqueued job ${job.id} for event "${eventName}"`);

  // Acknowledge the webhook and include the job ID.
  reply.send({ ok: true, jobId: job.id });
});

if (require.main === module) {
  const port = process.env.PORT || 3000;
  app.listen({ port, host: '0.0.0.0' }, (err, address) => {
    if (err) {
      app.log.error(err);
      process.exit(1);
    }
    app.log.info(`Server listening at ${address}`);
  });
}

module.exports = app;
