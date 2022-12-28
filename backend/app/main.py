from fastapi import FastAPI, UploadFile, File, Body, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pydantic import BaseModel
import timm
import torch
import torch.nn as nn
import cv2
import albumentations as A
from albumentations.pytorch import ToTensorV2
import random
import numpy as np
from sqlalchemy.orm import sessionmaker, Session
from starlette.requests import Request
from .database import Region, engine, User
import json
from fastapi_login import LoginManager

SessionClass = sessionmaker(engine)
session = SessionClass()
class RegionIn(BaseModel):
    id: int
    name: str
    fire: str
    plastic: str
    nonfire: str
    pet: str

class Area(BaseModel):
    name: int
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class UserInfo(BaseModel):
    email: str
    password: str
    area: int

class UserLogin(BaseModel):
    email: str
    password: str

SECRET = '8c135d24ed30d57f770967295653cc48adf3003ceedc95be'

app = FastAPI()
manager = LoginManager(SECRET, token_url='/auth/token')

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#以下は機械学習で呼び出す関数

def torch_fix_seed(seed=42):
    # Python random
    random.seed(seed)
    # Numpy
    np.random.seed(seed)
    # Pytorch
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms = True

class config():
    seed = 42
    size = 384
    batch_size=8  #16
    #model_name="tf_efficientnet_l2_ns"
    model_name="tf_efficientnetv2_b0"
    target_size=7
    n_splits=10
    train_fold_list=[0]
    lr = 1e-4
    num_epoch = 10
    grad_accum_steps = 1
    root_path = "/content/Garbage classification/Garbage classification"
    notebook_name = "Exp013"   #"requests.get('http://172.28.0.2:9000/api/sessions').json()[0]['name'][:-6]
    save_dir = "/content/drive/MyDrive/MyProject/MASSH/output/" + notebook_name

class MASSHModel(nn.Module):
    def __init__(self, cfg, pretrained=False):
        super().__init__()
        self.cfg = cfg
        self.model = timm.create_model(self.cfg.model_name, pretrained=pretrained)
        self.n_features = self.model.classifier.in_features
        self.model.classifier = nn.Identity()
        self.fc = nn.Linear(self.n_features, self.cfg.target_size)

    def feature(self, image):
        feature = self.model(image)
        return feature

    def forward(self, image):
        feature = self.feature(image)
        output = self.fc(feature)
        return output


@app.post("/posts")
def index(area: Area, upload_file: UploadFile = File(...)):
    try:
        path = f'app/images/{upload_file.filename}'
        with open(path, 'wb+') as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        buffer.close()
    except Exception as e:
        print(e)

    # ここからがモデル
    CFG = config
    torch_fix_seed(CFG.seed)

    transform = A.Compose([
                A.Resize(CFG.size, CFG.size),
                A.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
                ToTensorV2(),
            ])

    fold = 0

    MODEL_PATH = f"app/models/fold{fold}_best_model_small.pth"

    model = MASSHModel(CFG)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))

    image_path = "app/images/" + upload_file.filename
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = transform(image=image)["image"].unsqueeze(0)
    output = model(image).detach().cpu().numpy()

    label_to_name = {0:"pet",
                1:"nonfire",
                2:"plastic",
                3:"sigen",
                4:"sigen",
                5:"fire",
                6:"sigen"}

    label_to_name2 = {0:"ペットボトル",
            1:"燃やさないごみ",
            2:"包装容器プラスチック類",
            3:"資源ごみ(空き缶類)",
            4:"資源ごみ(紙類)",
            5:"燃やすごみ",
            6:"資源ごみ(紙類)"}

    region_id = area.name
    region_list = {}

    region = session.query(Region).filter_by(id=region_id).first()

    region_list["fire"] = region.fire
    region_list["pet"] = region.pet
    region_list["nonfire"] = region.nonfire
    region_list["plastic"] = region.plastic

    if(int(np.argmax(output, axis=1)) in [0, 1, 2, 5]):
        ans_label = label_to_name[int(np.argmax(output, axis=1))]
        ans = region_list[ans_label]
    else:
        ans = "自治体の指示に従ってください"
    # ここまで

    return {
        'type': label_to_name2[int(np.argmax(output, axis=1))],
        'ans': ans,
    }

@app.post('/regions')
def get_regions():
    regions = session.query(Region).all()
    list = []
    for region in regions:
        list.append(region.name)
    return {
        'regions': list
    }



@app.post("/signup")
async def signup(user: UserInfo):
    check_user = session.query(User).filter_by(email=user.email).first()
    if not check_user:
        session.add(User(email = user.email, password = user.password, area=user.area))
        session.commit()
        return {"is_success": True, "error": ""}
    else:
        return {"is_success": False, "error": "exists"}

@app.post('/auth/token')
async def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    login_user = session.query(User).filter_by(email=email).first()
    if not login_user:
        return {"is_success": False, "error": ""}
    elif password != login_user.password:
        return {"is_success": False, "error": ""}

    access_token = manager.create_access_token(
        data=dict(sub=email)
    )
    return {'access_token': access_token, 'token_type': 'bearer', "is_success": True, "error": "", 'user_area': login_user.area}


