class Room {
  constructor (conn, participants) {
    this.conn = conn
    this.participants = participants

    this.initWebSocket()
  }

  initWebSocket () {
    this.conn.onMessage((data) => {
      this.handleMessage(data)
    })
  }

  handleMessage (data) {
    switch (data.type) {
      case 'user_joined':
        this.addUser(data)
        break
      case 'leave_room':
        this.deleteUser(data)
        break
      case 'make_guess':
        this.userGuess(data)
        break
      case 'last_mark':
        this.lastGuess(data)
        break
      case 'refresh':
        this.refresh()
        break
      default:
        console.error('Неизвестный тип сообщения:', data.type)
    }
  }

  addUser (data) {
    const { user_uuid: uuid, nickname, role } = data
    this.participants[uuid] = { nickname, role }
    console.log('Пользователь добавлен:', this.participants[uuid])
  }

  deleteUser (data) {
    const { user_uuid: uuid } = data
    delete this.participants[uuid]
    console.log('Пользователь удален:', uuid)
  }
}

export default Room
