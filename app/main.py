from fastapi import FastAPI, Depends, Request, Response, Form, Cookie, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from jose import jwt
import json

from .flowers_repository import Flower, FlowerCreate, FlowersRepository
from .purchases_repository import Purchase, PurchaseCreate, PurchasesRepository
from .users_repository import User, UserCreate, UsersRepository
from pydantic import BaseModel

from .database import SessionLocal
from sqlalchemy.orm import Session

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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SignUpRequest(BaseModel):
    full_name: str
    email: str
    password: str


class SignUpResponse(BaseModel):
    full_name: str
    email: str

# needs db


@app.post("/signup", response_model=SignUpResponse)
def post_signup(
    user: SignUpRequest,
    db: Session = Depends(get_db)
):

    tmp = UserCreate(full_name=user.full_name,
                     email=user.email, password=user.password)

    user = users_repository.save(db, tmp)
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")

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

# needs db


@app.get("/profile")
def get_user_profile(
    request: Request,
    cookie_token: str = Cookie(),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user_id = decode_jwt(cookie_token)
    user = users_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user


# Flower path
@app.get("/flowers")
def get_flowers(request: Request, offset: int = 0, limit: int = 5, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    flowers = flowers_repository.get_all(db, offset=offset, limit=limit)
    if flowers is None:
        raise HTTPException(status_code=404, detail="Flower Not Found")
    return flowers


class FlowersRequest(BaseModel):
    name: str
    count: int
    cost: int


class FlowersResponse(BaseModel):
    name: str
    count: int
    cost: int

# needs db


@app.post("/flowers", response_model=FlowersResponse)
def post_flowers(
    flower: FlowersRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    flower = FlowerCreate(name=flower.name, count=int(
        flower.count), cost=int(flower.cost))
    one_flower = flowers_repository.save(db, flower)
    if one_flower is None:
        raise HTTPException(status_code=404, detail="Flower Not Found")
    return flower

class PatchFlower(BaseModel):
    name: str
    count: int
    cost: int

# patch
@app.patch("/flowers/{flower_id}")
def patch_flower(flower: PatchFlower, flower_id: int, db: Session = Depends(get_db)):
    current_flower = flowers_repository.get_by_id(db, flower_id)
    if current_flower is None:
        raise HTTPException(status_code=404, detail="Flower Not Found")
    
    db.query(Flower).filter(Flower.id == id).update(flower.dict())
    db.commit()

    return Response(status_code=200)
    
class DeleteUser(BaseModel):
    name: str
    count: int
    cost: int

# delete 
@app.delete("/flowers/{flower_id}", response_model=DeleteUser)
def delete_flower(flower_id: int, db: Session = Depends(get_db)):
    current_flower = flowers_repository.delete_flower(db, flower_id=flower_id)
    if current_flower is None:
        raise HTTPException(status_code=404, detail="Flower Not Found")
    return current_flower

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

# needs db


@app.get("/cart/items")
def get_cart(request: Request, cart: str = Cookie(default="[]"), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    cart_json = json.loads(cart)  # list of cart items
    flowers_in_basket = []
    for index in cart_json:
        flower = flowers_repository.get_by_id(db, index)
        if flower is None:
            HTTPException(status_code=404, detail="Flower Not Found")
        flowers_in_basket.append(flower)

    return flowers_in_basket
# needs db


@app.post("/purchased")
def get_purchased(flower_id: int = Form(), cookie_token: str = Cookie(), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_id = decode_jwt(cookie_token)
    purchase = PurchaseCreate(user_id, flower_id)
    db_purchase = purchases_repository.add_purchase(db, purchase)
    if db_purchase is None:
        HTTPException(status_code=404, detail="Purchase Not Found")
    return Response(status_code=200)
# needs db


@app.get("/purchased")
def get_purchased(request: Request, offset: int = 0, limit: int = 5, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    purchased_products = purchases_repository.get_all(db, offset, limit)
    if purchased_products is None:
        HTTPException(status_code=404, detail="Purchase Not Found")
    return purchased_products
