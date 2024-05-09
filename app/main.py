from fastapi import FastAPI, Depends, Request, Response, Form, Cookie, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from jose import jwt
import json

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository
from pydantic import BaseModel

app = FastAPI()
# templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()

# @app.get("/login")
# def login_get(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_post(email: str = Form(), password: str = Form()):
    user = users_repository.get_by_email(email)
    if not user:
        raise HTTPException(status_code=400, detail={"value": email, "msg": "incorrect username"})
    if user.password == password:
        # response = RedirectResponse(url="/profile", status_code=303)
        token = create_jwt(user.id)
        # response.set_cookie("token", token)
    else:
        raise HTTPException(status_code=400, detail={"value": password, "msg": "incorrect password"})
    return {"access_token": token, "type": "bearer"}




# @app.get("/")
# def root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# ваше решение сюда
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


# singup response
# @app.get("/signup")
# def get_singup(request: Request):
#     return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_model=SignUpResponse)
def post_signup(
    user: SignUpRequest,
    oauth
):

    user = User(full_name=user.full_name, email=user.email, password=user.password)
    users_repository.save(user)

    return user

    

# profile request
# profile response

@app.get("/profile")
def get_user_profile(
    request: Request,
    token: str = Cookie()
):
    user_id = decode_jwt(token)
    user = users_repository.get_by_id(user_id)
    return {
        "email": user.email,
        "full_name": user.full_name,
        "password": user.password,
        "id": user.id
    }


    

# flower request
# flower response

# Flower path
# @app.get("/flowers")
# def get_flowers(request: Request):
#     flowers = flowers_repository.get_all()
#     return templates.TemplateResponse("flowers.html", {"request": request, "flowers": flowers})



@app.post("/flowers")
def post_flowers(
    request: Request,
    name: str = Form(),
    count: str = Form(),
    cost: str = Form()
    ):
    flower = Flower(name=name, count=int(count), cost=int(cost))
    flowers_repository.save(flower)
    return RedirectResponse("/flowers", status_code=303)

    

# cart items request
# catt items response
# Basket path
@app.get("/cart/items")
def get_cart(request: Request, cart: str = Cookie(default="[]")):
    
    cart_json = json.loads(cart) # list of cart items
    flowers_in_basket = []
    for index in cart_json:
        flowers_in_basket.append(flowers_repository.get_by_id(index))
    
    return templates.TemplateResponse("cart.html", {"request": request, "cart":flowers_in_basket } )


# cart items request
# cart items response
@app.post("/cart/items")
def post_cart(
    response = Response,
    flower_id: int = Form(),
    cart: str = Cookie(default="[]")
):
    cart_json = json.loads(cart)
    if flower_id not in cart_json:
        cart_json.append(flower_id)
    new_cart = json.dumps(cart_json)
    response = RedirectResponse("/cart/items", status_code=303)
    response.set_cookie(key="cart", value=new_cart)
    return response

# purchased request
# purchased response

@app.get("/purchased")
def get_purchased(request: Request):
    flowers = []
    purchased_products = purchases_repository.get_all()
    for purchase in purchased_products:
        current_flower = flowers_repository.get_by_id(purchase.flower_id)
        flowers.append(current_flower)
    return templates.TemplateResponse("purchased.html", {"request": request, "products": flowers})

@app.post("/purchased")
def get_purchased(flower_id: int = Form(), token: str = Cookie()):
    user_id = decode_jwt(token)
    purchase = Purchase(user_id, flower_id)
    purchases_repository.add_purchase(purchase)
    return RedirectResponse("/purchased", status_code=303)

    


    
# конец решения
