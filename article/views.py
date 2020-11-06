from django.shortcuts import render,redirect
from django.contrib.auth.models import User
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from .models import ArticlePost
import markdown
from .forms import ArticlePostForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment


def article_list(request):
    search =request.GET.get('search')
    order = request.GET.get('order')
    #用户搜索逻辑
    if search:
        if order == 'total_views':
            # 用 Q对象 进行联合搜索
            article_list = ArticlePost.objects.filter(
            Q(title__icontains=search) | Q(body__icontains=search)
        ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(Q(title__icontains=search) | Q(body__icontains=search))
    else:
        #将search 参数重置为空
        search = ''
        if order == "total_views":
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()

    paginator = Paginator(article_list,9)
    page = request.GET.get("page")
    articles = paginator.get_page(page)
    context = {'articles':articles,'order':order,'search':search}
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
    article.body = md.convert(article.body)
    context = {'article': article, 'toc': md.toc,'comments':comments}
    return render(request,'article/detail.html',context)


#写文章的视图
@login_required(login_url='/userprofile/login/')
def article_create(request):

    if request.method == "POST":
        #将提交的数据赋予到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            new_article.save()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单数据有误，请重新输入")
    else:
        article_post_form = ArticlePostForm()
        context = { 'article_post_form':article_post_form}
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
            article.title = request.POST["title"]
            article.body = request.POST["body"]
            article.save()
            return redirect("article:article_detail",id=id)
        else:
            return HttpResponse("表单数据有误")
    else:
        article_post_form = ArticlePostForm()
        context = {'article':article,'article_post_form':article_post_form}
        return render(request,'article/update.html',context)
