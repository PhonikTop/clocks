import { ref, Ref, onUnmounted } from "vue";

export type MessageHandler = (message: any) => void;

export function useRoomWebSocket(url: string) {
  const isConnected: Ref<boolean> = ref(false);
  const error: Ref<Event | Error | null> = ref(null);
  const messageHandlers: Ref<Record<string, MessageHandler>> = ref({});

  const reconnectAttempts: Ref<number> = ref(0);
  const maxReconnectAttempts = 5;
  const reconnectFailed: Ref<boolean> = ref(false);

  let socket: WebSocket | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let isActive = true;

  const connect = (): void => {
    reconnectFailed.value = false;

    if (socket) disconnect();

    socket = new WebSocket(url);

    socket.onopen = () => {
      isConnected.value = true;
      reconnectAttempts.value = 0;
    };

    socket.onmessage = (event: MessageEvent) => {
      try {
        const message = JSON.parse(event.data);

        if (message.type && messageHandlers.value[message.type]) {
          messageHandlers.value[message.type](message);
        }
      } catch (e) {
        console.error("Error parsing message:", e);
      }
    };

    socket.onerror = (event: Event) => {
      error.value = event;
      reconnect();
    };

    socket.onclose = () => {
      isConnected.value = false;
      reconnect();
    };
  };

  const reconnect = (): void => {
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

  const sendMessage = (message: any): void => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  };

  const addMessageHandler = (type: string, handler: MessageHandler): void => {
    messageHandlers.value[type] = handler;
  };

  const removeMessageHandler = (type: string): void => {
    delete messageHandlers.value[type];
  };

  const disconnect = (): void => {
    if (socket) {
      socket.close();
      socket = null;
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };

  const resetReconnectLimit = (): void => {
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
