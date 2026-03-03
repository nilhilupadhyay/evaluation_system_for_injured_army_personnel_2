from flask import Flask, render_template, request, redirect, url_for
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import joblib
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import os


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projectdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

with app.app_context():
    db.create_all()


class ImpactHealth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bullet_velocity = db.Column(db.Float, nullable=False)
    human_body_mass = db.Column(db.Float, nullable=False)
    kinetic_energy = db.Column(db.Float, nullable=False)
    temperature_rise = db.Column(db.Float, nullable=False)
    blood_loss = db.Column(db.Float, nullable=False)
    ecg_readings = db.Column(db.String(100), nullable=False)
    health_status = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    diagnosis_result = db.Column(db.String(100), nullable=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'knn_model.joblib')

if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    raise FileNotFoundError(f"Model file '{model_path}' not found. Please train the model first.")


def predict_health_status(bullet_velocity, human_body_mass, kinetic_energy, temperature_rise, blood_loss, ecg_readings):
    ecg_readings = 0 if ecg_readings == 'Abnormal' else 1
    features = np.array([[bullet_velocity, human_body_mass, kinetic_energy, temperature_rise, blood_loss, ecg_readings]])
    prediction = model.predict(features)
    health_status_mapping = {0: 'Healthy', 1: 'Injured', 2: 'Critical'}
    return health_status_mapping.get(prediction[0], "Unknown")


def scrape_hospital_contact_details(hospitals):
    for hospital in hospitals:
        if hospital['name'] != 'N/A':
            hospital_name = hospital['name']
            search_query = f"{hospital_name} hospital contact details"
            search_url = f"https://www.google.com/search?q={search_query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            try:
                response = requests.get(search_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                email = 'Not found'
                mobile = 'Not found'
                for link in soup.find_all('a', href=True):
                    if 'mailto:' in link['href']:
                        email = link['href'].replace('mailto:', '')
                    if 'tel:' in link['href']:
                        mobile = link['href'].replace('tel:', '')
                hospital['email'] = email
                hospital['mobile'] = mobile
            except Exception as e:
                print(f"Error fetching details for {hospital_name}: {str(e)}")


def get_nearby_hospitals(location, radius=5000, limit=15):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{location[0]},{location[1]});
      way["amenity"="hospital"](around:{radius},{location[0]},{location[1]});
      relation["amenity"="hospital"](around:{radius},{location[0]},{location[1]});
    );
    out body;
    >;
    out skel qt;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    hospitals = []
    count = 0
    for element in data['elements']:
        if count >= limit:
            break
        if element['type'] == 'node':
            hospital = {
                'name': element.get('tags', {}).get('name', 'N/A'),
                'address': element.get('tags', {}).get('address', 'N/A'),
                'location': {
                    'lat': element['lat'],
                    'lon': element['lon']
                }
            }
            hospitals.append(hospital)
            count += 1
        elif element['type'] in ['way', 'relation']:
            for member in element.get('members', []):
                if member['type'] == 'node':
                    node_id = member['ref']
                    node = next((item for item in data['elements'] if item['id'] == node_id and item['type'] == 'node'), None)
                    if node:
                        hospital = {
                            'name': node.get('tags', {}).get('name', 'N/A'),
                            'address': node.get('tags', {}).get('address', 'N/A'),
                            'location': {
                                'lat': node['lat'],
                                'lon': node['lon']
                            }
                        }
                        hospitals.append(hospital)
                        count += 1
    return hospitals[:limit]


def send_email(sender_email, sender_password, recipient_emails, body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_emails)
    msg['Subject'] = "Health Status Update"
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_emails, msg.as_string())
    server.quit()


@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    health_status = ""
    nearby_hospitals = []
    record_id = None
    
    if request.method == 'POST':
        bullet_velocity = float(request.form.get('bullet_velocity'))
        human_body_mass = float(request.form.get('human_body_mass'))
        kinetic_energy = float(request.form.get('kinetic_energy'))
        temperature_rise = float(request.form.get('temperature_rise'))
        blood_loss = float(request.form.get('blood_loss'))
        ecg_readings = request.form.get('ecg_readings')
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')
        
        print(f"Received form data: bullet_velocity={bullet_velocity}, human_body_mass={human_body_mass}, kinetic_energy={kinetic_energy}, temperature_rise={temperature_rise}, blood_loss={blood_loss}, ecg_readings={ecg_readings}, lat={lat}, lng={lng}")

        try:
            
            health_status = predict_health_status(bullet_velocity, human_body_mass, kinetic_energy, temperature_rise, blood_loss, ecg_readings)
            
            
            
            new_record = ImpactHealth(
                bullet_velocity=bullet_velocity,
                human_body_mass=human_body_mass,
                kinetic_energy=kinetic_energy,
                temperature_rise=temperature_rise,
                blood_loss=blood_loss,
                ecg_readings=ecg_readings,
                health_status=health_status,
                latitude=lat,
                longitude=lng
            )
            
            
            db.session.add(new_record)
            db.session.commit()
            
            record_id = new_record.id
            message = "Record inserted successfully"
            
            
            if lat and lng:
                nearby_hospitals = get_nearby_hospitals((lat, lng))
                scrape_hospital_contact_details(nearby_hospitals)
            
            
            sender_email = "nikhilupadhyayin@gmail.com"  
            sender_email = os.environ.get("EMAIL_USER")
            sender_password = os.environ.get("EMAIL_PASS")
            #recipient_email = "nikhil2020upadhyay@gmail.com" 


            recipient_emails = []
            recipients_path = os.path.join(BASE_DIR, 'recipients.csv')
            with open(recipients_path, mode='r') as file:
                csv_reader = pd.read_csv(file)
                recipient_emails = csv_reader['email'].tolist()

            
            
            #msg = MIMEMultipart()
            #msg['From'] = sender_email
            #msg['To'] = recipient_email
            #msg['Subject'] = "Health Status Update"
            
            body = (
                f"Health Status: {health_status}\n "
                f"Bullet Velocity: {bullet_velocity}\n"
                f"Human Body Mass: {human_body_mass}\n"
                f"Kinetic Energy: {kinetic_energy}\n "
                f"Temperature Rise: {temperature_rise}\n "
                f"Blood Loss: {blood_loss}\n"
                f"ECG Readings: {ecg_readings}\n"
                f"Health Status: {health_status}\n "
                f"Latitude: {lat}\n "
                f"Longitude: {lng}\n"
                f"email_detail: nikhilupadhyayin@gmail.com"
            )
            send_email(sender_email, sender_password, recipient_emails, body)

            #msg.attach(MIMEText(body, 'plain'))
            
            
            #server = smtplib.SMTP('smtp.gmail.com', 587)
            #server.starttls()
            #server.login(sender_email, sender_password)
            #server.sendmail(sender_email, recipient_email, msg.as_string())
            #server.quit()
            
            print("Email sent successfully")
            
            
            return render_template('hospital.html', message=message, health_status=health_status, nearby_hospitals=nearby_hospitals, record_id=record_id)
        
        except Exception as e:
            message = f"Error: {str(e)}"
            print(message)
    
    return render_template('index.html', message=message, health_status=health_status, nearby_hospitals=nearby_hospitals, record_id=record_id)

@app.route('/hospitals', methods=['GET'])
def hospital_list():
    message = ""
    health_status = ""
    nearby_hospitals = []
    record_id = None
    lat = request.args.get('latitude')
    lng = request.args.get('longitude')
    
    if lat and lng:
        nearby_hospitals = get_nearby_hospitals((lat, lng))
        scrape_hospital_contact_details(nearby_hospitals)
    
    return render_template('hospital.html', message=message, health_status=health_status, nearby_hospitals=nearby_hospitals, record_id=record_id)

@app.route('/diagnosis/<int:id>', methods=['GET', 'POST'])
def diagnosis(id):
    record = ImpactHealth.query.get_or_404(id)
    message = ""

    if request.method == 'POST':
        diagnosis_result = request.form.get('diagnosis_result')
        record.diagnosis_result = diagnosis_result
        try:
            db.session.commit()
            message = "Diagnosis updated successfully"
        except Exception as e:
            db.session.rollback()
            message = f"Error: {str(e)}"

    return render_template('diagnosis.html', record=record, message=message)


   

