# Flask proxy for python file
app - project folder;
server.py - main running file

## Versions
Requires: Python >=3.5

## Install packages
```console
pip install -r requirements.txt  --no-cache-dir
```

## Run
```console
python server.py
```

## Echo test
```console
curl http://localhost:5000/echo/test123
```

## Data request
```console
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{\
	"input" : "Some input text",\
	"token" : ""
	}' http://localhost:5000/api/v1/input
```
Answer: script output example
{
	"output": "oewiruwr ioeiwr "
	"token": "fHBQCHs"
}


## Clear cache
```console
curl http://localhost:5000/clear/fHBQCHs
```
Example for token fHBQCHs

Answer: 'Cleared'