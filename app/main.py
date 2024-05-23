from fastapi import FastAPI, Depends, Request, Response, Form, Cookie, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from jose import jwt
import json

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository
from pydantic import BaseModel

from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()

def create_jwt(user_id: int) -> int:
    body = {"user_id": user_id}
    token = jwt.encode(body, "zhansen-secret", "HS256")
    return token


def decode_jwt(token: str) -> int:
    tok = jwt.decode(token, "zhansen-secret", "HS256")
    return tok["user_id"]

class SignUpRequest(BaseModel):
    full_name: str
    email: str
    password: str


class SignUpResponse(BaseModel):
    full_name: str
    email: str
    password: str

@app.post("/signup", response_model=SignUpResponse)
def post_signup(
    user: SignUpRequest
):

    tmp = User(full_name=user.full_name,
               email=user.email, password=user.password)
    users_repository.save(tmp)

    return user

@app.post("/login")
def login_post(username: str = Form(), password: str = Form()):
    user = users_repository.get_by_email(username)
    if not user:
        raise HTTPException(status_code=400, detail={
                            "value": username, "msg": "incorrect username"})
    if user.password == password:
        # response = RedirectResponse(url="/profile", status_code=303)
        token = create_jwt(user.id)
        return {"access_token": token, "type": "bearer"}
        # response.set_cookie("token", token)
    else:
        raise HTTPException(status_code=400, detail={
                            "value": password, "msg": "incorrect password"})

# ваше решение сюда


@app.get("/profile")
def get_user_profile(
    request: Request,
    cookie_token: str = Cookie(),
    token: str = Depends(oauth2_scheme)
):
    user_id = decode_jwt(cookie_token)
    user = users_repository.get_by_id(user_id)
    return user


# Flower path
@app.get("/flowers", response_model=list[Flower])
def get_flowers(request: Request, token: str = Depends(oauth2_scheme)):
    flowers = flowers_repository.get_all()
    return flowers


class FlowersRequest(BaseModel):
    name: str
    count: int
    cost: int


class FlowersResponse(BaseModel):
    name: str
    count: int
    cost: int


@app.post("/flowers", response_model=FlowersResponse)
def post_flowers(
    flower: FlowersRequest,
    token: str = Depends(oauth2_scheme)
):
    flower = Flower(name=flower.name, count=int(
        flower.count), cost=int(flower.cost))
    flowers_repository.save(flower)
    return flower


@app.post("/cart/items")
def post_cart(
    response: Response,
    flower_id: int = Form(),
    cart: str = Cookie(default="[]"),
    token: str = Depends(oauth2_scheme)
):
    cart_json = json.loads(cart)
    if flower_id not in cart_json:
        cart_json.append(flower_id)
    new_cart = json.dumps(cart_json)
    response = RedirectResponse("/cart/items", status_code=303)
    response.set_cookie(key="cart", value=new_cart)
    return response


@app.get("/cart/items", response_model=list[Flower])
def get_cart(request: Request, cart: str = Cookie(default="[]"), token: str = Depends(oauth2_scheme)):

    cart_json = json.loads(cart)  # list of cart items
    flowers_in_basket = []
    for index in cart_json:
        flowers_in_basket.append(flowers_repository.get_by_id(index))

    return flowers_in_basket

@app.post("/purchased")
def get_purchased(flower_id: int = Form(), cookie_token: str = Cookie(), token: str = Depends(oauth2_scheme) ):
    user_id = decode_jwt(cookie_token)
    purchase = Purchase(user_id, flower_id)
    purchases_repository.add_purchase(purchase)
    return Response(status_code=200)

@app.get("/purchased")
def get_purchased(request: Request, token: str = Depends(oauth2_scheme)):
    purchased_products = purchases_repository.get_all()

    return purchased_products
