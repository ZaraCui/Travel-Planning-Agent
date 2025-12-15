from flask import Flask, render_template, request, jsonify
from agent.planner import plan_itinerary_soft_constraints
from agent.geometry import TransportMode
from agent.constraints import ScoreConfig
from agent.models import Spot
from agent.explainer import weather_advice
from datetime import date
import json
import os
import traceback

app = Flask(__name__)

# ===== Unified response helper =====
def success_response(data, message="Success"):
    """Return a successful response with status and data."""
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), 200


def error_response(reason, status_code=400, message="Error"):
    """Return an error response with status and reason."""
    return jsonify({
        "status": "error",
        "code": status_code,
        "message": message,
        "reason": reason
    }), status_code

@app.route('/')
def index():
    # 返回首页，前端页面
    return render_template('index.html')

@app.route('/plan_itinerary', methods=['POST'])
def plan_itinerary():
    try:
        # 获取用户提交的数据
        data = request.json
        if not data:
            return error_response("Request body must be JSON", 400, "Invalid request")
        
        city = data.get('city')
        preference = data.get('preference')
        start_date = data.get('start_date')

        # 验证必需参数
        if not city:
            return error_response("Missing required parameter: 'city'", 400, "Validation error")
        if not preference:
            return error_response("Missing required parameter: 'preference'", 400, "Validation error")
        if not start_date:
            return error_response("Missing required parameter: 'start_date'", 400, "Validation error")

        # 根据偏好设置 transport mode
        preference_to_mode = {
            "walk": TransportMode.WALK,
            "transit": TransportMode.TRANSIT,
            "taxi": TransportMode.TAXI,
        }

        mode = preference_to_mode.get(preference)
        if not mode:
            return error_response(
                f"Invalid preference value '{preference}'. Must be one of: walk, transit, taxi",
                400,
                "Validation error"
            )

        # 加载 spots 数据
        def load_spots(city: str):
            path = f"data/spots_{city}.json"
            if not os.path.exists(path):
                raise FileNotFoundError(f"No spot data found for city: {city}")
            with open(path, encoding="utf-8") as f:
                return [Spot(**s) for s in json.load(f)]

        try:
            spots = load_spots(city)
        except FileNotFoundError as e:
            return error_response(str(e), 404, "City not found")
        except json.JSONDecodeError as e:
            return error_response(f"Corrupted city data: {str(e)}", 500, "Data loading error")

        # 配置评分标准
        cfg = ScoreConfig(
            max_daily_minutes={
                TransportMode.WALK: 240,
                TransportMode.TRANSIT: 300,
                TransportMode.TAXI: 360,
            },
            exceed_minute_penalty=1.5,
            one_spot_day_penalty=15.0,
            min_spots_per_day=2,
        )

        # 获取最佳行程
        try:
            itinerary, score, reasons = plan_itinerary_soft_constraints(
                city=city,
                spots=spots,
                days=3,
                cfg=cfg,
                mode=mode,
                trials=200,
            )
        except Exception as e:
            return error_response(
                f"Failed to plan itinerary: {str(e)}",
                500,
                "Planning error"
            )

        # 计算天气建议
        weather_msg = None
        try:
            # start_date 可能是字符串，需转为 date
            if isinstance(start_date, str):
                start_date_obj = date.fromisoformat(start_date)
            else:
                start_date_obj = start_date
            weather_msg = weather_advice(itinerary, start_date_obj)
        except ValueError as e:
            return error_response(
                f"Invalid date format: {str(e)}. Expected YYYY-MM-DD",
                400,
                "Date parsing error"
            )
        except Exception as e:
            # 天气建议失败不应该导致整个请求失败，但要记录原因
            weather_msg = None
            app.logger.warning(f"Weather advice generation failed: {str(e)}")

        # 将 Spot 对象转换为字典
        itinerary_dict = []
        for day in itinerary.days:
            day_dict = {
                "day": day.day,
                "spots": [spot.to_dict() for spot in day.spots]
            }
            itinerary_dict.append(day_dict)

        # 返回计划结果
        response_data = {
            'score': score,
            'reasons': reasons,
            'itinerary': itinerary_dict,
            'weather_advice': weather_msg,
        }
        
        return success_response(response_data, "Itinerary planned successfully")
    
    except Exception as e:
        # Catch-all for unexpected errors
        app.logger.error(f"Unexpected error in plan_itinerary: {traceback.format_exc()}")
        return error_response(
            f"Unexpected server error: {str(e)}",
            500,
            "Internal server error"
        )


# ===== Error handlers =====
@app.errorhandler(400)
def bad_request(e):
    return error_response(str(e.description) if hasattr(e, 'description') else "Bad request", 400, "Bad request")


@app.errorhandler(404)
def not_found(e):
    return error_response("Endpoint not found", 404, "Not found")


@app.errorhandler(405)
def method_not_allowed(e):
    return error_response("Method not allowed for this endpoint", 405, "Method not allowed")


@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"Internal server error: {traceback.format_exc()}")
    return error_response("Internal server error occurred", 500, "Internal server error")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
