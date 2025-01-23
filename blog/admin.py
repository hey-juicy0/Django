from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Post,Category,Tag,Comment,Board

# Register your models here.
admin.site.register(Post, MarkdownxModelAdmin)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment)

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}  # name 기반으로 slug 자동 생성

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 게시판 생성 시 기본 데이터 추가
        if not change:  # 새로 생성된 경우
            # 기본 게시물 생성
            Post.objects.create(
                title=f'{obj.name} 게시판이 새로 생성되었습니다!',
                content=f'{obj.name} 게시판이 새로 생성되었습니다. \n많은 이용 부탁드립니다.',
                category= obj.name,
                author=request.user,  # 현재 관리자를 기본 작성자로 설정
            )
