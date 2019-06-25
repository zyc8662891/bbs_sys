from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
用户表：User
username：账号
password：密码
data_joined：注册时间
email: 邮箱
avatar：图像
telephone：电话
blog：博客站点(一对一)
    """
    # 给该字段一个文件对象，该字段会将文件本体存放在upload_to指定的文件夹下，字段内存放文件路径
    avatar = models.FileField(upload_to='avatar', default='static/img/user.png')
    telephone = models.CharField(max_length=11)
    blog = models.OneToOneField(to='Blog', null=True, on_delete=models.SET_NULL, db_constraint=False, blank=True)
    def __str__(self):
        return self.username
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

class Blog(models.Model):
    """
博客站点表：Blog
site: 站点域名
name：站点名
title：标题
theme：站点主体样式
category：拥有的分类(多对多)
tag: 拥有的标签(多对多)
    """
    site = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=64)
    theme = models.CharField(max_length=32)
    category = models.ManyToManyField(to='Category', db_constraint=False)
    tag = models.ManyToManyField(to='Tag', db_constraint=False)

    def __str__(self):
        return self.site
    class Meta:
        verbose_name = "站点"
        verbose_name_plural = verbose_name


class Category(models.Model):
    """
分类表：Category
name：分类名
    """
    name = models.CharField(max_length=16, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "分组"
        verbose_name_plural = verbose_name


class Tag(models.Model):
    """
标签表：Tag
name：标签名
    """
    name = models.CharField(max_length=16, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name


# 接口：该表需要重构
class Article(models.Model):
    """
文章表：Article
title：文章标题
desc：文章摘要
content：文章内容
create_time：发布事件
blog：所属博客站点(一对多)
category：所属分类(一对多)
tag：拥有的标签(多对多)
"""
    title = models.CharField(max_length=32)
    desc = models.CharField(max_length=256)
    # content = models.TextField()
    create_time = models.DateField(auto_now_add=True)
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.SET_NULL, db_constraint=False)
    # category = models.ForeignKey(to='Category', null=True, on_delete=models.SET_NULL, db_constraint=False)
    # tag = models.ManyToManyField(to='Tag', db_constraint=False)
    article_detail = models.OneToOneField(to='ArticleDetail', null=True, on_delete=models.SET_NULL, db_constraint=False, blank=True)

    # 该文章的具体点赞点踩量，一定要通过代码逻辑保证与UpOrDown表中数据一致
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    # 评论数
    comment_count = models.IntegerField(default=0)


    def __str__(self):
        return self.title
    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name

# 文章详情
class ArticleDetail(models.Model):
    content = models.TextField()
    category = models.ForeignKey(to='Category', null=True, on_delete=models.SET_NULL, db_constraint=False)
    tag = models.ManyToManyField(to='Tag', db_constraint=False)

    def __str__(self):
        return str(self.id)
    class Meta:
        verbose_name = "文章详情"
        verbose_name_plural = verbose_name

class UpOrDown(models.Model):
    """
点赞点踩表：UpOrDown  # user与article的点踩关系表
user：点赞点踩用户(一对多)
article：点赞点踩文章(一对多)
is_up：点赞或点踩
    """
    user = models.ForeignKey(to='User', null=True, on_delete=models.SET_NULL, db_constraint=False)
    article = models.ForeignKey(to='Article', null=True, on_delete=models.SET_NULL, db_constraint=False)
    is_up = models.BooleanField()

    def __str__(self):
        return self.user.username + " | " + self.article.title + ">>>" + str(self.is_up)
    # 实际开发这种表存在大量的修改操作，不建议建立索引（索引服务于查询的）
    class Meta:
        unique_together = ('user', 'article')
        verbose_name = "赞踩"
        verbose_name_plural = verbose_name






class Comment(models.Model):
    """
评论表：Comment  # user与article的评论关系表
user：点赞点踩用户(一对多)
article：点赞点踩文章(一对多)
content：评论内容
parent：父评论(自关联, 一对多)
    """
    user = models.ForeignKey(to='User', null=True, on_delete=models.SET_NULL, db_constraint=False)
    article = models.ForeignKey(to='Article', null=True, on_delete=models.SET_NULL, db_constraint=False)
    content = models.TextField()
    # 评论创建的时间
    create_time = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(to='self', null=True, on_delete=models.SET_NULL, db_constraint=False)


    def __str__(self):
        return str(self.user.id) + "" + str(self.article.id) + "" + str(self.parent)


    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name


