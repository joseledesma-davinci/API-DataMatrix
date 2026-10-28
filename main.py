import io
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pylibdmtx.pylibdmtx import encode
from PIL import Image

app = FastAPI(title="DataMatrix API")


def generar_datamatrix(data: str, scale: int = 5, border: int = 2) -> bytes:
    encoded = encode(data.encode("utf-8"))
    img = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)

    # Escalar y agregar zona de silencio (quiet zone)
    img = img.resize((img.width * scale // 5 or 1, img.height * scale // 5 or 1), Image.NEAREST)
    canvas = Image.new("RGB", (img.width + border * 2 * scale, img.height + border * 2 * scale), "white")
    canvas.paste(img, (border * scale, border * scale))

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
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