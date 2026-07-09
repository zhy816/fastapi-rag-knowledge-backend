from datetime import datetime

from pydantic import BaseModel, ConfigDict

# 这个文件负责规定：注册接口接收什么数据，返回给前端什么数据。

# UserCreate：用户注册时传进来的数据 我们使用UserCreate 对他进行格式的规定
# UserRead：接口返回给用户看的数据
# from_attributes=True：允许 Pydantic 从 SQLAlchemy ORM 对象里读取字段

class UserCreate(BaseModel):
    username: str
    password: str

# 这个 BaseModel 的作用是：规定用户注册完成后， 他返回给用户的信息的格式应该是什么样子的
# 1. 校验接口传进来的 JSON 数据
# 2. 控制接口返回出去的数据格式
class UserRead(BaseModel):
    id: int
    username: str
    create_time: datetime

    # 允许 UserRead 从 SQLAlchemy ORM 对象 里面读取数据。因为我们从数据库里面得到的数据，
    # 是会被转换成 对象.属性 的形式，
    # 而不是字典的存储形式
    # 所以 我们要允许 这个读取对象的数据 应该是从属性里面读， 而不是字典里面读

    # 你别只按字典方式找字段，你也可以从对象属性里找，
    # 比如 db_user.id、db_user.username、db_user.create_time。
    model_config = ConfigDict(from_attributes=True)

    # 是 Pydantic 规定的模型配置写法。
    #
    # 因为 UserRead 继承了 BaseModel，所以 Pydantic 在创建这个模型类的时候，
    # 会专门去识别类里面的 model_config，然后根据里面的配置改变这个模型的行为。
    # Pydantic 官方文档也写了，Pydantic 模型就是继承 BaseModel 的类，
    # 并通过类型注解定义字段