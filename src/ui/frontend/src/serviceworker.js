export async function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    try {
      await navigator.serviceWorker.register('/sw.js');
    } catch (e) {
      console.log(e);
    }
    return true;
  } else {
    return false;
  }
}

export async function sendMessage(data) {
  return new Promise(resolve => {
    const channel = new MessageChannel();
    channel.port1.onmessage = (data) => {
      resolve(data);
    }
    navigator.serviceWorker.controller.postMessage(
      data, [channel.port2]
    );
  });
}
