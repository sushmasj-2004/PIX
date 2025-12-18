# faceapp/views.py
import json, io, base64, os
from datetime import date
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from PIL import Image
import numpy as np
import cv2
import datetime

from .auth import create_token, ACCESS_TOKEN_HOURS
from .models import User, Attendance, Department, APIToken


def home(request):
    return HttpResponse("Face Attendance Backend. Use /api/... endpoints")

# ---------------------------
# Departments (public)
# ---------------------------
def get_departments(request):
    qs = Department.objects.all().values("department_id", "department_name", "location", "total_employees")
    return JsonResponse(list(qs), safe=False)
@csrf_exempt
def add_department(request):
    # Example: you might want to protect this in the future (admin only)
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        name = data.get("name")
        location = data.get("location", "")
        if not name:
            return JsonResponse({"error": "Name required"}, status=400)
        dept = Department.objects.create(department_name=name, location=location)
        return JsonResponse({"message": "Department created", "department_id": dept.department_id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# DeepFace optional
try:
    from deepface import DeepFace
    HAS_DEEPFACE = True
except Exception:
    HAS_DEEPFACE = False


# ---------------------------
# Register User (public)
# ---------------------------
@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=400)
    try:
        # support multipart/form-data with a file upload or JSON without photo
        name = request.POST.get('name') or request.POST.get('full_name')
        email = request.POST.get('email') or request.POST.get('username')
        dept_id = request.POST.get('department')
        photo = request.FILES.get('photo')
        password = request.POST.get('password')

        # fallback to JSON body if not form-encoded
        if not (name and email):
            try:
                data = json.loads(request.body.decode('utf-8'))
                name = name or data.get('name')
                email = email or data.get('email')
                dept_id = dept_id or data.get('department')
                password = password or data.get('password')
                # photo via API is not supported in JSON here (use multipart upload)
            except Exception:
                pass

        if not all([name, email]):
            return JsonResponse({"error": "Name and email required"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "User with this email already exists"}, status=400)

        department = None
        if dept_id:
            try:
                department = Department.objects.get(department_id=dept_id)
            except Department.DoesNotExist:
                return JsonResponse({"error": "Invalid department id"}, status=400)

        user = User(name=name, email=email, department=department)
        if photo:
            user.photo = photo

        if password:
            user.set_password(password)
        else:
            # default password if not provided
            user.set_password(email.split("@")[0] + "123")

        user.save()

        # Create embedding if photo saved
        if HAS_DEEPFACE and getattr(user, 'photo', None):
            try:
                img_path = os.path.join(settings.MEDIA_ROOT, str(user.photo))
                rep = DeepFace.represent(img_path=img_path, model_name='Facenet', enforce_detection=False)
                if rep and isinstance(rep, list) and "embedding" in rep[0]:
                    user.embedding = json.dumps(rep[0]["embedding"])
                    user.save(update_fields=['embedding'])
            except Exception as e:
                print('Embedding creation failed:', e)

        return JsonResponse({"message": "User registered successfully"}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ---------------------------
# Login -> returns JWT (email + password)
# ---------------------------
@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "email and password required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        if not user.check_password(password):
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        token = create_token(user)

        # Persist token server-side so it can be revoked/audited (Postgres)
        try:
            expires = timezone.now() + datetime.timedelta(hours=ACCESS_TOKEN_HOURS)
            APIToken.objects.create(key=token, user=user, expires_at=expires)
        except Exception as e:
            # do not fail login if DB logging of token fails, but log for debug
            print("Warning: could not persist APIToken:", e)

        return JsonResponse({
            "status": "success",
            "token": token,
            "user": {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "is_admin": user.is_admin,
            },
            # Backwards-compatible top-level fields expected by the frontend
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin,
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------
# Face Recognition Helper
# ---------------------------
def recognize_face_from_frame(frame):
    try:
        rep = DeepFace.represent(frame, model_name='Facenet', enforce_detection=False)

        if not rep or not isinstance(rep, list) or "embedding" not in rep[0]:
            return None, None

        uploaded_emb = np.array(rep[0]["embedding"], dtype=float)
        if uploaded_emb.size == 0 or not np.isfinite(uploaded_emb).all():
            return None, None
        uploaded_norm = np.linalg.norm(uploaded_emb)
        if uploaded_norm == 0:
            return None, None
        uploaded_emb = uploaded_emb / uploaded_norm

        candidates = []

        for u in User.objects.exclude(embedding=None).exclude(embedding=""):
            try:
                stored_arr = np.array(json.loads(u.embedding), dtype=float)
                if stored_arr.shape != uploaded_emb.shape:
                    continue
                if not np.isfinite(stored_arr).all():
                    continue
                stored_norm = np.linalg.norm(stored_arr)
                if stored_norm == 0:
                    continue
                stored_emb = stored_arr / stored_norm
                dist = float(np.linalg.norm(stored_emb - uploaded_emb))
                candidates.append((u, dist))
            except Exception:
                continue

        if not candidates:
            return None, None

        candidates.sort(key=lambda x: x[1])
        # log top candidates for debugging
        top = [(c[0].id, c[0].name, c[1]) for c in candidates[:5]]
        print("Recognition candidates (id,name,dist):", top)

        best, min_dist = candidates[0]
        return best, min_dist

    except Exception as e:
        print("DeepFace error:", e)
        return None, None


# ---------------------------
# Start Attendance (PROTECTED)
# ---------------------------
@csrf_exempt
def start_attendance(request):
    # ensure user authenticated by middleware
    if not getattr(request, "user", None):
        return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)
    if not HAS_DEEPFACE:
        return JsonResponse({"status": "error", "message": "DeepFace not installed"}, status=501)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        image_data = payload.get('image')

        if not image_data:
            return JsonResponse({"status": "error", "message": "No image data provided"}, status=400)

        # decode base64
        if ',' in image_data:
            image_data = image_data.split(',', 1)[1]

        image_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        frame = np.array(img)[:, :, ::-1]

        user, distance = recognize_face_from_frame(frame)
        print("DISTANCE:", distance)

        if not user or distance is None:
            return JsonResponse({"status": "failed", "message": "Face not recognised"})

        if distance > 1.10:
            return JsonResponse({"status": "failed", "message": "Face not recognised", "distance": float(distance)})

        today = timezone.localdate()
        record, created = Attendance.objects.get_or_create(user=user, date=today)
        now = timezone.now()

        if not record.login_time:
            record.login_time = now
            record.save()
            return JsonResponse({"status": "success", "action": "login", "message": f"Login recorded for {user.name}", "name": user.name})
        else:
            record.logout_time = now
            record.calculate_working_hours()
            return JsonResponse({"status": "success", "action": "logout", "message": f"Logout recorded for {user.name}", "working_hours": record.working_hours, "name": user.name})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ---------------------------
# Verify Face (PROTECTED)
# ---------------------------
@csrf_exempt
def verify_face(request):
    if not getattr(request, "user", None):
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)
    if not HAS_DEEPFACE:
        return JsonResponse({"error": "DeepFace not installed"}, status=501)

    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get("email")
        image_data = data.get("image")

        if not email or not image_data:
            return JsonResponse({"error": "email and image required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        if not user.embedding:
            return JsonResponse({"error": "User has no embedding saved"}, status=400)

        if ',' in image_data:
            image_data = image_data.split(",", 1)[1]

        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        frame = np.array(img)[:, :, ::-1]

        rep = DeepFace.represent(frame, model_name='Facenet', enforce_detection=False)
        if not rep or not isinstance(rep, list) or 'embedding' not in rep[0]:
            return JsonResponse({"error": "Could not compute embedding from image"}, status=400)

        uploaded_emb = np.array(rep[0]['embedding'], dtype=float)
        if uploaded_emb.size == 0 or not np.isfinite(uploaded_emb).all():
            return JsonResponse({"error": "Invalid uploaded embedding"}, status=400)
        uploaded_norm = np.linalg.norm(uploaded_emb)
        if uploaded_norm == 0:
            return JsonResponse({"error": "Invalid uploaded embedding"}, status=400)
        uploaded_emb = uploaded_emb / uploaded_norm

        stored_arr = np.array(json.loads(user.embedding), dtype=float)
        if stored_arr.shape != uploaded_emb.shape:
            return JsonResponse({"error": "Embedding dimension mismatch"}, status=400)
        if not np.isfinite(stored_arr).all():
            return JsonResponse({"error": "Stored embedding invalid"}, status=400)
        stored_emb = stored_arr / np.linalg.norm(stored_arr)

        distance = float(np.linalg.norm(stored_emb - uploaded_emb))
        match = distance < 1.10

        return JsonResponse({"match": match, "distance": distance})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------
# Who Am I (PROTECTED)
# ---------------------------
@csrf_exempt
def whoami(request):
    if not getattr(request, "user", None):
        return JsonResponse({"status": "error", "message": "Not authenticated"}, status=401)

    user = request.user
    return JsonResponse({
        "status": "success",
        "user": {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin,
        }
    })


# ---------------------------
# Logout (Stateless)
# ---------------------------
@csrf_exempt
def logout_api(request):
    try:
        request.session.flush()
    except:
        pass
    # Also revoke API token if provided in Authorization header
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if auth.startswith("Bearer "):
        key = auth.split(None, 1)[1]
        try:
            t = APIToken.objects.filter(key=key).first()
            if t:
                t.revoked = True
                t.save(update_fields=["revoked"])
        except Exception:
            pass

    return JsonResponse({"status": "success", "message": "Logged out"})


@csrf_exempt
def session_login(request):
    """Create a Django session by authenticating against Django's auth.User.

    POST JSON: { "username": "admin", "password": "..." }
    On success this sets the session cookie so the browser can access /admin/.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return JsonResponse({"error": "username and password required"}, status=400)

        from django.contrib.auth import authenticate, login

        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        # login creates the session cookie
        login(request, user)
        return JsonResponse({"status": "success", "message": "Session created"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def start_attendance_file(request):
    if not getattr(request, "user", None):
        return JsonResponse({"status": "error", "message": "Authentication required"}, status=401)
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)
    if not HAS_DEEPFACE:
        return JsonResponse({"status": "error", "message": "DeepFace not installed"}, status=501)

    f = request.FILES.get('image')
    if not f:
        return JsonResponse({"status": "error", "message": "No file uploaded"}, status=400)

    try:
        img = Image.open(f).convert('RGB')
        frame = np.array(img)[:, :, ::-1]
        user, distance = recognize_face_from_frame(frame)

        if not user or distance is None:
            return JsonResponse({"status": "failed", "message": "Face not recognised"})

        if distance > 1.10:
            return JsonResponse({"status": "failed", "message": "Face not recognised", "distance": float(distance)})

        today = timezone.localdate()
        record, created = Attendance.objects.get_or_create(user=user, date=today)
        now = timezone.now()

        if not record.login_time:
            record.login_time = now
            record.save()
            return JsonResponse({"status": "success", "action": "login", "message": f"Login recorded for {user.name}", "name": user.name})
        else:
            record.logout_time = now
            record.calculate_working_hours()
            return JsonResponse({"status": "success", "action": "logout", "message": f"Logout recorded for {user.name}", "working_hours": record.working_hours, "name": user.name})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)