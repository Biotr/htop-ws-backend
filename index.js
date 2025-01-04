const socket = new WebSocket("ws://localhost:8765")


socket.addEventListener("message", (event)=>{
    const data = JSON.parse(event.data)
    const test = document.getElementById('test')
    test.innerHTML = data.cpu[1]
})