# faceapp/utils.py
import os
import csv
from django.conf import settings
from .models import User, Attendance

EXPORT_DIR = os.path.join(settings.BASE_DIR, 'exports')
USERS_CSV = os.path.join(EXPORT_DIR, 'users.csv')
ATTENDANCE_CSV = os.path.join(EXPORT_DIR, 'attendance.csv')

def ensure_csv_files():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    # users.csv
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Name', 'Email', 'Department', 'Created At'])
    # attendance.csv
    if not os.path.exists(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Name', 'Email', 'Department', 'Timestamp'])

def update_users_csv():
    ensure_csv_files()
    with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Name', 'Email', 'Department', 'Created At'])
        for u in User.objects.select_related('department').all():
            w.writerow([
                u.name,
                u.email,
                u.department.department_name if u.department else '',
                u.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

def add_attendance_to_csv(user, timestamp):
    ensure_csv_files()
    with open(ATTENDANCE_CSV, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            user.name,
            user.email,
            user.department.department_name if user.department else '',
            timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])
