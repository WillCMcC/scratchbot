const { Worker } = require('bullmq');

// The worker will connect to the Redis instance specified by the REDIS_URL
// environment variable. If this variable is not set, it will default to a
// local Redis instance, which is useful for standalone development.
const connectionUrl = process.env.REDIS_URL || 'redis://localhost:6379';

const queueName = 'scratchbot-jobs';

console.log(`Worker connecting to Redis at ${connectionUrl}...`);

// A worker's job is to listen for and process jobs from the queue.
const worker = new Worker(queueName, async job => {
  console.log(`Processing job ${job.id}`, job.data);
  // In the future, this is where the Python script would be called.
  // For now, we'll just simulate the work.
  await new Promise(resolve => setTimeout(resolve, 1000));
  console.log(`Finished job ${job.id}`);
  return { status: 'done', jobId: job.id };
}, { connection: connectionUrl });

worker.on('completed', job => {
  console.log(`${job.id} has completed!`);
});

worker.on('failed', (job, err) => {
  console.log(`${job.id} has failed with ${err.message}`);
});

console.log(`Worker listening for jobs on queue "${queueName}"`);
