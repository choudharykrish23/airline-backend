from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="airline_management"
    )

@app.route('/')
def home():
    return jsonify({"message": "AirManage API is running!"})

@app.route('/flights')
def get_flights():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.Flight_id, f.Flight_number, al.Name AS Airline,
               dep.City AS From_city, dep.Airport_code AS From_code,
               arr.City AS To_city, arr.Airport_code AS To_code,
               f.Departure_time, f.Arrival_time, f.Duration,
               f.Available_seats, f.Price
        FROM FLIGHT f
        JOIN AIRLINE al ON f.Airline_id = al.Airline_id
        JOIN AIRPORT dep ON f.Departure_airport = dep.Airport_code
        JOIN AIRPORT arr ON f.Arrival_airport = arr.Airport_code
    """)
    flights = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(flights)

@app.route('/flights/<from_code>/<to_code>')
def search_flights(from_code, to_code):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.Flight_id, f.Flight_number, al.Name AS Airline,
               dep.City AS From_city, dep.Airport_code AS From_code,
               arr.City AS To_city, arr.Airport_code AS To_code,
               f.Departure_time, f.Arrival_time, f.Duration,
               f.Available_seats, f.Price
        FROM FLIGHT f
        JOIN AIRLINE al ON f.Airline_id = al.Airline_id
        JOIN AIRPORT dep ON f.Departure_airport = dep.Airport_code
        JOIN AIRPORT arr ON f.Arrival_airport = arr.Airport_code
        WHERE dep.Airport_code = %s AND arr.Airport_code = %s
    """, (from_code.upper(), to_code.upper()))
    flights = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(flights)

@app.route('/bookings')
def get_bookings():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.Booking_ID, b.Seat_number, b.Class, b.Status,
               b.Booking_date,
               CONCAT(p.First_name,' ',p.Last_name) AS Passenger,
               f.Flight_number, al.Name AS Airline,
               dep.City AS From_city, arr.City AS To_city,
               pay.Amount, pay.Payment_method, pay.Payment_status
        FROM BOOKING b
        JOIN PASSENGER p ON b.Passenger_ID = p.Passenger_ID
        JOIN FLIGHT f ON b.Flight_ID = f.Flight_id
        JOIN AIRLINE al ON f.Airline_id = al.Airline_id
        JOIN AIRPORT dep ON f.Departure_airport = dep.Airport_code
        JOIN AIRPORT arr ON f.Arrival_airport = arr.Airport_code
        JOIN PAYMENT pay ON b.Booking_ID = pay.Booking_ID
    """)
    bookings = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(bookings)

@app.route('/admin/stats')
def get_stats():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total_flights FROM FLIGHT")
    flights = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS total_passengers FROM PASSENGER")
    passengers = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS total_bookings FROM BOOKING")
    bookings = cursor.fetchone()
    cursor.execute("SELECT SUM(Amount) AS total_revenue FROM PAYMENT WHERE Payment_status='Success'")
    revenue = cursor.fetchone()
    cursor.close()
    db.close()
    return jsonify({
        "total_flights": flights["total_flights"],
        "total_passengers": passengers["total_passengers"],
        "total_bookings": bookings["total_bookings"],
        "total_revenue": float(revenue["total_revenue"] or 0)
    })

if __name__ == '__main__':
    app.run(debug=True)