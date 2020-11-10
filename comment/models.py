from django.db import models
from django.contrib.auth.models import User
from article.models import ArticlePost

# Create your models here.
#富文本
from ckeditor.fields import RichTextField

#博主的评论
class Comment(models.Model):

    article = models.ForeignKey(
        ArticlePost,on_delete=models.CASCADE,related_name="comments"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    body = RichTextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return self.body[:20]




