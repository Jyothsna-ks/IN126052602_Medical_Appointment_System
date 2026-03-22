from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import math

app = FastAPI()

# Day 1 - Basic Setup

@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}


# Sample doctors
doctors = [
    {"id": 1, "name": "Dr. Ashvik Purohit", "specialization": "Cardiologist", "fee": 500, "experience_years": 7, "is_available": True},
    {"id": 2, "name": "Dr. Ruhanika Malhotra", "specialization": "Dermatologist", "fee": 350, "experience_years": 5, "is_available": True},
    {"id": 3, "name": "Dr. Riyanshi Goel", "specialization": "Pediatrician", "fee": 300, "experience_years": 4, "is_available": False},
    {"id": 4, "name": "Dr. Devrath Dixit", "specialization": "Cardiosurgeon", "fee": 650, "experience_years": 10, "is_available": True},
    {"id": 5, "name": "Dr. Sonakshi Kapoor ", "specialization": "Neurosurgeon", "fee": 750, "experience_years": 12, "is_available": True},
    {"id": 6, "name": "Dr. Anil Sharma", "specialization": "General", "fee": 350, "experience_years": 6, "is_available": False},
]

appointments = []
appt_counter = 1

# DAY 3 - Helper Functions

def find_doctor(doctor_id: int):
    for doc in doctors:
        if doc["id"] == doctor_id:
            return doc
    return None


def calculate_fee(base_fee: int, appointment_type: str, senior: bool):
    original_fee = base_fee
    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    else:
        fee = base_fee

    

    if senior:
        fee = fee * 0.85

    return int(original_fee), int(fee)


def filter_doctors_logic(specialization, max_fee, min_exp, is_available):
    result = doctors

    if specialization is not None:
        result = [d for d in result if d["specialization"] == specialization]

    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]

    if min_exp is not None:
        result = [d for d in result if d["experience_years"] >= min_exp]

    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]

    return result

# Day 1 - APIs

@app.get("/doctors")
def get_doctors():
    available = [d for d in doctors if d["is_available"]]
    return {
        "doctors": doctors,
        "total": len(doctors),
        "available_count": len(available)
    }


@app.get("/doctors/summary")
def doctors_summary():
    most_exp = max(doctors, key=lambda d: d["experience_years"])
    cheapest = min(doctors, key=lambda d: d["fee"])

    spec_count = {}
    for d in doctors:
        spec_count[d["specialization"]] = spec_count.get(d["specialization"], 0) + 1

    return {
        "total": len(doctors),
        "available": len([d for d in doctors if d["is_available"]]),
        "most_experienced": most_exp["name"],
        "cheapest_fee": cheapest["fee"],
        "specializations": spec_count
    }

@app.get("/doctors/search")
def search_doctors(keyword: str):
    result = [
        d for d in doctors
        if keyword.lower() in d["name"].lower()
        or keyword.lower() in d["specialization"].lower()
    ]

    if not result:
        return {"message": "No doctors found"}

    return {"results": result, "total_found": len(result)}

# Day 3 - Filter

@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None,
    max_fee: Optional[int] = None,
    min_experience: Optional[int] = None,
    is_available: Optional[bool] = None
):
    result = filter_doctors_logic(specialization, max_fee, min_experience, is_available)
    return {"results": result, "count": len(result)}

# Day 6 - Advanced APIs

@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee"):
    if sort_by not in ["fee", "name", "experience_years"]:
        raise HTTPException(400, "Invalid sort field")

    sorted_list = sorted(doctors, key=lambda d: d[sort_by])
    return {"sorted_by": sort_by, "data": sorted_list}


@app.get("/doctors/page")
def paginate_doctors(page: int = 1, limit: int = 3):
    total = len(doctors)

    # total pages using ceiling
    total_pages = math.ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    data = doctors[start:end]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "data": data
    }


@app.get("/appointments/search")
def search_appt(patient_name: str):
    return [a for a in appointments if patient_name.lower() in a["patient"].lower()]


@app.get("/appointments/sort")
def sort_appt(sort_by: str = "final_fee"):
    return sorted(appointments, key=lambda a: a.get(sort_by, 0))


@app.get("/appointments/page")
def page_appt(page: int = 1, limit: int = 2):
    total = len(appointments)
    total_pages = math.ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "data": appointments[start:end]
    }


@app.get("/doctors/browse")
def browse(
    keyword: Optional[str] = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = doctors

    if keyword:
        result = [
            d for d in result
            if keyword.lower() in d["name"].lower()
            or keyword.lower() in d["specialization"].lower()
        ]

    reverse = order == "desc"
    result = sorted(result, key=lambda d: d[sort_by], reverse=reverse)

    total = len(result)
    total_pages = math.ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "total_pages": total_pages,
        "data": result[start:end]
    }



@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Doctor not found")
    return doc


@app.get("/appointments")
def get_appointments():
    return {"appointments": appointments, "total": len(appointments)}


# Day 2 - Pydantic

class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False


# Day 2 - POST Appointment

@app.post("/appointments")
def create_appointment(req: AppointmentRequest):
    global appt_counter

    doctor = find_doctor(req.doctor_id)
    if not doctor:
        raise HTTPException(404, "Doctor not found")

    if not doctor["is_available"]:
        raise HTTPException(400, "Doctor not available")

    original_fee, final_fee = calculate_fee(
        doctor["fee"],
        req.appointment_type,
        req.senior_citizen
    )

    appointment = {
        "appointment_id": appt_counter,
        "patient": req.patient_name,
        "doctor_id": doctor["id"],
        "doctor": doctor["name"],
        "date": req.date,
        "type": req.appointment_type,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }

    appointments.append(appointment)
    appt_counter += 1
    doctor["is_available"] = False

    return appointment


# Day 4 - CRUD

class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = True


@app.post("/doctors", status_code=201)
def add_doctor(doc: NewDoctor):
    for d in doctors:
        if d["name"] == doc.name:
            raise HTTPException(400, "Doctor already exists")

    new_doc = doc.dict()
    new_doc["id"] = len(doctors) + 1
    doctors.append(new_doc)
    return new_doc


@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    fee: Optional[int] = None,
    is_available: Optional[bool] = None
):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Doctor not found")

    if fee is not None:
        doc["fee"] = fee
    if is_available is not None:
        doc["is_available"] = is_available

    return doc


@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Doctor not found")

    for a in appointments:
        if a["doctor_id"] == doctor_id and a["status"] == "scheduled":
            raise HTTPException(400, "Doctor has active appointments")

    doctors.remove(doc)
    return {"message": "Doctor deleted"}

# Day 5 - Workflow

def find_appointment(aid: int):
    for a in appointments:
        if a["appointment_id"] == aid:
            return a
    return None


@app.post("/appointments/{aid}/confirm")
def confirm(aid: int):
    appt = find_appointment(aid)
    if not appt:
        raise HTTPException(404, "Not found")
    appt["status"] = "confirmed"
    return appt


@app.post("/appointments/{aid}/cancel")
def cancel(aid: int):
    appt = find_appointment(aid)
    if not appt:
        raise HTTPException(404, "Not found")

    appt["status"] = "cancelled"
    doc = find_doctor(appt["doctor_id"])
    if doc:
        doc["is_available"] = True

    return appt


@app.post("/appointments/{aid}/complete")
def complete(aid: int):
    appt = find_appointment(aid)
    if not appt:
        raise HTTPException(404, "Not found")

    appt["status"] = "completed"
    return appt


@app.get("/appointments/active")
def active():
    result = [a for a in appointments if a["status"] in ["scheduled", "confirmed"]]
    return result


@app.get("/appointments/by-doctor/{doctor_id}")
def by_doc(doctor_id: int):
    return [a for a in appointments if a["doctor_id"] == doctor_id]


