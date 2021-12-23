from datetime import datetime


def year(request):
    d = datetime.now()
    return {
        'year': d.year
    }
