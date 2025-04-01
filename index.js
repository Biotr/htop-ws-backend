const localIp = window.location.hostname
const socket = new WebSocket(`ws://${localIp}:8765`)
let initialContent, tempProcesses
let activeProces = 0

const convertUnit = (value, n = 0, i = 5, prefix = "") => {
    let units = ["", prefix, "M", "G"]
    value = parseFloat(value)
    if ((Math.ceil(value).toString() + units[n]).length > i) {
        return convertUnit(value / Math.pow(2, 10), n + 1, i, prefix)
    } else {
        let rounding = units[n] == "G" ? 10 : 1
        rounding = units.includes("K") ? 100 : rounding
        return Math.floor(value * rounding) / rounding + units[n]
    }
}

const convertTime = (uptime, secondsType) => {
    uptime = Math.ceil(uptime)

    let hours = Math.floor((uptime / 60 / 60) % 24)
    hours = hours.toString().padStart(2, "0")
    let minutes = Math.floor((uptime / 60) % 60)
    minutes = minutes.toString().padStart(2, "0")
    let seconds = uptime % secondsType
    seconds = seconds.toString().padStart(2, "0")

    return ` ${hours}:${minutes}:${seconds}`
}
const refreshProcesses = () => {
    const table = document.getElementById("table")
    table.innerHTML = ""
    tempProcesses.forEach(proces => {
        const row = document.createElement("tr")
        table.appendChild(row)
        row.addEventListener("click", () => {
            handleMouseClick(proces["id"])
        })
        row.classList.add(activeProces === proces["id"] && "active")
        row.innerHTML = `<td>${proces["pid"].toString().padStart(7, " ")}</td>
                    <td>${proces["owner"]}</td>
                    <td>${proces["pri"]}</td>
                    <td>${proces["ni"]}</td>
                    <td>${convertUnit(proces["virt"])}</td> 
                    <td>${convertUnit(proces["res"])}</td> 
                    <td>${convertUnit(proces["shr"])}</td> 
                    <td>${proces["status"]}</td>
                    <td>${proces["pid_cpu_usage"].toFixed(1)}</td>
                    <td>${proces["mem_usage"].toFixed(1)}</td>
                    <td>${convertTime(proces["time_plus"] * 60, 60)}</td>
                    <td>${proces["command"]}</td>`
    })
}

const handleMouseClick = index => {
    activeProces = index
    refreshProcesses()
}
const handleInitializePage = coresLength => {
    const coresContainer = document.getElementById("cores-container")
    const coreDivs = []
    for (let i = 0; i < coresLength; i++) {
        let coreContainer = document.createElement("div")
        coreDivs.push(coreContainer)
        coresContainer.appendChild(coreContainer)
        coreContainer.classList.add("cell")
    }

    const totalMem = document.getElementById("total-memory")
    const swpMem = document.getElementById("swp-memory")
    const info = document.getElementById("info")
    return [coreDivs, totalMem, swpMem, info]
}

const handleRefreshBars = (data, suffix, prefix, toFill) => {
    let filledWithBars, word
    if (prefix === "%") {
        filledWithBars = Math.ceil((parseFloat(data) * toFill) / 100)
        word = data + prefix
    } else {
        filledWithBars = Math.ceil((data * toFill) / prefix)
        word =
            convertUnit(data, 1, 3, "K") + "/" + convertUnit(prefix, 1, 3, "K")
    }
    const filledWithSpaces = toFill - filledWithBars
    loadingBar = `${suffix.padStart(3, " ")}[${"|".repeat(
        filledWithBars
    )}${" ".repeat(filledWithSpaces)}]`
    let barSplitted = loadingBar.split("")
    const maxNumberToFill = barSplitted.length - word.length
    for (let i = maxNumberToFill; i < barSplitted.length; i++) {
        barSplitted[i - 1] = word[i + word.length - barSplitted.length]
    }
    return barSplitted.join("")
}

const handleMoreInfo = (processes, loadAvg, uptime) => {
    const numberOfTasks = processes.length
    const runningProcesses = []
    processes.forEach(
        proces => proces.status === "R" && runningProcesses.push(proces)
    )
    const systemRunningTime = convertTime(uptime, 60)
    const averageLoad = loadAvg.join(", ")
    const numberOfRunningTasks = runningProcesses.length
    return `<div class="cell">Tasks: ${numberOfTasks}, Unknown thr; ${numberOfRunningTasks} running</div>
            <div class="cell">Load average: ${averageLoad}</div>
            <div class="cell">Uptime:${systemRunningTime}</div>`
}
const handleKillProces = () => {
    socket.send(tempProcesses[activeProces]["pid"])
}

document.body.addEventListener("keyup", event => {
    const key = event.key
    switch (key) {
        case "ArrowDown":
            activeProces += 1
            break
        case "ArrowUp":
            if (activeProces !== 0) {
                activeProces -= 1
            }
            break
        case "Enter":
            handleKillProces(activeProces)
    }
    refreshProcesses()
})

socket.addEventListener("close", () => {
    console.log("Socket CLOSED")
})

socket.addEventListener("message", event => {
    console.log("cos")
    const {
        memory_info: memoryInfo,
        cores_usage: coresUsage,
        processes,
        load_average: loadAvg,
        uptime,
    } = JSON.parse(event.data)
    const {
        total_mem: totalMemory,
        used_mem: usedMemory,
        swap_mem: totalSwpMemory,
        swap_used: usedSwpMemory,
    } = memoryInfo

    const coresUsageValues = Object.values(coresUsage).slice(1)
    initialContent ??= handleInitializePage(coresUsageValues.length)
    let [coresIdBox, totalMemoryBox, swpMemoryBox, info] = initialContent
    let chars, width
    coresUsageValues.forEach((core, index) => {
        width = coresIdBox[index].offsetWidth
        chars = Math.floor(width / 7) - 13
        coresIdBox[index].innerHTML = handleRefreshBars(
            core,
            index.toString(),
            "%",
            chars
        )
    })
    width = totalMemoryBox.offsetWidth
    chars = Math.floor(width / 7) - 14

    totalMemoryBox.innerHTML = handleRefreshBars(
        usedMemory,
        "Mem",
        totalMemory,
        chars
    )

    swpMemoryBox.innerHTML = handleRefreshBars(
        usedSwpMemory,
        "Swp",
        totalSwpMemory,
        chars
    )

    info.innerHTML = handleMoreInfo(processes, loadAvg, uptime)
    processes.forEach((proces, index) => (proces["id"] = index))
    tempProcesses = processes

    refreshProcesses()
})
