from fastapi import FastAPI, UploadFile
import pandas as pd
from analyzer import predict
from predictor import predict


app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend working"}

@app.post("/analyze")
async def analyze(file: UploadFile):

    try:
        # Save uploaded file
        contents = await file.read()
        with open("temp.csv", "wb") as f:
            f.write(contents)

        # Read CSV
        data = pd.read_csv("temp.csv")

        # 🔥 Run model
        result = predict(data)

        # 🔥 Extract processed dataframe
        df = pd.DataFrame(result["data"])

        # 🔥 Compute stats from result
        total = result["total_records"]
        attacks = result["attacks"]
        normal = result["normal"]

        return {
            "total_records": total,
            "attacks": attacks,
            "normal": normal,
            "data": result["data"]
        }

    except Exception as e:
        return {"error": str(e)}