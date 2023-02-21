from fastapi import FastAPI, Depends, Header
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import Response, JSONResponse, FileResponse
import logging
import redis
import copy
import json


class Student(BaseModel):
    name: str
    id: str
    mobile_no: str
    graduated: bool


class NewStudentForm(BaseModel):
    name: str
    mobile_no: str


def get_redis_client():
    return redis.Redis(host="redis")


app = FastAPI()

logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

user_id_start = 1006000

user_list = {
    '1001001': {'name': 'Adam John Doe', 'id': '1001001', 'mobile_no': '80042342', 'graduated': True},
    '1001032': {'name': 'Brian John Doee', 'id': '1001032', 'mobile_no': '67526339', 'graduated': True},
    '1004301': {'name': 'Charlie Johnn Doeee', 'id': '1004301', 'mobile_no': '80049342', 'graduated': False},
    '1004421': {'name': 'David Johssn Doae', 'id': '1004421', 'mobile_no': '90042342', 'graduated': True},
    '1005034': {'name': 'Edwin Jokhn Deoe', 'id': '1005034', 'mobile_no': '87202342', 'graduated': False},
    '1001321': {'name': 'Franklin Johin Dobe', 'id': '1001321', 'mobile_no': '98110995', 'graduated': True},
    '1000207': {'name': 'George Johns Doke', 'id': '1000207', 'mobile_no': '94879262', 'graduated': False},
}

user_avatar_list = {'1001001': 0,
                    '1001032': 1,
                    '1004301': 2,
                    '1004421': 3,
                    '1005034': 4,
                    '1001321': 5,
                    '1000207': 0, }

avatar_list = ['data:image/jpeg;base64,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', 'data:image/jpeg;base64,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', 'data:image/jpeg;base64,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', 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHYAAAB2CAMAAAAqeZcjAAAAZlBMVEX///9CQkEhISDp6ek+Pj06Ojnv7+/09PQ3NzYzMzIbGxr8/PwwMC/39/erq6sqKinKyspPT051dXXU1NSCgoLh4eElJSNWVlVHR0Zubm2YmJi4uLhoaGddXVzAwMCOjo6goKAREQ8reef3AAAExklEQVRoge1a25aqMAylUqAdqoACgsjg/P9PnhbKTVuIM815cj+5XNZNmnuC533wwQcfICOO/Ph/8kWnvKUiOXwdvnh2fqTH/8J6ETygRINSJsq2wWdtBHkGFVmBS1qc+QtrL/QJkzWlzMQqwdsUjfVCqYVVCszrEIe1IHZWiYDhaPgebLESwnIU2mxTWHnPdwzWsNxmJaTCCFsnmxXP4iLQHo0eu0Rwc8/q5TsGpYBgytcdg1Lits5vOa72hSWZ82wU7wtLiHAeqEC0ybdzWgArCZzHKZBu6dW1cuO90KjAOsesIAciycU5bQuR1n05d9+npXf3QbkGRCmEhAugpVfX4SI+AzIBYWfHt+wfAKwyOjrOQf5uadGjdOxB0W5p0SNxnXEBFqXg2qZOuzUNwXDcMAHQ8odjVlAtxan74Jj+7F7xCaPDbnZyEK0RSCUe207EMMpkicu2MQusDndb2jJCos23eGmFxOpdtmixVOttd7hoqt2OkAEaqxdu3LH7WnVGZxWXu69VZ/g25dIMkVVGqtfZ3yAs6hjOiyyBmfqotN63UVyMCnkNY3Uj0Ge7nSndI6vWs1QZiJFR42y65OCMzBobOz/aItOGmdGBKqxkq+Gbk1+AGRs9tRgx0mJ7kCX3YduUtUpH3ULFlsk9rR4XLGL/uw79yui3WXEur13qfubon2oqvgqvMGxlgmvhtWrxluWpQ0+Ki8ddCEmXpKYqPbj640wySKrczbIxvtyuCaezn6RPPWfQyruNpi8lc3f5a5+bdiRh07Wyh/quWQ0ymGL1iuV3QVndfj9OiL/zJFlZrk7np3LJ2kv2nP5ZmZ1+Y2BRUyfi2VvGZvI2kXC9c7q9BE3KDvc3Y1fY3AU3eApttbl0mpeP0Sk3JiYucnCwDr/rwMSpUI0Xl/f2LEbW2DaAZfzaAC47Ss+E28cUfLIUtUAWU+UW2rsyykm3I3LRZRucZNlgHWsm5gbksjnIYey+wVzUfG/YthgBhe2igDpZyvZJZJbUligSkv0J37IgLhY6A4yPmKXwOQPminTap4UPkk1rnyNkpC8eJtYCNLuthq7Dv0lLoclda2zDohbgpjRhrLtfH3kgygcToj9DQHgO05azpiIeNjHWRwstnh7PvMYoE0xbdHNP9YLRpoYh/tgNAMe+yestQ9bC6omvw8+HqY0Y/ieEbOLIkK7XiGGsErqTVd3BKKylin3BkDeX2A4zC3D9xI0Mjkwb8gMy4yamNnhnjrl4Yi1hJw/w5i3VGoaw0JNTl6WmCboo94GqfV20HqGsRK8h/P7jMAODee18dkYB81qFQblpr84hD8K8VoE9TVZAiw99tJupWK9cSEAe8LzgBXqtwjD5Gqh65RZwBYn1OwOgDDJC3Wyof8+1K0GPrqNyCBdW3qw8m2p1qu1aDT/8NBAFBwsF5UKjFclHOELdRx1dt8F7NckaSTi9ICD/J4Xf8fM2rgO7gAJr5reY+Htns5XjgmNUD1rPXV9ZmEc3Fqwc1zL1sSKYK5Egf+vkynGLt1SryIwfAVg57htB9Y9YrVqh+fLvWGVc0NsNTrDMuMe6IgHjLEnKQ4+vCQcnmP/vh1nbvziOj8doQDjBfwehHy4RLWBj/eCDDz4w4R8gA0EwVPF3ygAAAABJRU5ErkJggg==', 'data:image/png;base64,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', 'data:image/png;base64,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']


@app.get("/")
def read_root():
    return "Hello World"


@app.get("/students/{id}")
def get_studetns(id: str):
    if id:
        if id in user_list:
            return user_list[id]
        else:
            return Response(status_code=404, content="Entry does not exist")


@app.get("/avatar/{id}")
def get_avatar(id: str):
    if id in user_list:
        return Response(status_code=200, media_type="image/png", content=avatar_list[user_avatar_list[id]])
    else:
        return Response(status_code=404, content=f"Student {id} does not exist!")

@app.post("/login")
def login(Authorization: Optional[str] = Header(default=None)):
    if Authorization == None:
        return Response(status_code=401, content="missing auth token")
    token = Authorization.split(" ")[1]
    logger.warn(token)
    if token != 'aFs0hQDHTYb53NGC9lljiw':
        return Response(status_code=401, content="unauthorised")
    
    return Response(status_code=200, content="Logged In!")

@app.get("/students")
def get_studetns(sortBy: Optional[str] = None, count: Optional[int] = None, offset: Optional[int] = None):
    lists = copy.deepcopy(list(user_list.values()))
    logger.warn(lists)
    if sortBy != None:
        filter = ''
        if sortBy == 'name':
            logger.warn("sortby name")
            filter = 'name'
        elif sortBy == 'id':
            logger.warn("sortby id")
            filter = 'id'
        elif sortBy == 'mobile_no':
            logger.warn("sortby mobile")
            filter = 'mobile_no'
        elif sortBy == 'graduated':
            logger.warn("sortby grad")
            filter = 'graduated'
        else:
            logger.warn("none")
            return Response(status_code=400, content=f"Invalid query param: sortBy={sortBy}")
        lists.sort(key=lambda x: x[filter])

    if count != None:
        logger.warn(count)
        if count <= 0:
            logger.warn("illegal count")
            return Response(status_code=400, content=f"Invalid query param: count={count}")
        size_arr = len(lists)
        if count < size_arr:
            lists = lists[0:count]

    if offset != None:
        if offset <= 0:
            logger.warn("illegal offset")
            return Response(status_code=400, content=f"Invalid query param: offset={offset}")
        size_arr = len(lists)
        if offset < size_arr:
            lists = lists[offset:]

    return JSONResponse(status_code=200, content=lists)


@app.post("/new-student")
def create_student(student: NewStudentForm, redis_client: redis.Redis = Depends(get_redis_client)):
    # By default a new student is not graduated and will be allocated to a new student id
    global user_id_start
    while user_id_start in user_list:
        user_id_start += 1
    new_student = {'name': f'{student.name}', 'id': f'{user_id_start}',
                   'mobile_no': f'{student.mobile_no}', 'graduated': False}
    redis_client.set(new_student['id'], json.dumps(new_student))
    user_list[new_student['id']] = new_student
    logger.warn(user_list)
    return JSONResponse(status_code=200, content=new_student)


@app.put("/students/{id}")
def get_studetns(id: str, request: Student):
    user_list[id] = {'name': f'{request.name}', 'id': f'{request.id}',
                     'mobile_no': f'{request.mobile_no}', 'graduated': request.graduated}
    return user_list[id]


@app.delete("/students/{id}")
def get_studetns(id: str):
    if id in user_list:
        user_list.pop(id)
        return Response(status_code=200, content=f"Deleted student {id} successfully!")
    else:
        return Response(status_code=404, content=f"Student {id} does not exist!")

@app.patch("/graduate")
def graduate_student(smallerEq:str):
    if smallerEq not in user_list:
        return Response(status_code=404, content=f"Student {smallerEq} does not exist!")
    to_graduate = [k for k in user_list.keys() if int(k) <= int(smallerEq)]
    for i in to_graduate:
        user_list[i]['graduated'] = True

    return Response(status_code=200, content="success")