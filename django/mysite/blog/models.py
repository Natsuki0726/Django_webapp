from django.db import models
from django.utils import timezone
from django.urls import reverse_lazy

# ジャンルのモデル
class Category(models.Model):
    # カテゴリ名
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    # 登録した時間
    timestamp = models.DateTimeField(auto_now_add=True)
    # adminでの表示方法
    def __str__(self):
        return self.name


# タグのモデル
class Tag(models.Model):
    # タグ名
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    # 登録した時間
    timestamp = models.DateTimeField(auto_now_add=True)

    # adminでの表示名
    def __str__(self):
        return self.name


class Post(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True)
    title = models.CharField(max_length=255)
    singer = models.CharField(max_length=50, default='')
    url = models.URLField(max_length=200, default='', blank=True)
    description = models.TextField()
    image = models.ImageField(
        upload_to='images', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    like = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if self.is_public and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy("blog:index")



# ブログ記事に画像を挿入する
class ContentImage(models.Model):
    # 一つの記事につき,画像は一つ
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    content_image = models.ImageField(upload_to='post_content_images/')


# コメント機能
class Comment(models.Model):
    # 投稿に対してリレーション
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=50)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def approve(self):
        self.approved = True
        self.save()

    def __str__(self):
        return self.text


# 返信機能
class Reply(models.Model):
    # コメントに対してリレーション
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name='replies')
    author = models.CharField(max_length=50)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def approve(self):
        self.approved = True
        self.save()

    def __str__(self):
        return self.text