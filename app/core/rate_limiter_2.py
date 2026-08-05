@router.get("/limited")
@limiter.limit("100/minute")
async def limited_endpoint(request: Request):
    return {"message": "This is rate-limited!"}
