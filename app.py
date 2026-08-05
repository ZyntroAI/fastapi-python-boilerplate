from fastapi import FastAPI
 
app = FastAPI()
 
@app.get("/")
def home():
    return {"message": "Hello from Python on Vercel"}
 
@app.get("/api/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
