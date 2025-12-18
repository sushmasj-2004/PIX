from django.core.management.base import BaseCommand
from faceapp.models import User
from PIL import Image
import numpy as np
import json

try:
    from deepface import DeepFace
    HAS_DEEPFACE = True
except Exception:
    HAS_DEEPFACE = False


class Command(BaseCommand):
    help = "Recompute face embeddings for all users from their photo files"

    def handle(self, *args, **options):
        if not HAS_DEEPFACE:
            self.stdout.write(self.style.ERROR('DeepFace not installed'))
            return

        users = User.objects.all()
        for u in users:
            if not u.photo:
                self.stdout.write(f"skip {u.id} no photo")
                continue
            try:
                img = Image.open(u.photo.path).convert('RGB')
                frame = np.array(img)[:, :, ::-1]
                rep = DeepFace.represent(frame, model_name='Facenet', enforce_detection=False)
                if rep and isinstance(rep, list) and 'embedding' in rep[0]:
                    u.embedding = json.dumps(rep[0]['embedding'])
                    u.save(update_fields=['embedding'])
                    self.stdout.write(f"updated {u.id} {u.email}")
                else:
                    self.stdout.write(f"no embedding for {u.id}")
            except Exception as e:
                self.stdout.write(f"error for {u.id}: {e}")
