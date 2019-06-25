from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from appo.models import *
from appo.checks import check_name,CheckForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from PIL import Image,ImageFont,ImageDraw
from io import BytesIO
from bbs_sys import settings
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# 事务:多条sql同时成功或同时失败,原子性(回滚)
from django.db import transaction
from django.db.models import F
import random,datetime,time,os,json
from bs4 import BeautifulSoup
from appo.Myform import UserForm
# Create your views here.
#注册
# 定义接口规范
response_dic = {
    'statue': 2,
    'msg': 'error',
    'data': {}
}
def save_local():
    img = Image.new('RGB', (230, 32), (40, 20, 10))  # type: Image
    # 本地写流
    wf = open('code.png', 'wb')
    # 将数据以指定格式丢给文件操作流
    img.save(wf, 'png')

    with open('code.png', 'rb') as f:
        data = f.read()
    return data

# 随机RGB元组
def random_RGB(min, max):
    return tuple([random.randint(min, max) for i in range(3)])

# 随机产生六位验证码
def random_six_code():
    code = ""
    # 每一位均可以为字母大写、小写或数字
    for i in range(6):
        tag = random.randint(1, 3)  # 1:大写 2:小写 3:数字
        if tag == 1:
            code += chr(random.randint(65, 90))
        elif tag == 2:
            code += chr(random.randint(97, 122))
        else:
            code += str(random.randint(0, 9))
    return code
#获取验证码
def login_code(request):
    img = Image.new('RGB', (230, 32), random_RGB(150, 255))

    # 在画板中画字
    img_draw = ImageDraw.Draw(img)

    # 设置ImageFont字体
    img_font = ImageFont.truetype('static/font/kumo.ttf', size=30)

    # 获取六位验证码
    img_code = random_six_code()
    # 将img_code存储到session中，与会话绑定，用来完成登录验证码的验证
    request.session['img_code'] = img_code

    # 画文字：xy轴、文本、颜色、ImageFont字体
    for i, ch in enumerate(img_code):
        img_draw.text((30 + i * 30, 0), ch, random_RGB(0, 150), img_font)

    bf = BytesIO()
    img.save(bf, 'png')
    data = bf.getvalue()  # 从内存中将数据全部取出
    return HttpResponse(data)


# 注册
def register(request):
    # if request.method == "GET":
    #     return render(request, 'register.html')
    # if request.method == "POST":
    #     # print(request.POST)
    #     # 除了re_password其余都是有用字段
    #     # 数据库插入数据
    #     avatar = request.FILES.get('avatar',None)
    #     print(avatar)
    #
    #     check_form = CheckForm(request.POST)
    #     print(check_form)
    #     print(check_form.is_valid())
    #     print(check_form.cleaned_data)
    #     if check_form.is_valid():
    #         cleaned_form = check_form.cleaned_data
    #         cleaned_form.pop('re_password')
    #         print(cleaned_form)
    #
    #         if avatar:
    #             cleaned_form['avatar'] = avatar
    #         user = User.objects.create_user(**cleaned_form)
    #         if user:
    #             response_dic['statue'] = 1
    #             response_dic['msg'] = 'ok'
    #             response_dic['data'] = {}
    #         else:
    #             response_dic['statue'] = 2
    #             response_dic['msg'] = 'error'
    #             response_dic['data'] = {}
    #         print(response_dic)
    #         return JsonResponse(response_dic)
    #     return JsonResponse(response_dic)
    if request.is_ajax():
        form = UserForm(request.POST)
        username=request.POST.get('username', None)
        response = {'user':None,'msg':None}
        if form.is_valid():
            response['username'] = form.cleaned_data.get('username')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            title = '%s的blog' %username
            category = Category.objects.all()
            print(category)
            tag = Tag.objects.all()
            blog_obj = Blog.objects.create(site=username,title=title,theme=username)
            blog_obj.category.set(category)
            blog_obj.tag.set(tag)
            blog_obj.save()
            extra = {}
            if avatar_obj:
                extra['avatar'] = avatar_obj
                extra['telephone'] = '18855443866'
            user=User.objects.create_user(username=username,password=password,email=email,**extra)
            user.blog = blog_obj
            user.save()

        else:
            response['msg'] = form.errors
        return JsonResponse(response)
    my_form = UserForm
    return render(request,'register.html',{'form':my_form})


# 校验用户名是否重名
def check_username(request):
    if request.is_ajax():
        username = request.GET.get('username', None)
        print(username)
        msg = check_name(username)
        response_dic['msg'] = msg
        print(response_dic)

        return JsonResponse(response_dic)

def my_login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    if request.method == 'POST':
        client_code = request.POST.get('img_code',None).lower()
        server_code = request.session.get('img_code',None).lower()
        client_code = server_code
        print("client_code",client_code)
        print("server_code",server_code)
        if client_code != server_code:
            return JsonResponse({
                'statue':2,
                'msg':'验证码错误',
                'data':{}
            })
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        print(username,password)
        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
            return JsonResponse({
                'status':1,
                'msg':'登录成功',
                'data':{}
            })
        return JsonResponse({
            'status':2,
            'msg':'密码错误',
            'data':{}
        })
def my_paginator(request,article_list):
    paginator = Paginator(article_list,15)
    page = request.GET.get('page',1)
    currentPage = int(page)
    # 如果页数十分时,换另外一种现实方式
    if paginator.num_pages > 11:
        if currentPage - 5 < 1:
            pageRange = range(1,3)
        elif currentPage + 5 > paginator.num_pages:
            pageRange = range(currentPage - 5,paginator.num_pages + 1)
        else:
            pageRange = range(currentPage - 5,currentPage + 5)
    else:
        pageRange = paginator.page_range
    try:
        article_list = paginator.page(page)
    except PageNotAnInteger:
        article_list = paginator.page(1)
    except EmptyPage:
        article_list = paginator.page(paginator.num_pages)
    return pageRange,paginator,article_list


def index(request):
    #用来展示服务器上所有文章
    article_list = Article.objects.order_by('pk').all().reverse()
    top_up = Article.objects.all().order_by('up_count').all().reverse()[0:10]
    pageRange,pagintor,article_list = my_paginator(request,article_list)

    #接口:用分页完成
    return render(request,'index.html',locals())

def my_logout(request):
    logout(request)
    return  redirect('/')
@login_required(login_url='/my_login/')
def update_password(request):
    if request.method == 'GET':
        return render(request,'update_password.html')
    if request.method == 'POST':
        username = request.user.username
        or_password = request.POST.get('or_password',None)
        user = authenticate(username=username, password=or_password)
        new_password = request.POST.get('password',None)
        print(username,or_password,new_password)

        if user: #type:AbstractUser
            user.set_password(new_password)
            user.save()
            return JsonResponse({
                'status': 1,
                'msg': '修改成功',
                'data': {}
            })
        return JsonResponse({
            'status': 2,
            'msg': '原密码不正确,修改失败',
            'data': {}
        })
@login_required(login_url='/my_login/')
def update_avatar(request):
    if request.method == 'GET':
        user = request.user
        print(user)
        return render(request,'update_avatar.html')
    if request.method =='POST':
        avatar = request.FILES.get('avatar',None)
        print(avatar)
        if avatar is None :
            return JsonResponse({
                'status':2,
                'msg':'图片参数获取失败'
            })
        #转bytes类型
        pic = avatar.read()
        #生成 随机文件名字
        now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = "%06d" %random.randint(0,999999)
        name = now_time + random_str
        fname = "{}.png".format(name)

        try:
            with open(os.path.join(settings.MEDIA_ROOT, 'avatar', fname),'wb') as f:
                f.write(pic)
        except Exception as e:
            print(e)
            return JsonResponse({
                'status':2,
                'msg':'保存图片失败',
                'data':{}
            })

        username = request.POST.get('username',None)
        print(username)
        user = User.objects.filter(username=username)
        print(user)
        name=os.path.join(settings.MEDIA_ROOT,'avatar',fname)
        print(name)
        user.update(avatar=name)
        return JsonResponse({
            'status':1,
            'msg':'修改成功',
            'data':{}
        })

def site_page(request,site,group=None,key=None):
    if not site:
        url = redirect('my_login')
        return redirect(url)
    #url匹配的当前站点
    blog = Blog.objects.filter(site=site).first() #type:Blog
    if not blog:
        return HttpResponse('404')
    article_list = Article.objects.filter(blog=blog).all().order_by('-create_time','-pk')
    return render(request, 'site/site_content.html', locals())

def article_page(request,site,aid):
    blog = Blog.objects.filter(site=site).first()
    article = Article.objects.filter(pk=aid).first()
    if not blog or not article: #站点与文章id错误,都是404
        return HttpResponse('404')
    if request.user.is_authenticated:
        is_up = request.user.upordown_set.filter(article=article).values('is_up').first()
        comment_list = Comment.objects.filter(article=article).all()
    return render(request,'site/article.html',locals())



#点赞点踩
def upordown(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status':2,
            'msg':'请先登录',
            'data':{}
        })
    user = request.user
    is_up = request.GET.get('is_up',None)
    is_up = json.loads(is_up) #将前台的true|false转化为后台True|False
    article_id = request.GET.get('article_id',None)

    #操作文章表的up_count|down_count
    #操作upordown表的 user-article-is_up

    #某用户未对文章进行过赞踩操作:点赞就是点赞,点赞就是点踩
    #某用户已对文章进行过赞踩操作:点赞就是赞增踩减,点踩就是踩增赞减

    #获取用户是否赞踩过文章
    res = user.upordown_set.filter(article_id=article_id)
    try:
        with transaction.atomic(): #会捕捉事务中所有sql.一旦异常就会回滚
            if not res:
                if is_up:
                    Article.objects.filter(pk=article_id).update(up_count=F('up_count') + 1)
                else:
                    Article.objects.filter(pk=article_id).update(down_count=F('down_count') +1)
                UpOrDown.objects.create(user=user,article_id=article_id,is_up=is_up)
            else:
                if is_up:
                    Article.objects.filter(pk=article_id).update(up_count=F('up_count') + 1)
                    Article.objects.filter(pk=article_id).update(down_count=F('down_count') - 1)
                else:
                    Article.objects.filter(pk=article_id).update(up_count=F('up_count') - 1)
                    Article.objects.filter(pk=article_id).update(down_count=F('down_count') + 1)
                UpOrDown.objects.filter(user=user,article_id=article_id).update(is_up=is_up)
    except:
        return JsonResponse({
            'status':2,
            'msg':'error',
            'data':{}
        })
    return JsonResponse({
        'status':1,
        'msg':'ok',
        'data':{}
    })

def article_detail(request,username,article_id):
    user = User.objects.filter(username=username).first()
    username = username
    blog = user.blog
    article_obj = Article.objects.filter(pk=article_id).first()
    comment_list = Comment.objects.filter(article_id=article_id)

    return render(request,"article_detail.html",locals())
@login_required(login_url='/my_login/')
def backend(request):
    article_list = Article.objects.all().filter(blog=request.user.blog).order_by('-create_time','-pk')
    return render(request,'backends/backend.html',locals())
@login_required(login_url='/my_login/')
def add_article(request):
    '''
    后台管理的添加书籍视图函数
    :param request:
    :return:
    '''
    # if request.method == 'POST':
    #     title = request.POST.get("title")
    #     content = request.POST.get("content")
    #
    #     #防止xss攻击,过滤script标签
    #     soup = BeautifulSoup(content,'html.parser')
    #     for tag  in soup.find_all():
    #         if tag.name == "script":
    #             tag.decompose()
    #     # 构建摘要数据,获取标签字符串的文本前150个符号
    #     desc = soup.text[0:150] + "..."
    #     Article.objects.create(title=title,desc=desc,user = request.user.blog)
    #     ArticleDetail.objects.create(content=content,ca)
    print(request.user)
    blog = request.user.blog
    print(blog)
    if request.method == 'GET':
            category_list = blog.category.all().order_by('pk')
            tag_list = blog.tag.all().order_by('pk')
            return render(request,'backends/add_article.html',locals())
    if request.method == 'POST':
        print(request.POST)
        title = request.POST.get('title',None)
        content = request.POST.get('content',None)
        category_id = request.POST.get('category_id',None)
        tag_ids = request.POST.getlist('tag_ids',None)

        #利用bs4模块解析html文本
        soup = BeautifulSoup(content,'html.parser')
        desc = soup.text.strip()[0:100] #解析后数据存放在soup.text

        article = Article.objects.create(
            title=title,
            desc=desc,
            blog=blog,
        )
        article_detail = ArticleDetail.objects.create(
            content=content,
            category_id=category_id,
        )
        # 多对多利用第三张表的add方法
        article_detail.tag.add(*tag_ids)
        #建立一对一关系
        article.article_detail = article_detail
        article.save()
        return redirect('/add_article/')
@login_required(login_url='/my_login/')
def edit_article(requeset,article_id):
    '''
    博客文章编辑功能
    :param requeset:
    :param article_id:
    :return: 返回管理界面
    '''
    blog = requeset.user.blog
    category_list = blog.category.all().order_by('pk')
    print(category_list)
    tag_list = blog.tag.all().order_by('pk')
    article_obj = Article.objects.filter(pk=article_id).first()
    article_detail_obj = ArticleDetail.objects.filter(article=article_obj).first()

    print(type(article_obj))
    if requeset.method == "POST":
        title = requeset.POST.get("title")
        content = requeset.POST.get("content")

        #防止xss攻击,过滤script标签
        soup = BeautifulSoup(content,"html.parser")
        for tag in soup.find_all():
            if tag.name == "script":
                tag.decompose()
        # 构建摘要数据,获取标签字符串的文本前150个符号
        desc = soup.text[0:150] + "..."
        Article.objects.filter(pk=article_id).update(title=title,desc=desc)
        ArticleDetail.objects.filter(pk=article_id).update(content=str(soup))
        return redirect("/backend/")
    return render(requeset,'backends/edit.html',locals())











