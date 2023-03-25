from django.core.paginator import Paginator
from django.conf import settings


def paginate_posts(posts, page_number):
    paginator = Paginator(posts, settings.POSTS_QUANTITY)
    page_obj = paginator.get_page(page_number)
    return page_obj
