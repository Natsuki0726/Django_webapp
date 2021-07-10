from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, FormView

from .forms import CommentForm, ReplyForm, SignUpForm, ContactForm
from .models import Post, Category, Tag, Comment, Reply
from django.urls import reverse_lazy


# 個々のブログ記事のView
class PostDetailView(DetailView):
    # Postモデルを表示する
    model = Post

    # 公開されおらず、ユーザログインしていない場合はError
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_public and not self.request.user.is_authenticated:
            raise Http404
        return obj


# 記事の一覧View
class IndexView(ListView):
    # Postモデルを表示する
    model = Post
    # テンプレート名
    template_name = 'blog/index.html'
    paginate_by = 3


# カテゴリ一覧View
class CategoryListView(ListView):
    # 公開済みのカテゴリの集計
    queryset = Category.objects.annotate(
        num_posts=Count('post', filter=Q(post__is_public=True)))


# タグ一覧View
class TagListView(ListView):
    # 公開済みのタグの集計
    queryset = Tag.objects.annotate(num_posts=Count(
        'post', filter=Q(post__is_public=True)))


# 特定のカテゴリにおける投稿一覧
class CategoryPostView(ListView):
    # Postモデルを表示する
    model = Post
    # テンプレート名
    template_name = 'blog/category_post.html'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        self.category = get_object_or_404(Category, slug=category_slug)
        qs = super().get_queryset().filter(category=self.category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


# 特定のタグにおける投稿一覧
class TagPostView(ListView):
    # Postモデルを表示
    model = Post
    # テンプレート名
    template_name = 'blog/tag_post.html'

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug']
        self.tag = get_object_or_404(Tag, slug=tag_slug)
        qs = super().get_queryset().filter(tags=self.tag)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


# 検索機能
class SearchPostView(ListView):
    model = Post
    template_name = 'blog/search_post.html'
    paginate_by = 3

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        lookups = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        )
        if query is not None:
            qs = super().get_queryset().filter(lookups).distinct()
            return qs
        qs = super().get_queryset()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        return context


def like(request,pk):
    try:
        article = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        raise Http404
    article.like += 1
    article.save()
    return redirect('blog:post_detail', pk)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:index')
    else:
        form = SignUpForm()

    context = {'form':form}
    return render(request, 'blog/signup.html', context)


class Create(CreateView):
    model = Post
    fields = ["title", "singer", "category", "tags", "description", "url", "image", "is_public"]


class ContactFormView(FormView):
    template_name = 'blog/contact_form.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact_result')

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)


class ContactResultView(TemplateView):
    template_name = 'blog/contact_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success'] = "お問い合わせは正常に送信されました。"
        return context


class CommentFormView(CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        post_pk = self.kwargs['pk']
        comment.post = get_object_or_404(Post, pk=post_pk)
        comment.save()
        return redirect('blog:post_detail', pk=post_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_pk = self.kwargs['pk']
        context['post'] = get_object_or_404(Post, pk=post_pk)
        return context


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('blog:post_detail', pk=comment.post.pk)
 
 
@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('blog:post_detail', pk=comment.post.pk)


class ReplyFormView(CreateView):
    model = Reply
    form_class = ReplyForm

    def form_valid(self, form):
        reply = form.save(commit=False)
        comment_pk = self.kwargs['pk']
        reply.comment = get_object_or_404(Comment, pk=comment_pk)
        reply.save()
        return redirect('blog:post_detail', pk=reply.comment.post.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_pk = self.kwargs['pk']
        context['comment'] = get_object_or_404(Comment, pk=comment_pk)
        return context


@login_required
def reply_approve(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    reply.approve()
    return redirect('blog:post_detail', pk=reply.comment.post.pk)


@login_required
def reply_remove(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    reply.delete()
    return redirect('blog:post_detail', pk=reply.comment.post.pk)