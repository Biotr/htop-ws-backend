# htop-ws-backend

htop-ws-backend is backend application that allows to power web-based monitor interface similar to htop.
- `collectors` collects data such as cores usage, memory usage, running processes from your Linux system.
- `core` there we have `engine` that pull data from collectors and object state with latest data asynchronously every 1 sec.
- `api` websocket server that stream the data and listen on specified port
 
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
3. Setup environment variables, example:
```
WEBSOCKET_HOST='0.0.0.0'
WEBSOCKET_PORT='8765'
WEBSOCKET_CERT_PATH='./certificates/cert.pem'
WEBSOCKET_KEY_PATH='./certificates/key.pem'
ENGINE_INTERVAL="1.0"
```
3. To make connection with SSL you have to create certificates.  
You can do by running `setup.sh` or create certificates by your own in `./certifications` directory.
```
./setup.sh
```
4. If everything worked correctly, you can run:
```
python main.py
```
5. Because with `setup.sh` we created self-signed certificates, you have to go to `https://{server-public-ip}:{WEBSOCKET_PORT}` > Advanced > "Proceed".
6. Now we you can go to https://biotr.github.io/htop-web, enter your server public ip and fell free to monitor your system.

OPTIONAL
On [HTOP](https://biotr.github.io/htop-web/) site leave blank input and click OK. 
Leaving blank input allows you to get first look of how it works with mocked data.

### Known issues and todos
There are still some issues that i will work at such as:
- for `actions `add other options of orginal htop like sorting processes, get threads...
- method `get_memory_info` collects data using `subprocess.run` its not optimal approach
- add `.env` file, add `config.py` file, contenerize application
- add unit tests and create Jenkins pipeline




