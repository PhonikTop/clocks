import { ref, onUnmounted } from "vue";

export function useRoomWebSocket(url) {
  const isConnected = ref(false);
  const error = ref(null);
  const messageHandlers = ref({});

  let socket = null;

  const connect = () => {
    socket = new WebSocket(url);

    socket.onopen = () => {
      isConnected.value = true;
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        if (message.type && messageHandlers.value[message.type]) {
          messageHandlers.value[message.type](message);
        }
      } catch (e) {
        console.error("Error parsing message:", e);
      }
    };

    socket.onerror = (event) => {
      error.value = event;
      reconnect();
    };

    socket.onclose = () => {
      isConnected.value = false;
      reconnect();
    };
  };

  const reconnect = () => {
    setTimeout(connect, 3000);
  };

  const sendMessage = (message) => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  };

  const addMessageHandler = (type, handler) => {
    messageHandlers.value[type] = handler;
  };

  const removeMessageHandler = (type) => {
    delete messageHandlers.value[type];
  };

  const disconnect = () => {
    if (socket) {
      socket.close();
      socket = null;
    }
  };

  onUnmounted(() => {
    disconnect();
  });

  return {
    isConnected,
    error,
    connect,
    disconnect,
    sendMessage,
    addMessageHandler,
    removeMessageHandler,
  };
}
