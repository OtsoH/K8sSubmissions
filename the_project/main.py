import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "todo app"}


def main():
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
