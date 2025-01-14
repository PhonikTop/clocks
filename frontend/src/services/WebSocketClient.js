class WebSocketClient {
  constructor (url) {
    this.url = url
    this.socket = null
    this.isConnected = false
    this.reconnectInterval = 5000
    this.messageHandlers = []
    this.shouldReconnect = true
  }

  connect () {
    return new Promise((resolve, reject) => {
      if (this.isConnected) {
        return resolve()
      }

      this.socket = new WebSocket(this.url)

      this.socket.onopen = () => {
        console.log('WebSocket успешно подключен.')
        this.isConnected = true
        resolve()
      }

      this.socket.onerror = (error) => {
        console.error('Ошибка подключения:', error)
        reject(error)
      }

      this.socket.onclose = (event) => {
        console.log(`Соединение закрыто: ${event.reason || 'без причины'}`)
        this.isConnected = false
        if (this.shouldReconnect) {
          console.log('Попытка переподключения через', this.reconnectInterval, 'мс')
          setTimeout(() => this.connect().catch(console.error), this.reconnectInterval)
        }
      }

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.messageHandlers.forEach((handler) => handler(data))
        } catch (error) {
          console.error('Ошибка обработки сообщения:', error)
        }
      }
    })
  }

  send (message) {
    if (!this.isConnected || !this.socket) {
      console.error('Нет соединения с WebSocket.')
      return
    }

    try {
      this.socket.send(JSON.stringify(message))
    } catch (error) {
      console.error('Ошибка при отправке сообщения:', error)
    }
  }

  onMessage (callback) {
    if (typeof callback === 'function') {
      this.messageHandlers.push(callback)
    } else {
      console.error('Переданный обработчик не является функцией.')
    }
  }

  disconnect () {
    this.shouldReconnect = false
    if (this.socket) {
      this.socket.close()
    }
    this.isConnected = false
  }
}

export default WebSocketClient
