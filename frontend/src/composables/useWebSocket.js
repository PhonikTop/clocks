import { ref, onUnmounted } from "vue";

export function useRoomWebSocket(url) {
  const isConnected = ref(false);
  const error = ref(null);
  const messageHandlers = ref({});

  const reconnectAttempts = ref(0);
  const maxReconnectAttempts = 5;
  const reconnectFailed = ref(false);

  let socket = null;
  let reconnectTimer = null;
  let isActive = true;

  const connect = () => {
    reconnectFailed.value = false;

    if (socket) disconnect();

    socket = new WebSocket(url);

    socket.onopen = () => {
      isConnected.value = true;
      reconnectAttempts.value = 0;
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
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    if (!isActive) return;
    if (reconnectAttempts.value >= maxReconnectAttempts) {
      reconnectFailed.value = true;
      error.value = new Error(
        `Max reconnect attempts reached (${maxReconnectAttempts})`
      );
      return;
    }

    reconnectAttempts.value++;
    reconnectTimer = setTimeout(
      connect,
      3000 * Math.pow(2, reconnectAttempts.value - 1)
    );
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
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };

  const resetReconnectLimit = () => {
    reconnectAttempts.value = 0;
    reconnectFailed.value = false;
  };

  onUnmounted(() => {
    isActive = false;
    disconnect();
  });

  return {
    isConnected,
    error,
    reconnectAttempts,
    maxReconnectAttempts,
    reconnectFailed,
    connect,
    disconnect,
    sendMessage,
    addMessageHandler,
    removeMessageHandler,
    resetReconnectLimit,
  };
}
