from django import forms
#from django.forms import ModelForm
from songs.models import Book, Song, Author, Publisher, Chapter, Verse, Ministry
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from captcha.fields import CaptchaField
from registration.forms import RegistrationForm
from songs.functions import test_parsable

# class MultiEmailField(forms.Field):
    # def to_python(self, value):
        # """normalize data to a list of strings"""
        # if not value:
            # return []
        # return value.split(',')
        
    # def validate(self, value):
        # super(MultiEmailField, self).validate(value)
        # for email in value:
            # validate_email(email)

class SelectWithPop(forms.Select):
    def render(self, name, *args, **kwargs):
        html = super(SelectWithPop, self).render(name, *args, **kwargs)
        popupplus = render_to_string("add_widget.html", {'field':name})
        return html+popupplus
        
class MultipleSelectWithPop(forms.SelectMultiple):
    def render(self,name, *args, **kwargs):
        html = super(MultipleSelectWithPop,self).render(name, *args, **kwargs)
        popupplus = render_to_string("add_widget.html", {'field':name, 'multiple':True})
        return html+popupplus

class BasicForm(forms.Form):
    required_css_class = "required"
    #email = forms.EmailField(required=False)
    pass


    
class TagVerseForm(forms.Form):
    songs = forms.ModelMultipleChoiceField(Song.objects)

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    email = forms.EmailField(required=False, label="Your Email Address")
    message = forms.CharField(widget=forms.Textarea)
    # captcha = CaptchaField()
    
    def clean_message(self):
        message = self.cleaned_data['message']
        num_words = len(message.split())
        if num_words <4:
            raise forms.ValidationError("Not enough words!")
        return message

    
def validate_parsable(value):
    if not test_parsable(value):
        raise ValidationError("Oops! We don't understand what you typed or the verses don't exist.")

def validate_too_long(value):
    if len(value) > 50:
        raise ValidationError("Oops! Please keep your search below 50 characters.")
        
class SearchVerseForm(forms.Form):
    query = forms.CharField(validators=[validate_parsable, validate_too_long,])
    
class SearchInfoForm(forms.Form):
    query = forms.CharField(validators=[validate_too_long])        
        
class TrialForm(forms.Form):
    books = forms.ModelChoiceField(Book.objects)
    
class BookForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = Book
        fields = ['name', 'num_chapters', 'order_index']
       
class BookChapterForm(forms.Form):
    required_css_class = "required"
    def __init__(self, *args, **kwargs):
        chap_list = kwargs.pop('chapter_list')
        super(BookChapterForm, self).__init__(*args, **kwargs)
        
        for chapter in chap_list:
            self.fields['Verses in chapter %s' % chapter.number] = forms.IntegerField()
        
        
class SongForm(forms.ModelForm):
    required_css_class = "required"
    authors = forms.ModelMultipleChoiceField(Author.objects, widget=MultipleSelectWithPop)
    publisher = forms.ModelMultipleChoiceField(Publisher.objects, widget=MultipleSelectWithPop)
    #songform doesn't have verses. verses handled separately
    class Meta:
        model = Song
        fields = ['title', 'authors','ccli', 'key_line','original_key', 'recommended_key', 'publisher', 'publication_year']

    
class InviteForm(forms.Form):
    emails = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class':'form-control',
        'placeholder':'Enter emails separated by commas...'}))

    def clean_emails(self):
        emails = self.cleaned_data['emails']
        email_list = emails.split(',')
        invalid_emails = []
        for email in email_list:
            email = email.strip()
            if '@' not in email:
                invalid_emails.append(email)
        if invalid_emails:
            bad_email_string = ', '.join(invalid_emails)
            raise forms.ValidationError("No invitations were sent since the following email(s) are invalid: " + bad_email_string)
        return emails
    
    
class MinistryForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = Ministry
        fields = ['name', 'address', 'city', 'state_province', 'country']
        
class ProfileForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = User
        fields = ['first_name', 'last_name',]
    # def add_ministry(self, code):
        # try:
            # ministry = Ministry.objects.get(id=request.POST.get('ministry_code'))
            # profile.ministries.add(ministry)
        # except:
            # raise forms.ValidationError('Invalid Ministry Code')

class AuthorForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = Author
        fields = ['full_name', 'email']
        
class PublisherForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = Publisher
        fields = ['name', 'address', 'city', 'state_province', 'country', 'website']
        
        
