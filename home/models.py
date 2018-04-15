import ntpath
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

def get_video_path(instance, filename):
    return '{0}/{1}/{2}'.format(instance.user.username, get_random_string(length=5), filename)

def validate_video_extension(value):
  import os
  ext = os.path.splitext(value.name)[1]
  valid_extensions = ['.mp4','.avi','.webm','.3gp']
  if not ext in valid_extensions:
    raise ValidationError(u'Please upload a video file!')

class Video(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_video_path,max_length=500,validators=[validate_video_extension])
    image = models.ImageField(upload_to='',max_length=500,null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + ": " + ntpath.basename(self.file.name)

class Comment(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE)
    video = models.ForeignKey(Video,on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + ": " + self.description

@receiver(post_save,sender=Video)
def save_screenshot(sender,instance,created,**kwargs):
    if created:
        from contextlib import closing
        from videosequence import VideoSequence
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import io
        with closing(VideoSequence(instance.file.path)) as frames:
            tempio = io.BytesIO()
            frames[0].save(tempio,format='JPEG')
            memoryfile = InMemoryUploadedFile(tempio,None,'screenshot.jpeg','image/jpeg',0,None)
            instance.image.save(
                instance.file.name+".jpg",
                memoryfile
            )
            instance.save()
