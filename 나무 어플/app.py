from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 업로드 폴더 설정
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    # 파일 수신
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400
    
    # 파일 저장
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # 위도 및 경도 수신
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    if not latitude or not longitude:
        return jsonify({"error": "Latitude or Longitude not provided"}), 400

    # 필요한 추가 처리 (예: 데이터베이스 저장 등)
    print(f"Received file: {filename}")
    print(f"Latitude: {latitude}, Longitude: {longitude}")

    response = {
        "message": "File uploaded successfully",
        "file_path": file_path,
        "latitude": latitude,
        "longitude": longitude
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
