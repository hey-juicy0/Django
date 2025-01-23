from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .forms import CommentForm
from .models import Post, Category, Tag, Comment, Board
from django.utils.text import slugify


# 댓글 삭제
def delete_comment(request, slug=None, pk=None):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    # 게시판 검증
    if slug:
        board = get_object_or_404(Board, slug=slug)
        if post.board != board:
            raise PermissionDenied

    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied


# 댓글 작성
def new_comment(request, slug=None, pk=None):
    if request.user.is_authenticated:
        board = None
        if slug:
            board = get_object_or_404(Board, slug=slug)
        post = get_object_or_404(Post, pk=pk, board=board)
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(post.get_absolute_url())
            else:
                return redirect(post.get_absolute_url())
        else:
            raise PermissionDenied


# 댓글 수정
class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


# 게시글 작성
class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        board_slug = self.kwargs.get('slug', None)
        if board_slug:
            board = get_object_or_404(Board, slug=board_slug)
            form.instance.board = board
        form.instance.author = self.request.user
        return super().form_valid(form)


# 게시글 수정
class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']
    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list(tag.name for tag in self.object.tags.all())
            context['tag_str_default'] = ';'.join(tags_str_list)
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_list = tags_str.strip().replace(',', ';').split(';')
            for tag_name in tags_list:
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                if created:
                    tag.slug = slugify(tag.name, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response


# 게시글 목록
class PostList(ListView):
    model = Post
    ordering = '-pk'
    paginate_by = 5

    def get_queryset(self):
        # 블로그 글만 반환 (board=None)
        return Post.objects.filter(board__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 블로그 카테고리만 전달
        context['categories'] = Category.objects.filter(post__board__isnull=True).distinct()
        # 미분류 게시글 수
        context['no_category_post_count'] = Post.objects.filter(board__isnull=True, category=None).count()
        # 블로그는 board가 없음
        context['board'] = None
        return context


# 게시글 상세
class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['board'] = post.board
        context['categories'] = Category.objects.all()
        context['comment_form'] = CommentForm()
        return context


# 블로그 검색
class PostSearch(PostList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        return Post.objects.filter(Q(title__icontains=q) | Q(tags__name__icontains=q)).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_info'] = f'Search: {self.kwargs["q"]} ({self.get_queryset().count()})'
        return context


# 게시판 검색
class BoardPostSearch(PostList):
    def get_queryset(self):
        q = self.kwargs['q']
        board_slug = self.kwargs['slug']
        board = get_object_or_404(Board, slug=board_slug)
        return Post.objects.filter(Q(title__icontains=q) | Q(tags__name__icontains=q), board=board).distinct()


# 카테고리 페이지
def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = get_object_or_404(Category, slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
        }
    )


# 태그 페이지
def tag_page(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )


# 게시판 페이지
class BoardPostList(ListView):
    model = Post
    template_name = 'blog/board_table.html'  # 게시판 전용 템플릿
    context_object_name = 'posts'
    paginate_by = 5
    ordering = '-pk'

    def get_queryset(self):
        # 게시판 글만 반환
        board_slug = self.kwargs.get('slug')
        board = get_object_or_404(Board, slug=board_slug)
        return Post.objects.filter(board=board)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 현재 게시판 정보
        board_slug = self.kwargs.get('slug')
        board = get_object_or_404(Board, slug=board_slug)
        context['board'] = board
        # 해당 게시판의 카테고리만 전달
        context['categories'] = Category.objects.filter(post__board=board).distinct()
        return context


def delete_post(request, slug, pk):
    board = get_object_or_404(Board, slug=slug) if slug else None
    post = get_object_or_404(Post, pk=pk, board=board)

    if request.user.is_authenticated and request.user == post.author:
        post.delete()
        if board:
            return redirect('board_page', slug=slug)
        return redirect('post_list')  # /blog로 이동
    else:
        raise PermissionDenied
