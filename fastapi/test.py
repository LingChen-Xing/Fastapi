from fastapi import FastAPI,Form,Query,Header,HTTPException,Request,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware  # 跨域支持
import uvicorn
from typing import Optional,List
from enum import Enum
from pydantic import BaseModel
from fastapi.responses import JSONResponse,RedirectResponse
from starlette.exceptions import HTTPException as Http_404
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse


#定义枚举类型
class ModelName(str,Enum):
    bj = "beijing"
    nj = "nanjing"
    sh = "shanghai"


app = FastAPI(
    title="My API",  # API名称
    version="1.0.0",  # 版本号
    docs_url="/docs",  # 文档地址
    redoc_url=None      # 禁用Redoc文档
)
app.mount("/static",StaticFiles(directory="static"),name="static")#当读取到static文件夹的时候不要把下面的东西当作路由来执行

#定义jinja模板加载位置
templates = Jinja2Templates(directory="templates")

#定义后台需要做什么
def write_notifiy(email:str,message=""):
    with open("log.txt",mode="w") as email_file:
        content = f"user is doing {email} : {message}"
        email_file.write(content)

# origins = [#这里定义谁可以访问我,比如下面这个网站的人就可以访问我网站的资源，其他人不行
#     "http://www.xxx.com"
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins = origins,
#     #这里要注意防范CRSF，要使用的话要做好限制
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )


#定义异常处理类
class UnicornException(Exception):
    def __init__(self,name:str):
        self.name = name

#自定义异常处理器
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request:Request,exc:UnicornException):
    return JSONResponse(
        status_code=401,
        content={"message":f"you are wrong {exc.name}, please go back"}
    )

#404
@app.exception_handler(Http_404)
async def Http_404(request,exc):
    return RedirectResponse('/Not_found')

@app.get('/Not_found')
async def Http_404_page():
    return {'Not found':'路由错误'}

#定义一个数据模型
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 10.1#没有设置的话默认是这么多
    tags:List[str] = []

#定义返回值，结构必须要和上面的类一致
items = {
    "sp1":{"name":"sp1","price":100.2},
    "sp2":{"name":"sp2","description":"Good things","price":1000.2,"tax":9.8},
    "sp3":{"name":"sp3","description":"Good things","price":120.2,"tax":19.8,"tags":[]}
}

# 配置跨域访问 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源访问（生产环境建议指定域名）
    allow_credentials=True,
    allow_methods=["*"],   # 允许所有HTTP方法
    allow_headers=["*"],   # 允许所有请求头
)

@app.get("/")
async def fun():
    return {"message": "good", "status": 200}

@app.get("/a")
async def fun_a():
    return {"message": "haha", "status": 200}

@app.get("/b")
async def fun_b_none():
    return {"message": "you should input a number", "status": 200}

@app.get("/b/{id}")
async def fun_b(id:int):
    return {"message": id, "status": 200}

@app.get("/c")
async def fun_c(q:Optional[str]=None):#默认是空
    if q is None:
        return "Please input q by Get method"
    else:
        return {"message": q, "status": 200}

@app.get("/c/{id}")
async def fun_c(id, q:Optional[str]=None):#默认是空
    if q is None:
        return "Please input q by Get method"
    else:
        return {"message": q, "id": id, "status": 200}

@app.post("/d")
async def fun_d(q:Optional[str]=Form()):#默认是空
    if q is None:
        return "Please input q by Get method"
    else:
        return {"message": q, "status": 200}

#用户只能输入我定义的内容，如果里面的东西写死的话，是有一定防sql注入的能力的，相对安全一些
@app.get("/e/{id}")
async def fun_e(id:ModelName):
    if id == ModelName.bj:
        return "your choose is beijing"
    return "other"

@app.get("/f")
async def fun_f_none(q:Optional[str] = Query("默认值",min_length=3,max_length=8,regex="^haha")):#但是这里的默认编码是unicode,regex里面是正则表达式
    #高级一些的返回
    result = {"item":[{"user1":"Admiewang"},{"user2":"dzy"}]}
    if q:
        result.update({"q":q})
    return result

@app.get("/g")
async def fun_g_none(q:Optional[List[str]] = Query(None)):#这里可以传入多个q
    #高级一些的返回
    result = {"item":[{"user1":"Admiewang"},{"user2":"dzy"}]}
    if q:
        result.update({"q":q})
    return result

@app.get("/h")
async def fun_h(user_agent:Optional[str] = Header(None)):

    return {"message": user_agent, "status": 200}

@app.get("/buy/{item_id}",response_model=Item,response_model_exclude_unset=True)#response_model_exclude_unset=True响应不包含默认值
async def fun_buy(item_id:str):
    #response_model_exclude={“tax”}#不会把tax字段的东西输出出来

    return items[item_id]

#返回状态码，还是能显示出来的
@app.get("/i",status_code=404)
async def fun_i(user_agent:Optional[str] = Header(None)):

    return {"message": user_agent, "status": 200}

#错误处理
@app.post("/j/{id}")
async def fun_j(id:str):#默认是空
    items = {"xing":"welcome"}
    if id not in items:
        raise HTTPException(
            status_code = 404,
            detail = "you are wrong",
            headers = {"X-Error":"Error"}
        )
    else:
        return {"message": items[id], "status": 200}

    # 错误处理
@app.post("/k/{id}")
async def fun_k(id: str):  # 默认是空
    items = {"xing": "welcome"}
    if id not in items:
        raise UnicornException(name = id)
    else:
        return {"message": items[id], "status": 200}

@app.get("/email",status_code=200)
async def fun_emile(email:str,background_tasks:BackgroundTasks):
    background_tasks.add_task(write_notifiy,email,message="haha")

    return {"message": "over", "status": 200}

#Jinja模板
@app.get("/moban",response_class=HTMLResponse)
async def fun_moban(email:str,background_tasks:BackgroundTasks):
    return templates.TemplateResponse("item/index.html")

# 添加健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run(
        app="test:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # 新增日志配置
        access_log=True,  # 启用访问日志
        log_config="uvicorn_log.yaml"  # 自定义日志格式
    )