from fastapi import Header, HTTPException
import os

async def verify_token(authorization: str = Header()):
    # Check Authen
    if authorization != os.getenv("BASIC_AUTH"):
        raise HTTPException(status_code=400, detail="Token Invalid")
