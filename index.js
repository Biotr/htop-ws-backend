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
        console.log(tempProcesses)
        tempProcesses.forEach((proces)=>{
            table.innerHTML=table.innerHTML+`<tr onclick="handleMouseClick(${0})" class=${activeProces==proces[12]?"active":''}>
            <td>${proces["pid"].toString().padStart(7,' ')}</td>
            <td>${proces["owner"]}</td>
            <td>${proces["pri"]}</td>
            <td>${proces["ni"]}</td>
            <td>${proces["virt"]}</td> 
            <td>${proces["res"]}</td> 
            <td>${proces["shr"]}</td> 
            <td>${proces["status"]}</td>
            <td>${proces["pid_cpu_usage"].toFixed(1)}</td>
            <td>${proces["mem_usage"].toFixed(1)}</td>
            <td>${convertTime(proces["time_plus"])}</td>
            <td>${proces["command"]}</td></tr>`
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
        console.log(word)
    }
    let filledWithSpaces = toFill-filledWithBars
    console.log(data, suffix,prefix,toFill)
    console.log(filledWithBars,filledWithSpaces)
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
    
    processes.forEach(proces=>proces.status==='R'&&runningProcesses.push(proces))
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
    const {memory_info:memoryInfo, cores_usage:coresUsage, processes,load_average:loadAvg,uptime} = JSON.parse(event.data)
    const {total_mem:totalMemory,used_mem:usedMemory,swap_mem:totalSwpMemory,swap_used:usedSwpMemory} = memoryInfo
    const coresUsageValues = Object.values(coresUsage)
    initialContent ??= handleInitializePage(coresUsageValues.length)
    let [coresIdBox, totalMemoryBox,swpMemoryBox,info] = initialContent 
    let chars,width
    coresUsageValues.forEach((core,index) => {
        width = coresIdBox[index].offsetWidth
        chars = Math.floor(width/7)-9 
        coresIdBox[index].innerHTML = handleRefreshBars(core,index.toString(),'%',chars)
    });
    width = totalMemoryBox.offsetWidth
    chars = Math.floor(width/7)-14
    console.log(memoryInfo)
    totalMemoryBox.innerHTML = handleRefreshBars(usedMemory,'Mem',totalMemory,chars)
    swpMemoryBox.innerHTML = handleRefreshBars(usedSwpMemory,'Swp',totalSwpMemory,chars)
    
    info.innerHTML = handleMoreInfo(processes,loadAvg,uptime)
    tempProcesses = processes

    refreshProcesses()
})