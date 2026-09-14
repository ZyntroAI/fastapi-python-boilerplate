def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    return payload

def require_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker
