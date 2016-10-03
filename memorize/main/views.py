from django.shortcuts import render,  get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Article
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context
from .forms import ContactForm

#def index(request):
   # return render(request, 'main/index.html') 

def article_list(request):
    articles = Article.objects.filter(published_date__lte=timezone.now()).order_by('published_date') 
    return render(request, 'main/article_list.html', {'articles' : articles})

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'main/article_detail.html', {'article': article})
def contact(request):
    form_class = ContactForm

    # new logic!
    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            contact_name = request.POST.get(
                'contact_name'
            , '')
            contact_email = request.POST.get(
                'contact_email'
            , '')
            form_content = request.POST.get('content', '')

            # Email the profile with the 
            # contact information
            template = get_template('contact_template.txt')
            context = Context({
                'contact_name': contact_name,
                'contact_email': contact_email,
                'form_content': form_content,
            })
            content = template.render(context)

            email = EmailMessage(
                "New contact form submission",
                content,
                "Your website" +'',
                ['youremail@gmail.com'],
                headers = {'Reply-To': contact_email }
            )
            email.send()
            return redirect('contact')

    return render(request, 'main/contact.html', {
        'form': form_class,
    })


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/main/')
