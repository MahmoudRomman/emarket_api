from django.http import JsonResponse



def handle_404(request, exception):
    message = ("Incorrect link")
    response = JsonResponse(data={"Error" : message})
    response.status_code = 404
    return response