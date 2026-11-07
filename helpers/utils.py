
from rest_framework.response import Response
from django.core.paginator import Paginator


def paginate_data(data, page=1, page_size=10, max_page_size=10):
    page_size = min(max(int(page_size), 1), max_page_size)

    paginator = Paginator(data, page_size)
    paginated_data = paginator.get_page(page)
    
    return Response({
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": paginated_data.number,
        "data": paginated_data.object_list,
    })