# Fast API

### Run the app
* `uvicorn main:app --reload`
* `uvicorn clinic_ms.main:app --reload` (if you are in the root directory)

### Open Interactive docs:
`http://127.0.0.1:8000/docs`

### Create:
`curl -X POST "http://127.0.0.1:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":1200.5,"description":"Gaming laptop"}'
`

### Read all:
`curl "http://127.0.0.1:8000/items/"`
### Read one:
`curl "http://127.0.0.1:8000/items/1"`
### Update:
`curl -X PUT "http://127.0.0.1:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{"price":1100.0, "available": false}'
`
### Delete:
`curl -X DELETE "http://127.0.0.1:8000/items/1"`

