from .models import Board

def boards_context(request):
    return {
        'boards': Board.objects.all()
    }
