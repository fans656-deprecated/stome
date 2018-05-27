export default function watch(func, options) {
  options = options || {};
  const interval = options.interval || 500;
  const id = setInterval(async () => {
    const stop = await func();
    if (stop) {
      clearInterval(id);
    }
  }, interval);
}
