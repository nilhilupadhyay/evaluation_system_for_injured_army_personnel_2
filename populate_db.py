import csv
from app import db, ImpactHealth, app

def read_data_from_csv(file_path):
    data_list = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            if len(row) == 10:
                data_list.append(row)
            else:
                print(f"Ignoring row {row}: Number of columns is not equal to 10")
    return data_list

def insert_data_into_db(data):
    with app.app_context():
        db.create_all()  # Ensure all tables are created
        for record in data:
            try:
                new_record = ImpactHealth(
                    bullet_velocity=float(record[0]),
                    human_body_mass=float(record[1]),
                    kinetic_energy=float(record[2]),
                    temperature_rise=float(record[3]),
                    blood_loss=int(record[4]),
                    ecg_readings=record[5],
                    health_status=record[6],
                    latitude=float(record[7]),
                    longitude=float(record[8]),
                    diagnosis_result=record[9]
                )
                db.session.add(new_record)
            except ValueError as e:
                print(f"Ignoring row {record}: {e}")
        db.session.commit()
        print(f"Inserted {len(data)} records into the database.")

def populate_db():
    file_path = 'bullet_impact_data.csv'  # Ensure this is the correct path to your CSV file
    data = read_data_from_csv(file_path)
    insert_data_into_db(data)

if __name__ == "__main__":
    populate_db()
