# htop-ws-backend

htop-ws-backend is backend application that allows to power web-based monitor interface similar to htop.
- `main.py` collects data such as cores usage, memory usage, running processes from your Linux system.
- `server.py` websockets server streams collected data to connected clients.
 
Application can be used together with compatibile frontend - [htop-web](https://github.com/Biotr/htop-web).  
Repository `htop-web` has been deployed with github pages [HTOP](https://biotr.github.io/htop-web/) so you can easliy use it.

### Get started 
---
1. First of all you have to clone repository.

```
git clone https://github.com/Biotr/htop-ws-backend.git
```  
2. Now you have to initate virtual enviroment and install `requirements.txt`.
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. To make connection with SSL you have to create certificates.  
You can do by running `setup.sh` or create certificates by your own in `./certifications` directory.
```
./setup.sh
```
4. If everything worked correctly, you can run websocket server.
```
python server.py
```
5. Because with `setup.sh` we created self-signed certificates, you have to go to `https://{server-public-ip}:8765` > Advanced > "Proceed".
6. Now we you can go to https://biotr.github.io/htop-web, enter your server public ip and fell free to monitor your system.

OPTIONAL
On [HTOP](https://biotr.github.io/htop-web/) site leave blank input and click OK. 
Leaving blank input allows you to get first look of how it works with mocked data.

### Known issues
There are still some issues that i will work at such as:
- add other options of orginal htop like sorting processes, get threads...
- in `main.py` memory is getting with `subprocess.run()` so it creates proces (imo its not good). 





