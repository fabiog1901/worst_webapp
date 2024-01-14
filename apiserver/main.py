from fastapi import FastAPI, Depends, HTTPException, Query, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Annotated
from apiserver import db
from apiserver import service as svc
from apiserver.api_router import WorstRouter
from apiserver.models import (
    UserInDB,
    Token,
    User,
    UpdatedUserInDB,
    pyd_models,
)
from apiserver.routers.admin import admin
import os
import threading
import time
import apiserver.dependencies as dep

import hashlib
import os
import urllib.parse as parse
import requests

JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY_SECONDS", 1800))

AUTH_URL = "http://localhost:18080/realms/fabioworst/protocol/openid-connect/auth"
TOKEN_URL = "http://localhost:18080/realms/fabioworst/protocol/openid-connect/token"
SCOPE = "openid"
CLIENT_ID = "BankApp"
CLIENT_SECRET = "XmdmfRWJ149Iaf054NWU0tZvhIeOYMYz"
REDIRECT_URI = "http://localhost:5500/callback"

ALGORITHM = "RS256"
JWKS = '{"keys":[{"kid":"UFnFt3_8o557r-lH2EuOjXAjzn56Xjv-aWlEsz2C0u0","kty":"RSA","alg":"RSA-OAEP","use":"enc","n":"thdVcAuenPhEBkzSQfrdh50jm3A3swFm-WmE-pQvHvaYafzye3ToFC9vIyNtXUF_p4FLgUJWbUrwZU6PCdEb-S8EPx1x3zUJ9GRas-RG9exhB7RQ3iqQYdEaQzlc7Fzw9nV3OTrmvGz4WdZDZ3FVjGNXx2eNRSJEV4hIS-8Hl2iNAar7w4NV9QhhTHIG6cs_Pp1fnw_buIb_Ap2C1EceGH_xyMSdN2K35exHXhQWUP_4Izw0YYZqM-isBDcUSAsfy2Ae4Sl5rawf-CvRUezE616CHOyAdJtigrwgkKVCr6r2-jgvF-yV0ozKC_SyzK2ZRTC9ChAAo8skO02bxgg-lQ","e":"AQAB","x5c":["MIICozCCAYsCBgGMxsl5ODANBgkqhkiG9w0BAQsFADAVMRMwEQYDVQQDDApmYWJpb3dvcnN0MB4XDTI0MDEwMTIwNDcyMVoXDTM0MDEwMTIwNDkwMVowFTETMBEGA1UEAwwKZmFiaW93b3JzdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALYXVXALnpz4RAZM0kH63YedI5twN7MBZvlphPqULx72mGn88nt06BQvbyMjbV1Bf6eBS4FCVm1K8GVOjwnRG/kvBD8dcd81CfRkWrPkRvXsYQe0UN4qkGHRGkM5XOxc8PZ1dzk65rxs+FnWQ2dxVYxjV8dnjUUiRFeISEvvB5dojQGq+8ODVfUIYUxyBunLPz6dX58P27iG/wKdgtRHHhh/8cjEnTdit+XsR14UFlD/+CM8NGGGajPorAQ3FEgLH8tgHuEpea2sH/gr0VHsxOteghzsgHSbYoK8IJClQq+q9vo4LxfsldKMygv0ssytmUUwvQoQAKPLJDtNm8YIPpUCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAVbrQ0HCSB4NPvDUv4SPbO7anjRLH/5f/97CXVWymWIwcuvYUpV3ynvmOsg2ygIYkEZKULwlYhlKcGRnbAU1I1wDzPHO8BVCr6Qz8a4olfcL46jppcf3HfLohDPkNp4rpEFwqwBLIGd39Cj5OwB93MrAQ+ZWykdgZV+kHH8BAqfED3m7+wpHjISjkXlAi1IZ52PqvH0NBWdPBznT8tHOCyXbeiMM26oFBNnmZoC95YZA2wUBloF+HNFpvJrUTAPCJk6ekDYLap3wzSJzdF4LgdykGkUzVMOrYOzotOn5nMSP+2oo8toSIpNA2SZ/pM5hAvP2JftBCunxKWgfvohr36g=="],"x5t":"LvaKfBL3DWrhayiw_ApyR3E2Exg","x5t#S256":"pDexnxZVn4tQToZX6ZzHoz7XXVikyKEk_6KJE5Eby1E"},{"kid":"aBeFPPWPSBtx-mHokr8Dox3IrFdSjeLsXG__uVLmkQs","kty":"RSA","alg":"RS256","use":"sig","n":"2Il9H1HC6iSeJmXUuPBSRy3JOGjcYXyrWr-ETqP9lXRUk4tV8jYBLRNnLt6R5YthpB03X5-AAZZXDPnLqIED2lE9rdvXO_D5sHCrgeIWG-bG11LzZS8oRrzeszOEoxYUdr1VB0HT45mElvmBk4OvEjDbjdBFzuARunmmqjfRh327tu4BSn4bseRTMqozDaYJIp78Hh5YZxz9pNaNQWIqPKyjtWg-HLKmQGUcK32dPloqMrwCgjusdO6mO8W6l0H9-g7AvLrcUoss5H5-LJQWQS3T2ZL8-WzbH3Ji6VKqvtiVzgtPuASDh54ToKxHTlmeO2znfqwfADBP3P3apg4DtQ","e":"AQAB","x5c":["MIICozCCAYsCBgGMxsl4nTANBgkqhkiG9w0BAQsFADAVMRMwEQYDVQQDDApmYWJpb3dvcnN0MB4XDTI0MDEwMTIwNDcyMVoXDTM0MDEwMTIwNDkwMVowFTETMBEGA1UEAwwKZmFiaW93b3JzdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANiJfR9RwuokniZl1LjwUkctyTho3GF8q1q/hE6j/ZV0VJOLVfI2AS0TZy7ekeWLYaQdN1+fgAGWVwz5y6iBA9pRPa3b1zvw+bBwq4HiFhvmxtdS82UvKEa83rMzhKMWFHa9VQdB0+OZhJb5gZODrxIw243QRc7gEbp5pqo30Yd9u7buAUp+G7HkUzKqMw2mCSKe/B4eWGcc/aTWjUFiKjyso7VoPhyypkBlHCt9nT5aKjK8AoI7rHTupjvFupdB/foOwLy63FKLLOR+fiyUFkEt09mS/Pls2x9yYulSqr7Ylc4LT7gEg4eeE6CsR05Znjts536sHwAwT9z92qYOA7UCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAchpFWYaMpWy93OoZKrs9IBmJ+7VXZmHk7idl/Y835cQ7oCLzsRH5B9lR4EXz7KNBaJlpTWs8I/uoiKV58LNeKR8VGDf3sMksKqpR2HwE6Ym1YzSMcWloUM829tKjdCfrIoLa6ONKsJpkaEvVriRKAxAf51lvccEiVEhTVpIwhKV892K6pGmSNaiFCJNB7gdFhnZndc/Mdu/1+h0c1apTNckdPnbuXwrXy+dWmPCKQVXfKyWiFtFPfe9nFf4Dx6u24FESwC3g+bjMHV1B364hNKguBZogiEqa5EQGTzDg+akG4qs6cY3HMEv+yLjtHwGEgT6EyFqJa/zEPMcJGVU0Qw=="],"x5t":"wpGV-y-vuLqwylzggZBh2oOKXcM","x5t#S256":"DT74NssiVfgcRxo7_dBsQPGi3Nltupb2yrb5v6W8dek"}]}'


app = FastAPI(
    title="Worst API",
    version="0.1.0",
    docs_url="/api",
    openapi_url="/worst.openapi.json",
)


app.mount("/app", StaticFiles(directory="webapp/dist"), name="app")

origins = ["http://localhost:5500", "http://localhost:5500/app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
)
async def home() -> FileResponse:
    return FileResponse("webapp/dist/index.html")


@app.get("/healthcheck")
async def healthcheck() -> dict:
    return {"hello": "worst"}


@app.get("/me", dependencies=[Depends(dep.get_current_user)])
async def get_user_me(
    current_user: Annotated[User, Depends(dep.get_current_user)]
) -> User | None:
    return current_user


@app.get("/authorization_code", tags=["auth"])
async def get_authorization_code() -> RedirectResponse:
    return AUTH_URL + "?{}".format(
        parse.urlencode(
            {
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "response_type": "code",
                "scope": SCOPE,
                "state": hashlib.sha256(os.urandom(32)).hexdigest(),
            }
        )
    )


@app.get("/token")
async def get_token(authorization_code: str):
    # exchange auth code for token
    try:
        r = requests.post(
            TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "code": authorization_code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
            },
        )

        token = r.json()
    except Exception as e:
        print("Exception: ", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

    return Token(access_token=token["access_token"], token_type="bearer")


# add routers dynamically
for k, v in pyd_models.items():
    app.include_router(
        WorstRouter(
            model_name=k,
            default_model=v["default"],
            overview_model=v["overview"],
            update_model=v["update"],
        )
    )


# ADMIN
app.include_router(admin.router)


# uvicorn server is started and configured to reload
# if file 'watch.txt' changes.
# Thus, whenever the app wants to instruct uvicorn to reboot itself,
# it just has to touch that file.
# To make sure that every instance of the app reboots,
# the app updates a db entry that is periodically fetched by
# every instance. If the value is different than the initial value,
# the app touches file watch.txt which will cause uvicorn to reload the app.

# store initial value at startup
watch_epoch = db.get_watch()


def watch_it(watch_epoch: int):
    while True:
        if db.get_watch() > watch_epoch:
            Path("watch.txt").touch()

        time.sleep(15)


# periodically check if a restart is needed
threading.Thread(target=watch_it, args=(watch_epoch,), daemon=True).start()
