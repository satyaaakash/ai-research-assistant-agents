from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def parse_query():
    data = request.json
    user_query = data.get("query", "")

    # Very basic keyword extraction logic (can improve with LLM later)
    if "in" in user_query.lower():
        topic = user_query.lower().split("in")[-1].strip()
    else:
        topic = user_query

    response = {
        "topic": topic,
        "original_query": user_query
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)