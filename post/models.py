from django.db import models

from users.models import CustomUser
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user =models.OneToOneField(CustomUser ,on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    image= models.ImageField(upload_to="media/", blank=True, null=True)
    create_at =models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"@{self.user.username}"


class Post(models.Model):
    user =models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="posts")
    image =models.ImageField(upload_to='posts/')
    caption =models.TextField(blank=True)
    create_at =models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post {self.pk} @{self.user.username}"


class PostLike(models.Model):
    post =models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"@{self.user.username} liked Post {self.post.pk}"


class Comment(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE,null=True, blank=True, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" @{self.user.username} shu foydalanuvchi  #{self.post.pk} potga izoh bildirdi"


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f"@{self.user.username} singning #{self.comment.pk} cammentingizga yoqtirdi"


class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"@{self.follower.username} → @{self.following.username}"


def story_expiration():
    return timezone.now() + timedelta(hours=24)


class Story(models.Model):
    user= models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='stories')
    image= models.ImageField(upload_to='stories/images/', blank=True, null=True)
    video= models.FileField(upload_to='stories/videos/', blank=True, null=True)
    text= models.CharField(max_length=500, blank=True)
    expires_at = models.DateTimeField(default=story_expiration)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.pk} by @{self.user.username}"


class StoryLike(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='story_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'user')

    def __str__(self):
        return f"@{self.user.username} liked Story  {self.story.pk}"


class StoryComment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='story_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"@{self.user.username} commented on Story #{self.story.pk}"
