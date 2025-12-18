# faceapp/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_employees = models.IntegerField(default=0)

    def __str__(self):
        return self.department_name


class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    embedding = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    password = models.CharField(max_length=255, default="")
    is_admin = models.BooleanField(default=False)

    def set_password(self, raw):
        self.password = make_password(raw)

    def check_password(self, raw):
        if not self.password:
            return False
        return check_password(raw, self.password)

    def __str__(self):
        return f"{self.name} ({'Admin' if self.is_admin else 'Employee'})"

    class Meta:
        verbose_name = "Face App User"
        verbose_name_plural = "Face App Users"

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)

        # Auto-generate embedding only if photo exists
        if self.photo and (creating or not self.embedding):
            try:
                from deepface import DeepFace
                import numpy as np, json
                from PIL import Image

                img = Image.open(self.photo.path).convert("RGB")
                frame = np.array(img)[:, :, ::-1]

                rep = DeepFace.represent(
                    frame,
                    model_name='Facenet',
                    enforce_detection=False
                )

                if rep and "embedding" in rep[0]:
                    self.embedding = json.dumps(rep[0]['embedding'])
                    super().save(update_fields=["embedding"])
                else:
                    print("❌ DeepFace returned no embedding")

            except Exception as e:
                print("❌ Embedding creation failed:", e)


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)  # daily record
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    working_hours = models.FloatField(null=True, blank=True)  # in hours    from faceapp.models import User
    # Do not access the DB at import time (avoids startup warnings and errors).
    # If you need diagnostics, run a management command or log inside views/ready().

    def calculate_working_hours(self):
        if self.login_time and self.logout_time:
            delta = self.logout_time - self.login_time
            self.working_hours = round(delta.total_seconds() / 3600, 2)
            self.save()

    def __str__(self):
        name = self.user.name if self.user else "Unknown"
        return f"{name} | {self.date}"


class APIToken(models.Model):
    """
    Optional server-side token store. Saves issued JWTs so they can be
    revoked or audited. Storing tokens in the DB is useful for logout
    / revocation, short-lived refresh tokens, and administration.
    """
    key = models.CharField(max_length=512, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked = models.BooleanField(default=False)

    def is_valid(self):
        if self.revoked:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

    def __str__(self):
        return f"APIToken(user={self.user.email}, revoked={self.revoked})"
