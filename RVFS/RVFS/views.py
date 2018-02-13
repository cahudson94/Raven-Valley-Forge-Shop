from django.shortcuts import render
from collection.forms import ContactForm

def contact(request):
    form_class = ContactForm
    
    return render(request, 'templates/contact_form/contact_form.html', {
        'form': form_class,
    })