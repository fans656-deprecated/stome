export default async function watch(func, options) {
  const stop = await func();
  if (stop) return;

  options = options || {};
  const interval = options.interval || 500;

  scheduleCall(func, interval);
}

async function scheduleCall(func, interval) {
  setTimeout(async () => {
    const stop = await func();
    if (!stop) {
      scheduleCall(func, interval);
    }
  }, interval);
}
