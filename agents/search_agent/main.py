from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def search_arxiv():
    data = request.json
    topic = data.get("topic", "")

    if not topic:
        return jsonify({"error": "Missing 'topic' in request."}), 400

    query = topic.replace(" ", "+")
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5"

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from arXiv"}), 500

    root = ET.fromstring(response.content)
    ns = {"arxiv": "http://www.w3.org/2005/Atom"}

    papers = []
    for entry in root.findall("arxiv:entry", ns):
        paper = {
            "title": entry.find("arxiv:title", ns).text.strip(),
            "summary": entry.find("arxiv:summary", ns).text.strip(),
            "link": entry.find("arxiv:id", ns).text.strip(),
            "authors": [author.find("arxiv:name", ns).text.strip() for author in entry.findall("arxiv:author", ns)]
        }
        papers.append(paper)

    return jsonify({
        "topic": topic,
        "results": papers
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)