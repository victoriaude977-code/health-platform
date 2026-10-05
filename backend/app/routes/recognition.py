"""Food Image Recognition API (Objective 6 - OPTIONAL module).

Per the design phase, AI food recognition is optional: it requires a
pre-trained ResNet model fine-tuned on a food dataset, and is deliberately
left out of the core build to protect the schedule. This blueprint keeps the
endpoint defined so it can be enabled later without changing the frontend.
"""
from flask import Blueprint, jsonify

recognition_bp = Blueprint("recognition", __name__, url_prefix="/api/recognition")


@recognition_bp.post("")
def recognize_food():
    return jsonify(
        error="Food image recognition is an optional module and is not enabled "
              "in this build. Enable it by deploying a fine-tuned ResNet model "
              "in app/services/ai_recognition.py."
    ), 501
