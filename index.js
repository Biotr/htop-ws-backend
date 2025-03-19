const socket = new WebSocket('ws://localhost:8765')
let initialContent,tempProcesses
let activeProces = 0
const tableHeader = ["PID","USER","PRI","NI","VIRT","RES","SHR","S","CPU%","MEM%","TIME+","Command"]
const convertUnit = (value,n=0,i=5,prefix='') =>{
    let units = ['',prefix,'M','G']
    value = parseFloat(value)
    if((Math.ceil(value).toString()+units[n]).length>i){
        return convertUnit(value/Math.pow(2,10),n+1,i,prefix)
    }
    else{
        let rounding = units[n] == 'G' ? 10 : 1 
        rounding = units.includes('K') ? 100 : rounding
        return (Math.floor(value*rounding)/rounding)+units[n]
    }   
}

const convertTime=(value)=>{
    let hours = Math.floor(value/60)
    let minutes = (value - hours * 60).toFixed(2)
    let minutesSplitted = minutes.toString().split('.')
    return `${hours}:${minutesSplitted[0].padStart(2,'0')}.${minutesSplitted[1].padStart(2,'0')}`
}

const refreshProcesses = ()=>{

        const table = document.getElementById('table')
        table.innerHTML= `<tr>${tableHeader.map((cell)=>`<th>${cell}</th>`).join('')}</tr>`
        tempProcesses.forEach((proces)=>{
            table.innerHTML=table.innerHTML+`<tr onclick="handleMouseClick(${proces[12]})" class=${activeProces==proces[12]?"active":''}>
            <td>${proces[0].toString().padStart(7,' ')}</td>
            <td>${proces[1]}</td>
            <td>${proces[2]}</td>
            <td>${proces[3]}</td>
            <td>${convertUnit(proces[4])}</td>
            <td>${convertUnit(proces[5])}</td>
            <td>${convertUnit(proces[6])}</td>
            <td>${proces[7]}</td>
            <td>${proces[8].toFixed(1)}</td>
            <td>${proces[9].toFixed(1)}</td>
            <td>${convertTime(proces[10])}</td>
            <td>${proces[11]}</td></tr>`
        })


    }
const handleMouseClick = (index)=>{
    activeProces = index
    refreshProcesses()
}
const handleInitializePage = (coresLength) => {
    const coresContainer = document.getElementById('cores-container')
    const coreDivs = []
    for (let i = 0;i<coresLength;i++){
        let coreContainer = document.createElement('div')
        coreDivs.push(coreContainer)
        coresContainer.appendChild(coreContainer)
        coreContainer.classList.add('cell')
    }

    const totalMem = document.getElementById('total-memory')  
    const swpMem = document.getElementById('swp-memory')
    const info = document.getElementById('info')
    return [coreDivs,totalMem,swpMem,info]
}

const handleRefreshBars = (data,suffix,prefix,toFill) => {
    let filledWithBars, word
    if(prefix==='%'){
        filledWithBars = Math.ceil((parseFloat(data)*toFill)/100)
        word = data + prefix
    }
    else{
        filledWithBars = Math.ceil((data*toFill)/prefix)
        word = convertUnit(data,1,3,'K')+'/'+convertUnit(prefix,1,3,'K')
    }
    let filledWithSpaces = toFill-filledWithBars
    let loadingBar = `${suffix.padStart(3,' ')}[${'|'.repeat(filledWithBars)}${' '.repeat(filledWithSpaces)}]`
    let barSplitted = loadingBar.split('')

    for(let i = barSplitted.length - word.length; i<barSplitted.length; i++){
        barSplitted[i-1]=word[i+word.length-barSplitted.length]
    }
    return barSplitted.join('')
    
}

const handleMoreInfo = (processes,loadAvg,uptime)=>{
    const numberOfTasks = processes.length
    const runningProcesses = []
    uptime = Math.ceil(uptime)
    let days = Math.floor(uptime/60/60/24)
    days = days?`${days} days,`: ''
    let hours = Math.floor(uptime/60/60%24)
    hours = hours.toString().padStart(2,'0')
    let minutes = Math.floor(uptime/60%60)
    minutes = minutes.toString().padStart(2,'0')
    let seconds = uptime%60
    seconds = seconds.toString().padStart(2,'0')
    processes.forEach(proces=>proces.includes('R')&&runningProcesses.push(proces))
    return `<div class="cell">Tasks: ${numberOfTasks}, Unknown thr; ${runningProcesses.length} running</div>
        <div class="cell">Load average: ${loadAvg.join(', ')}</div>
        <div class="cell">Uptime:${days} ${hours}:${minutes}:${seconds}</div>`
}
const handleKillProces = () =>{
    socket.send(tempProcesses[activeProces][0])
}

document.body.addEventListener('keyup',(event)=>{
    const key = event.key
    switch(key){
        case 'ArrowDown': 
            activeProces+=1
            break;
        case 'ArrowUp':
            if(activeProces!==0){
                activeProces-=1
            }
            break;
        case 'Enter':
            handleKillProces(activeProces)
    }
    refreshProcesses()
    
})

socket.addEventListener("close", event=>{
    console.log("Socket CLOSED")
})


socket.addEventListener('message', (event)=>{
    const {cpu, memory, processes,loadavg,uptime} = JSON.parse(event.data)
    initialContent ??= handleInitializePage(cpu.length)
    let [coresIdBox, totalMemory,swpMemory,info] = initialContent 
    let chars,width
    cpu.forEach((core,index) => {
        width = coresIdBox[index].offsetWidth
        chars = Math.floor(width/7)-9 
        coresIdBox[index].innerHTML = handleRefreshBars(core,index.toString(),'%',chars)
    });
    width = totalMemory.offsetWidth
    chars = Math.floor(width/7)-14
    totalMemory.innerHTML = handleRefreshBars(memory[1],'Mem',memory[0],chars)
    swpMemory.innerHTML = handleRefreshBars(memory[3],'Swp',memory[2],chars)
    
    info.innerHTML = handleMoreInfo(processes,loadavg,uptime)
    tempProcesses = processes.map((proces,index)=>[...proces,index])

    refreshProcesses()
})