from django.shortcuts import render,redirect
from django.contrib import messages
from accounts import views
from .models import Survey_feedback

def survey(request):
    if request.method=="POST":
        source = request.POST['platforms']
        name = request.POST['username']
        purchase = request.POST['purchase']
        favourite_food = request.POST['favourite']
        mail = request.POST['email']
        rating = request.POST['rating']
        feedback = request.POST['feedback']
        obj = Survey_feedback.objects.create(source=source,name=name,purchase=purchase,favourite_food=favourite_food,mail=mail,rating=rating,feed=feedback)
        obj.save()
        messages.info(request, 'Thanks for your feedback!')
        return redirect('home')
    else:
        return render(request,'surveyForm.html')