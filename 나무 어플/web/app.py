from flask import Flask, request, jsonify, render_template
import folium
import pandas as pd
import os
from PIL import Image
import base64
import cv2
from ultralytics import YOLO

app = Flask(__name__)

UPLOAD_FOLDER = 'C:/Users/USER/Desktop/기타 작품/나무 어플/web/static/images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# YOLOv8 모델 로드
model = YOLO('yolov8n.pt')

@app.route('/', methods=['GET'])
def index():
    try:
        data = pd.read_csv('coordinates.csv', encoding='utf-8')
    except UnicodeDecodeError:
        data = pd.read_csv('coordinates.csv', encoding='ISO-8859-1')

    selected_filters = request.args.getlist('filter')
    seoul_map = folium.Map(location=[37.417421437, 126.865121126], zoom_start=12, width='100%', height='800px')

    if selected_filters:
        for _, row in data.iterrows():
            if row['name'] not in selected_filters:
                continue

            file_path = os.path.join(app.root_path, 'static/images', row["image_url"])
            if os.path.exists(file_path):
                with open(file_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                image_tag = f'<img src="data:image/jpeg;base64,{img_data}" style="width:200px;height:auto;" alt="{row["name"]}">'
            else:
                image_tag = f'<p>Image not found: {row["image_url"]}</p>'

            popup_html = f"""
            <h4>{row['name']}</h4>
            {image_tag}
            <p>{row['info']}</p>
            """
            iframe = folium.IFrame(html=popup_html, width=250, height=600)
            popup = folium.Popup(iframe, max_width=250)

            icon_file_path = os.path.join(app.root_path, 'static/icons', row["icon_url"])
            if os.path.exists(icon_file_path):
                with open(icon_file_path, 'rb') as icon_file:
                    icon_data = base64.b64encode(icon_file.read()).decode()
                icon_url = f'data:image/png;base64,{icon_data}'
                icon = folium.CustomIcon(icon_image=icon_url, icon_size=(50, 50))
            else:
                icon = folium.Icon(color='red', icon='info-sign')

            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=popup,
                tooltip=row['name'],
                icon=icon
            ).add_to(seoul_map)
    else:
        for _, row in data.iterrows():
            file_path = os.path.join(app.root_path, 'static/images', row["image_url"])
            if os.path.exists(file_path):
                with open(file_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                image_tag = f'<img src="data:image/jpeg;base64,{img_data}" style="width:200px;height:auto;" alt="{row["name"]}">'
            else:
                image_tag = f'<p>Image not found: {row["image_url"]}</p>'

            popup_html = f"""
            <h4>{row['name']}</h4>
            {image_tag}
            <p>{row['info']}</p>
            """
            iframe = folium.IFrame(html=popup_html, width=250, height=800)
            popup = folium.Popup(iframe, max_width=250)

            icon_file_path = os.path.join(app.root_path, 'static/icons', row["icon_url"])
            if os.path.exists(icon_file_path):
                with open(icon_file_path, 'rb') as icon_file:
                    icon_data = base64.b64encode(icon_file.read()).decode()
                icon_url = f'data:image/png;base64,{icon_data}'
                icon = folium.CustomIcon(icon_image=icon_url, icon_size=(50, 50))
            else:
                icon = folium.Icon(color='red', icon='info-sign')

            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=popup,
                tooltip=row['name'],
                icon=icon
            ).add_to(seoul_map)

    map_html = seoul_map._repr_html_()
    additional_info_list = data.loc[data['icon_url'].isin(selected_filters), 'info'].tolist() if selected_filters else []
    return render_template('map.html', map_html=map_html, additional_info_list=additional_info_list, selected_filters=selected_filters)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400
    
    image = Image.open(file)
    max_size = (800, 800)
    image.thumbnail(max_size)

    # 이미지를 임시 파일로 저장하여 YOLO 모델에 입력
    temp_file_path = os.path.join(UPLOAD_FOLDER, 'temp.jpg')
    image.save(temp_file_path)

    # YOLO 모델을 사용하여 "potted plant" 감지
    results = model(temp_file_path)
    potted_plant_class_id = 58  # COCO 데이터셋 기준 "potted plant"의 클래스 ID

    detected = False
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            if class_id == potted_plant_class_id:
                print(class_id)
                detected = True
                break
        if detected:
            break

    # 감지되지 않으면 파일 업로드 취소
    if not detected:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return jsonify({"error": "No potted plant detected in the image"}), 400

    # 감지된 경우 파일 저장
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(file_path)

    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    if not latitude or not longitude:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return jsonify({"error": "Latitude or Longitude not provided"}), 400

    new_data = pd.DataFrame([{
        "name": "loco",
        "latitude": latitude,
        "longitude": longitude,
        "image_url": filename,
        "icon_url": "a.png",
        "info": "tree"
    }])
    csv_file = 'coordinates.csv'
    if os.path.exists(csv_file):
        new_data.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8')
    else:
        new_data.to_csv(csv_file, mode='w', header=True, index=False, encoding='utf-8')

    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)  # 임시 파일 삭제

    response = {
        "message": "File uploaded successfully",
        "name": "loco",
        "file_path": file_path,
        "latitude": latitude,
        "longitude": longitude,
        "icon": "a.png"
    }
    print(response)
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
