const fastify = require('fastify');
const crypto = require('crypto');

const app = fastify();

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

app.post('/webhooks/github', (req, reply) => {
  const signature = req.headers['x-hub-signature-256'];
  const payload = req.body;
  if (!verifySignature(signature, payload)) {
    reply.code(401).send({ error: 'Invalid signature' });
    return;
  }
  reply.send({ ok: true });
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
