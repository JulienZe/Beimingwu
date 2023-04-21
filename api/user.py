from flask import Blueprint, g, jsonify, request, session
import json
import os, time
from config import C
import hashlib
from .utils import *
from .auth import login_required

if C.database_type == "sqlite":
    import lib.sqlite as database

import lib.engine as engine_helper

__all__ = ["user_api", "remove_learnware"]

user_api = Blueprint("User-API", __name__)


def remove_learnware(learnware_id: str) -> bool:
    # [TODO] Require code for engine
    # try:
    ok = C.engine.delete_learnware(learnware_id)
    if not ok:
        return False
    cnt = database.remove_learnware("learnware_id", learnware_id)
    return cnt > 0
    # except:
        # return False


@user_api.route("/get_profile", methods=["POST"])
@login_required
def get_profile():
    # Return profile
    result = {
        "code": 0,
        "msg": "Get profile success.",
        "data": {"username": g.user["username"], "email": g.user["email"]},
    }
    return jsonify(result)

@user_api.route("/change_password", methods=["POST"])
@login_required
def change_password():
    data = get_parameters(request, ["old_password", "new_password"])
    old_value = data["old_password"]
    new_value = data["new_password"]
    user_id   = g.user["id"]
    user = database.get_user_info(by="id", value=user_id)
    
    if user is None:
        return jsonify({"code": 51, "msg": "Account not exist."})
    elif not user["password"] == old_value:
        return jsonify({"code": 52, "msg": "Incorrect password."})
    flag = database.update_user_password(pwd=new_value, by="id", value=user_id)
    if not flag:
        return jsonify({"code": 31, "msg": "Update error."})
    
    # Return profile
    result = {
        "code": 0,
        "msg": "Update success"
    }
    return jsonify(result)


@user_api.route("/get_learnware_list", methods=["POST"])
@login_required
def get_learnware_list():
    data = get_parameters(request, [])
    # Return learnware list directly
    if data is None or "limit" not in data:
        ret, cnt = database.get_learnware_list("user_id", g.user["id"])
        learnware_list = engine_helper.get_learnware_by_id([x["learnware_id"] for x in ret])
        result = {
                "code": 0,
                "msg": "Ok.", 
                "data": {
                    "learnware_list": learnware_list
                    }
                }
        return jsonify(result)
    # Calculate the page limit
    limit = data["limit"]
    if limit == 0:
        return jsonify({"code": 51, "msg": "Limit cannot be 0."})
    page  = 0 if "page" not in data else data["page"]
    ret, cnt = database.get_learnware_list("user_id", g.user["id"], limit, page)
    learnware_list = engine_helper.get_learnware_by_id([x["learnware_id"] for x in ret])
    result = {
        "code": 0, 
        "msg": "Ok.", 
        "data": {
            "learnware_list": learnware_list,
            "page": page,
            "limit": limit,
            "total_pages": (cnt + limit - 1) // limit
        }
    }
    return jsonify(result)


@user_api.route("/add_learnware", methods=["POST"])
@login_required
def add_learnware():
    semantic_specification = request.form.get("semantic_specification")
    if request.files is None or 'learnware_file' not in request.files or semantic_specification is None:
        return jsonify({"code": 21, "msg": f"Request parameters error."})

    learnware_file = request.files['learnware_file']
    if learnware_file.filename == '' or not learnware_file:
        return jsonify({"code": 21, "msg": f"Request parameters error."})

    leareware_filename = f"{int(time.time())}_" + hashlib.md5(learnware_file.read()).hexdigest() + ".zip"
    if not os.path.exists(C.upload_path):
        os.mkdir(C.upload_path)
    learnware_path = os.path.join(C.upload_path, leareware_filename)
    learnware_file.seek(0)
    learnware_file.save(learnware_path)
    try:
        semantic_specification = json.loads(semantic_specification)
    except:
        return jsonify({"code": 41, "msg": "Semantic specification error"})
    
    user_id = g.user["id"]
    # learnware_id = generate_random_str(16)
    # [TODO] Add learnware
    # try:
    learnware_id, ok = C.engine.add_learnware(learnware_path, semantic_specification)
    # except:
        # return jsonify({"code": 42, "msg": "Engine add learnware error."})
    if ok == C.engine.INVALID_LEARNWARE:
        return jsonify({"code": 42, "msg": "Your learnware is invalid."})
    
    # Add learnware
    cnt = database.add_learnware(user_id, learnware_id)
    if cnt > 0:
        result = {"code": 0, "msg": f"Add success."}
    else:
        result = {
            "code": 31,
            "msg": "System error.",
        }
    
    if C.remove_upload_file: os.remove(learnware_path)
    return jsonify(result)


@user_api.route("/delete_learnware", methods=["POST"])
@login_required
def delete_learnware():
    # Check & get parameters
    data = get_parameters(request, ["learnware_id"])
    if data is None:
        return jsonify({"code": 21, "msg": "Request parameters error."})
    learnware_id = data["learnware_id"]

    # Check permission
    learnware_infos, cnt = database.get_learnware_list("learnware_id", learnware_id)
    if len(learnware_infos) == 0 or learnware_infos[0]["user_id"] != g.user["id"]:
        return jsonify({"code": 51, "msg": "You do not own this learnware."})
    
    # Remove learnware
    if remove_learnware(learnware_id):
        result = {"code": 0, "msg": "Delete success."}
    else:
        result = {
            "code": 31,
            "msg": "System error.",
        }
    return jsonify(result)
