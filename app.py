import os
import uvicorn
import asyncio
from typing import Annotated
from fastapi import BackgroundTasks, FastAPI, UploadFile, File, Response, status


FILES = "./files"
os.makedirs(FILES, exist_ok=True)

app = FastAPI()
files_progresses = {}


async def file_analyze(filename: str, file_content: Annotated[bytes, File()]):
    file_len = len(file_content)
    chunk_len = file_len // 10
    process = 0

    with open(f"{FILES}/{filename}", "ab") as file:
        for i in range(0, file_len, chunk_len):
            chunk = file_content[i : i + chunk_len]
            file.write(chunk.lower())
            process += len(chunk)
            progress = (process / file_len) * 100
            files_progresses.update({filename: progress})
            await asyncio.sleep(5)


@app.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File()):
    background_tasks.add_task(
        file_analyze, filename=file.filename, file_content=file.file.read()
    )
    return f"File {file.filename} is uploading"


@app.get("/get_progress", status_code=status.HTTP_302_FOUND)
def get_progress(filename: str):
    progress = files_progresses.get(filename)
    if progress:
        return f"Progress:{progress},File: {filename}"
    else:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND, content=f"No file named {filename}"
        )


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
