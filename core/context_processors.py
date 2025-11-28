from .models import Restaurant


def restaurant_info(request):
    """Добавляет информацию о ресторане в контекст всех шаблонов"""
    try:
        restaurant = Restaurant.objects.first()
        return {
            'restaurant': restaurant
        }
    except:
        return {
            'restaurant': None
        }
