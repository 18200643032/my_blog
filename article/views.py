from django.shortcuts import render,redirect
from django.contrib.auth.models import User
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from .models import ArticlePost,ArticleColumn
import markdown
from .forms import ArticlePostForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from comment.forms import CommentForm

#开始使用类视图
from django.views.generic import ListView,DetailView
from django.views.generic.edit import CreateView



def article_list(request):
    search =request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    article_list = ArticlePost.objects.all()
    #用户搜索逻辑
    if search:
        article_list = ArticlePost.objects.filter(
        Q(title__icontains=search) | Q(body__icontains=search)
    )
    else:
        search = ''
    #栏目查询
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)
    #标签查询
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])
    #查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    paginator = Paginator(article_list,3)
    page = request.GET.get("page")
    articles = paginator.get_page(page)
    context = {'articles':articles,'order':order,'search':search,'column':column,'tag':tag}


    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
    print(ip)

    return render(request,'article/list.html',context)

#文章详情
def article_detail(request,id):
    #取出对应的文章
    article = ArticlePost.objects.get(id=id)
    comments = Comment.objects.filter(article=id)
    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
        extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        ]
    )
    commet_form = CommentForm()

    article.body = md.convert(article.body)
    context = {'article': article, 'toc': md.toc,'comments':comments,'commet_form':commet_form}
    return render(request,'article/detail.html',context)


#写文章的视图
@login_required(login_url='/userprofile/login/')
def article_create(request):

    if request.method == "POST":
        #将提交的数据赋予到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            article_post_form.save_m2m()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单数据有误，请重新输入")
    else:
        article_post_form = ArticlePostForm()
        columns  = ArticleColumn.objects.all()
        context = { 'article_post_form':article_post_form,'columns':columns}
        return render(request,'article/create.html',context)


#删除的视图

def article_delete(request,id):
    article = ArticlePost.objects.get(id=id)
    article.delete()
    return redirect("article:article_list")

#安全删除文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request,id):

    if request.method == "POST":
        article = ArticlePost.objects.get(id=id)
        if request.user != article.author:
            return HttpResponse("抱歉，你无权修改这篇文章")
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

@login_required(login_url='/userprofile/login/')
def article_update(request,id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章")
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)

        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None

            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')
            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            return redirect("article:article_detail",id=id)
        else:
            return HttpResponse("表单数据有误")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
            'tags':','.join([x for x in article.tags.names()])
        }

        return render(request,'article/update.html',context)

class ContextMixin:
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = 'total_views'
        return context
class ArticleListView(ContextMixin,ListView):
    #上下文名称
    context_object_name = 'articles'
    #查询集
    #模版位置
    template_name = 'article/list.html'
    def get_queryset(self):
        """查询集"""
        queryset = ArticlePost.objects.filter(title="Python")
        return queryset

#展示文章
class ArticleDetailView(DetailView):
    queryset = ArticlePost.objects.all()
    context_object_name = 'article'
    template_name = 'article/detail.html'
    def get_object(self,**kwargs):
        """获取展示的对象"""
        obj = super(ArticleDetailView,self).get_object()
        obj.total_views += 1
        obj.save(update_field=['total_views'])
        return obj

#新建文章
class ArticleCreateView(CreateView):
    model = ArticlePost
    fields = '__all__'
    template_name = 'article/create_by_class_view.html'

