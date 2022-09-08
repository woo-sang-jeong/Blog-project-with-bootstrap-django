# FBV 방식으로 제작할 때 필요 : from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import PostForm
from .models import Post, Category, Tag, Comment
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.shortcuts import get_object_or_404


# Create your views here.

class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context


class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    # model.py의 Post 클라스 모델을 사용한다 선언
    model = Post
    # Post 모델에 사용할 필드명을 리스트로 작성하여 fields 변수에 저장
    # fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']
    form_class = PostForm

    # UserPassesTestMixin을 위한 함수
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    # form_valid는 유효성 검사를 뜻한다.
    def form_valid(self, form):
        # 웹 사이트 방문자 current_user
        current_user = self.request.user
        # 로그인시 form에서 생성한 instance(생성한 포스트)의 author 필드에 current_user를 담는다.
        # form_valid() 함수에 현재의 form을 인자로 보내 처리한다.
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user

            # CreateView의 form_valid() 함수의 결과값을 response 변수에 담아둔다.
            response = super(PostCreate, self).form_valid(form)

            # 1 blog 참조
            tags_str = self.request.POST.get('tags_str')
            # 2
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    # 3
                    t = t.strip()
                    # 4
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    # 5
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    # 6
                    self.object.tags.add(tag)
            # 7
            return response


        # 비로그인시 redirect() 함수에 의해 /blog/ 로 되돌려 보낸다.
        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    # fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']
    form_class = PostForm

    # CBV로 뷰를 만들 때 template_name을 지정해 원하는 html 파일을 템플릿 파일로 설정 할 수 있다.
    template_name = 'blog/post_update_form.html'

    # self.get_object()는 UpdateView의 메서드로 Post.objects.get(pk=pk)와 동일한 역할을 한다.
    # Post 인스터스의 author 필드가 방문자와 동일한 경우 dispatch()가 제 역할을 하게된다.
    # 조건 불만족시 raise PermissionDenied를 실행한다.
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    # post_update_form.html의 tags_str_default에 값을 넘겨주기 위한 함수
    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_create = Tag.objects.get_or_create(name=t)
                if is_tag_create:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


# 어느 class 에 속하지 않은 함수들이다. urls.py와 연결 되어 있다.
def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
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


def tag_page(request, slug):
    # URL에서 인자로 넘어온 slug와 동일한 slug를 가진 태그를 쿼리셋으로 가져와 tag 변수에 저장한다.
    tag = Tag.objects.get(slug=slug)
    # 가져온 태그와 연결된 포스트 전부를 post_list에 저장한다.
    post_list = tag.post_set.all()

    # 쿼리셋으로 가져온 인자들을 render() 함수안에 딕셔너리 형태로 담는다.
    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'tag': tag
        }
    )


def new_comment(request, pk):
    if request.user.is_authenticated:  # 1
        post = get_object_or_404(Post, pk=pk)  # 2

        if request.method == 'POST':  # 3
            comment_form = CommentForm(request.POST)  # 4
            if comment_form.is_valid():  # 5
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())  # 6
        else:  # 3
            return redirect(post.get_absolute_url)
    else:  # 1
        raise PermissionDenied


def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

"""
FBV 방식으로 제작한 함수

def index(request):
    posts = Post.objects.all().order_by('-pk')

    return render(
        request,
        'blog/post_list.html',
        {
            'posts': posts,
        }
    )

def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(
        request,
        'blog/post_detail.html',
        {
            'post' : post,
        }
    )
"""
