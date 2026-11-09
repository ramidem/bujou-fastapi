```shel
source .venv/bin/activate

fastapi dev main.py
```


curl
```shell
# get all
curl http://127.0.0.1:8000/

# get one

# create one
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"name": "bananas"}' \
  http://127.0.0.1:8000

# update one
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"name": "bananas"}' \
  http://127.0.0.1:8000

```