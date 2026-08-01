from django.shortcuts import render,redirect

# Create your views here.
def checkout(request):
    if request.method=="POST":
        return redirect('waiting')
    else:
        return render(request,'checkout.html')

def waiting(request):
    return render(request,'waiting.html')