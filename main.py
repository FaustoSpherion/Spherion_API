# app/main.py
# - Title - "Spherion API"
# - Goal - Spherion free
# - URL - localhost
# - Endpoint
# -     localhost or Drive GetHob/spherion (GET)
# -     localhost or Drive GetHob/spherion/id (GET)
# -     localhost or Drive GetHob/spherion/id (POST)
# -     localhost or Drive GetHob/spherion/id (DELETE)
#
from fastapi import FastAPI, Header, HTTPException
from app.models import EncodeRequest, EncodeResponse
from app.core.encoding import encode_spherion

API_KEY = "demo-key"                       # env var in prod
app = FastAPI(
    title="Spherion API",
    version="0.1",
    description="Free tier – hierarchical spherical look-ups with uncertainty."
)

def verify(key: str):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/v1/encode", response_model=EncodeResponse)
def encode(req: EncodeRequest, authorization: str = Header(...)):
    verify(authorization.replace("Bearer ", ""))
    hemi, levels, uncertainty = encode_spherion(req.lat, req.lon, req.depth)
    return EncodeResponse(
        hemisphere=hemi,
        levels=levels,
        uncertainty=uncertainty
    )
