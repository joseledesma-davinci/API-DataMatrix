import io
import treepoem
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from PIL import Image

app = FastAPI(title="DataMatrix API")


def generar_datamatrix(data: str, scale: int = 5) -> bytes:
    img = treepoem.generate_barcode(
        barcode_type="datamatrix",
        data=data,
    )
    img = img.convert("RGB")

    # Escalar si se pide
    if scale != 5:
        w, h = img.size
        img = img.resize((w * scale // 5, h * scale // 5), Image.NEAREST)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


class DMRequest(BaseModel):
    data: str
    scale: int = 5


@app.get("/datamatrix")
def get_datamatrix(data: str = Query(..., max_length=2000), scale: int = Query(5, ge=1, le=20)):
    try:
        png = generar_datamatrix(data, scale)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return StreamingResponse(io.BytesIO(png), media_type="image/png")


@app.post("/datamatrix")
def post_datamatrix(req: DMRequest):
    try:
        png = generar_datamatrix(req.data, req.scale)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return StreamingResponse(io.BytesIO(png), media_type="image/png")