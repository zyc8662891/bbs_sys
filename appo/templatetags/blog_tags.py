from django.template import Library
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = Library()
@register.inclusion_tag('site/menu_list.html',name='menu_list_tag')

def menu_list(blog):
    #该站点下的分组与该分组下的文章数
    #[(py,2),(h5,1),(java,1)]
    category_set = blog.category.all().filter(articledetail__article__blog=blog) \
       .values('name').annotate(c=Count('articledetail')).values_list('name','c')
    print(category_set)
    #标签
    tag_list = blog.tag.all() \
       .filter(articledetail__article__blog=blog) \
       .values('name').annotate(c=Count('articledetail'))
    print(tag_list)
    #档案
    time_list = blog.article_set.all() \
        .annotate(month=TruncMonth('create_time')) \
        .values('month').annotate(c=Count('pk')).order_by('-month')
    print(time_list)
    return {
        'category_set':category_set,
        'tag_list':tag_list,
        'time_list':time_list
    }











