import os.path

from django.contrib.auth.models import User
from django.db import models
from markdownx.utils import markdown
from markdownx.models import MarkdownxField

class Board(models.Model):
    name = models.CharField(max_length=50, unique=True)  # 게시판 이름
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)  # 게시판 URL에 사용
    description = models.TextField(blank=True)  # 게시판 설명
    created_at = models.DateTimeField(auto_now_add=True)  # 생성일

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/board/{self.slug}/'

class Tag(models.Model):
    name = models.CharField(max_length = 50, unique = True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    board = models.ForeignKey('Board', null=True, blank=True, on_delete=models.CASCADE)  # 게시판 연결

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length = 50, unique = True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    board = models.ForeignKey('Board', null=True, blank=True, on_delete=models.CASCADE)  # 게시판 연결

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'
    class Meta:
        verbose_name_plural = 'Categories'

class Post(models.Model):
    objects = None
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)

    content = MarkdownxField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User,null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)

    board = models.ForeignKey('Board', null=True, blank=True, on_delete=models.CASCADE)  # null=True로 설정

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return f'[{self.pk}] {self.title} :: {self.author}'

    def get_absolute_url(self):
        # 게시판에 연결된 경우 게시판 URL 반환
        if self.board:
            return f'/blog/board/{self.board.slug}/{self.pk}/'
        # Blog URL 반환
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

    def get_content_markdown(self):
        return markdown(self.content)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT8BgtXlULdjwe_uDYrlTxOTv8V998gp7n7Pg&s'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'{self.author}::{self.content}'
    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT8BgtXlULdjwe_uDYrlTxOTv8V998gp7n7Pg&s'
