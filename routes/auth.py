from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from utils import spotify
from utils.firebase import db
from database.models.user import User


router = APIRouter()

@router.get("/login")
async def login():
    return {"auth_url": spotify.get_spotify_auth_url()}


@router.get("/callback")
def get_token(code: str = None):    
    try:
        parsed_code = spotify.parse_response_code(code)
        
        if parsed_code is None:
            raise HTTPException(status_code=400, detail="Invalid code")
        token = spotify.get_spotify_token(parsed_code)
  
        if "error" in token:
            raise HTTPException(status_code=400, detail="Invalid token")
        
        access_token = token["access_token"]
        refresh_token = token["refresh_token"]
 
        sp_auth = spotify.get_spotify_client(access_token)
        
        # get user info
        user_data = sp_auth.me()
        user = User.get_by_id(user_data["id"])
        
        if user is None:
            user = User(
                id=user_data["id"],
                username=user_data["display_name"]
            )
            user.save()
            
        response = JSONResponse(content={"user": user.to_dict(), "message": "User logged in successfully"})
        response.set_cookie(key="access_token", value=access_token)
        response.set_cookie(key="refresh_token", value=refresh_token)
        
        return response
        
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/logout")
def logout():
    response = JSONResponse(content={"message": "User logged out"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

    