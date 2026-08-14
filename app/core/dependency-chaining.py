async def parse_jwt(token: str = Depends(oauth2_scheme)) -> dict:
 ...

async def valid_owned_post(
 post_id: UUID4,
 token_data: dict = Depends(parse_jwt), # Cached per-request!
) -> Post:
 post = await service.get(post_id)
 if post.creator_id != token_data["user_id"]:
 raise UserNotOwner()
 return post
